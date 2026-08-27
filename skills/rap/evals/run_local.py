#!/usr/bin/env python3
"""
Local eval runner for the rap skill.

Runs the same evals/<case>/prompt.md + graders/*.md suite that `claude plugin eval`
consumes, using headless `claude -p` runs. Exists because `claude plugin eval` is
still early-access-gated; when your account is enabled, prefer:

    claude plugin eval . --allow-tools Bash Write Edit WebFetch WebSearch

This runner implements the deterministic graders (tool_used, tool_order, file_exists,
regex) plus an LLM judge, and an ablation arm so you can see whether the skill actually
beats no-skill on the same prompt.

    python3 evals/run_local.py                 # all cases, both arms
    python3 evals/run_local.py --case quick-*  # filter
    python3 evals/run_local.py --runs 1 --no-ablation
"""
import argparse, fnmatch, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pip install pyyaml")

EVALS = Path(__file__).resolve().parent
SKILL = EVALS.parent                      # skills/rap
SKILL_NAME = SKILL.name

FM = re.compile(r'^---\n(.*?)\n---\n(.*)$', re.S)


def parse_md(path):
    m = FM.match(path.read_text())
    if not m:
        return {}, path.read_text()
    return yaml.safe_load(m.group(1)) or {}, m.group(2).strip()


# ---------------------------------------------------------------- running

def run_case(case_dir, meta, prompt, arm, model, workspace):
    """One headless run. Returns (trace, last_message, created_files, cost, error)."""
    workspace.mkdir(parents=True, exist_ok=True)

    scaffold = case_dir / "scaffold.sh"
    if scaffold.exists():
        subprocess.run(["bash", str(scaffold)], cwd=workspace, check=True,
                       stdout=subprocess.DEVNULL)

    if arm == "with":
        dest = workspace / ".claude" / "skills" / SKILL_NAME
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL, dest, ignore=shutil.ignore_patterns("evals", ".DS_Store"))

    before = {p for p in workspace.rglob("*") if p.is_file()}

    tools = meta.get("allowed_tools") or ["Read", "Glob", "Grep", "Bash", "Write",
                                          "Edit", "Agent", "WebSearch", "WebFetch",
                                          "Skill", "TodoWrite"]
    cmd = ["claude", "-p", prompt,
           "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits",
           "--model", model,
           "--allowedTools", *tools]
    if arm == "without":
        # Baseline = same prompt, no skill machinery at all.
        cmd += ["--disallowedTools", "Skill"]

    try:
        proc = subprocess.run(cmd, cwd=workspace, capture_output=True, text=True,
                              timeout=meta.get("timeout_seconds", 900))
    except subprocess.TimeoutExpired:
        return [], "", [], 0.0, "timeout"

    trace, last, cost = [], "", 0.0
    for line in proc.stdout.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "assistant":
            for b in d["message"].get("content", []):
                if b.get("type") == "tool_use":
                    trace.append({"name": b["name"], "input": b.get("input", {})})
                elif b.get("type") == "text":
                    last += b["text"]
        elif d.get("type") == "result":
            cost = d.get("total_cost_usd", 0.0) or 0.0
            if d.get("is_error"):
                return trace, last, [], cost, d.get("stop_reason") or "error"

    created = sorted(str(p.relative_to(workspace))
                     for p in workspace.rglob("*")
                     if p.is_file() and p not in before and ".claude/skills" not in str(p))
    return trace, last, created, cost, None


# ---------------------------------------------------------------- graders

def read_source(spec, run, workspace):
    """Resolve a grader's source into text."""
    if spec in (None, "last_message"):
        return run["last"]
    if spec == "trace":
        return "\n".join(json.dumps(t) for t in run["trace"])
    if spec == "files":
        return "\n".join(run["created"])
    if isinstance(spec, dict) and spec.get("source") == "file":
        hits = sorted(workspace.glob(spec["path"]))
        return "\n\n".join(h.read_text(errors="replace") for h in hits) if hits else ""
    return run["last"]


def judge(criteria, content, judge_model, votes):
    """LLM-as-judge. Returns (passed, reason)."""
    prompt = (
        "You are grading one run of an AI agent against a rubric. Be strict and "
        "literal: judge only what the rubric asks.\n\n"
        f"=== RUBRIC ===\n{criteria}\n\n"
        f"=== CONTENT UNDER TEST ===\n{content[:60000]}\n\n"
        'Reply with ONLY a JSON object, no prose, no code fence: '
        '{"pass": true|false, "reason": "<one sentence>"}'
    )
    results = []
    for _ in range(votes):
        p = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "json",
             "--model", judge_model, "--permission-mode", "acceptEdits",
             "--disallowedTools", "Bash", "Write", "Edit", "Read", "Skill"],
            capture_output=True, text=True, timeout=300)
        try:
            raw = json.loads(p.stdout)
            # --output-format json returns a list of messages; the result is last.
            txt = (raw[-1] if isinstance(raw, list) else raw)["result"]
            m = re.search(r'\{.*\}', txt, re.S)
            v = json.loads(m.group(0))
            results.append((bool(v.get("pass")), v.get("reason", "")))
        except Exception as e:
            results.append((False, f"judge parse failure: {e}"))
    passed = sum(1 for r, _ in results if r) > len(results) / 2
    return passed, results[0][1]


def grade(g, body, run, workspace, judge_model, votes):
    """Returns (passed, detail)."""
    t = g.get("type")

    if t == "tool_used":
        calls = [c for c in run["trace"] if c["name"] == g["tool"]]
        if g.get("input_match"):
            rx = re.compile(g["input_match"])
            calls = [c for c in calls if rx.search(json.dumps(c["input"]))]
        n = len(calls)
        lo, hi = g.get("min", 1), g.get("max")
        ok = n >= lo and (hi is None or n <= hi)
        return ok, f"{g['tool']} called {n}x (min={lo}, max={hi})"

    if t == "tool_order":
        names = [c["name"] for c in run["trace"]]
        try:
            ok = names.index(g["before"]) < names.index(g["after"])
        except ValueError:
            return False, f"missing {g['before']} or {g['after']}"
        return ok, f"{g['before']} before {g['after']}"

    if t == "file_exists":
        hits = [f for f in run["created"] if fnmatch.fnmatch(f, g["path"])]
        return bool(hits), f"matched {hits[:3] or 'nothing'} for {g['path']}"

    if t == "regex":
        text = read_source(g.get("source") or g.get("target"), run, workspace)
        flags = re.I if "i" in str(g.get("flags", "")) else 0
        found = re.findall(g["pattern"], text, flags)
        mode = g.get("match", "contains")
        if mode == "not_contains":
            return not found, f"{len(found)} match(es), wanted none" + (
                f" — first: {found[0]!r}" if found else "")
        if mode.startswith("count:"):
            want = int(mode.split(":")[1])
            return len(found) == want, f"{len(found)} match(es), wanted {want}"
        return bool(found), f"{len(found)} match(es)"

    if t == "llm":
        content = read_source(g.get("source"), run, workspace)
        if not content.strip():
            return False, "nothing to judge (empty source)"
        return judge(g.get("criteria") or body, content, judge_model, votes)

    return False, f"unknown grader type {t!r}"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default="*")
    ap.add_argument("--runs", type=int)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--judge-model", default="haiku")
    ap.add_argument("--judge-votes", type=int, default=1)
    ap.add_argument("--no-ablation", action="store_true")
    ap.add_argument("--keep-temp", action="store_true")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)  # stream progress when piped

    if (Path.home() / ".claude" / "skills" / SKILL_NAME).exists():
        print(f"note: ~/.claude/skills/{SKILL_NAME} also exists; the copy under test is the "
              f"repo one, but keep them in sync to avoid confusion.\n", file=sys.stderr)

    cases = sorted(d for d in EVALS.iterdir()
                   if d.is_dir() and (d / "prompt.md").exists()
                   and fnmatch.fnmatch(d.name, args.case))
    if not cases:
        sys.exit(f"no cases matching {args.case!r} in {EVALS}")

    arms = ["with"] if args.no_ablation else ["with", "without"]
    report, total_cost = [], 0.0

    for case_dir in cases:
        meta, prompt = parse_md(case_dir / "prompt.md")
        graders = [(p.stem, *parse_md(p)) for p in sorted((case_dir / "graders").glob("*.md"))]
        n_runs = args.runs or meta.get("runs", 3)
        case_rec = {"case": case_dir.name, "arms": {}}
        print(f"\n\033[1m{case_dir.name}\033[0m  ({n_runs} runs × {len(arms)} arm(s))")

        for arm in arms:
            run_scores, indicators = [], []
            for i in range(n_runs):
                tmp = Path(tempfile.mkdtemp(prefix=f"rap-eval-{case_dir.name}-{arm}-"))
                t0 = time.time()
                trace, last, created, cost, err = run_case(
                    case_dir, meta, prompt, arm, args.model, tmp)
                total_cost += cost
                run = {"trace": trace, "last": last, "created": created}

                earned = possible = 0.0
                details = []
                for name, g, body in graders:
                    with_only = g.get("type") == "tool_used" and g.get("tool") == "Skill" \
                                and g.get("arm") != "both"
                    if with_only and arm == "without":
                        continue
                    ok, detail = grade(g, body, run, tmp, args.judge_model, args.judge_votes)
                    w = float(g.get("weight", 1))
                    if with_only:
                        indicators.append(ok)
                        details.append((name, ok, detail, "indicator"))
                        continue
                    possible += w
                    earned += w if ok else 0
                    details.append((name, ok, detail, "scored"))

                score = earned / possible if possible else 0.0
                run_scores.append(score)
                mark = "\033[32m✓\033[0m" if score == 1 else "\033[31m✗\033[0m"
                print(f"  {arm:>7} run {i+1}: {mark} {score:.0%}  "
                      f"({time.time()-t0:.0f}s, ${cost:.2f}"
                      + (f", {err}" if err else "") + ")")
                for name, ok, detail, kind in details:
                    if not ok or kind == "indicator":
                        sym = "·" if kind == "indicator" else " "
                        col = "\033[32m" if ok else "\033[31m"
                        print(f"        {sym} {col}{name}\033[0m — {detail}")
                if not args.keep_temp:
                    shutil.rmtree(tmp, ignore_errors=True)
                else:
                    print(f"        kept: {tmp}")

            mean = sum(run_scores) / len(run_scores)
            case_rec["arms"][arm] = {"mean": mean, "runs": run_scores,
                                     "skill_fired": indicators}
            print(f"  {arm:>7} mean: \033[1m{mean:.0%}\033[0m")

        if len(arms) == 2:
            d = case_rec["arms"]["with"]["mean"] - case_rec["arms"]["without"]["mean"]
            arrow = "▲" if d > 0 else ("▼" if d < 0 else "=")
            col = "\033[32m" if d > 0 else ("\033[31m" if d < 0 else "")
            print(f"  {col}plugin effect: {arrow} {d:+.0%}\033[0m")
            case_rec["delta"] = d
        report.append(case_rec)

    print(f"\n\033[1mtotal cost: ${total_cost:.2f}\033[0m")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(
            {"cases": report, "totalCostUsd": total_cost}, indent=2))
        print(f"wrote {args.json_out}")

    worst = min((c["arms"]["with"]["mean"] for c in report), default=0)
    sys.exit(0 if worst == 1.0 else 1)


if __name__ == "__main__":
    main()
