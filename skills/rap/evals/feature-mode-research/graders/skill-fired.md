---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?rap"'
min: 1
---
TRIGGER RELIABILITY. This case invokes the skill by the bare word "rap", not the `/rap`
slash form, so the model has to decide to fire it from the description alone. A small,
obviously-doable brief tempts the model to skip planning and just write the code — which is
exactly the regression this grader is here to catch.
