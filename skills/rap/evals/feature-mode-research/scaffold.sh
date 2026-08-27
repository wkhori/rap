#!/usr/bin/env bash
# Minimal two-subsystem Express app so the case exercises `feature` mode
# (real codebase research) rather than greenfield.
set -e
mkdir -p src/api src/store test
cat > package.json <<'JSON'
{
  "name": "notes-api",
  "version": "0.3.0",
  "type": "module",
  "scripts": { "test": "node --test", "start": "node src/server.js" },
  "dependencies": { "express": "^4.19.2", "better-sqlite3": "^9.4.3" }
}
JSON
cat > src/server.js <<'JS'
import express from 'express'
import { notesRouter } from './api/notes.js'

const app = express()
app.use(express.json())
app.use('/notes', notesRouter)
app.listen(3000)
JS
cat > src/api/notes.js <<'JS'
import { Router } from 'express'
import { allNotes, insertNote, noteById } from '../store/notes.js'

export const notesRouter = Router()

notesRouter.get('/', (req, res) => res.json(allNotes()))
notesRouter.get('/:id', (req, res) => {
  const note = noteById(req.params.id)
  if (!note) return res.status(404).json({ error: 'not found' })
  res.json(note)
})
notesRouter.post('/', (req, res) => {
  const { title, body } = req.body
  if (!title) return res.status(400).json({ error: 'title required' })
  res.status(201).json(insertNote({ title, body: body ?? '' }))
})
JS
cat > src/store/notes.js <<'JS'
import Database from 'better-sqlite3'

const db = new Database(process.env.NOTES_DB ?? 'notes.db')
db.exec(`CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  body TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
)`)

export const allNotes = () => db.prepare('SELECT * FROM notes ORDER BY id DESC').all()
export const noteById = (id) => db.prepare('SELECT * FROM notes WHERE id = ?').get(id)
export const insertNote = ({ title, body }) =>
  noteById(db.prepare('INSERT INTO notes (title, body) VALUES (?, ?)').run(title, body).lastInsertRowid)
JS
cat > test/notes.test.js <<'JS'
import { test } from 'node:test'
import assert from 'node:assert'
import { insertNote, noteById } from '../src/store/notes.js'

test('insertNote round-trips', () => {
  const n = insertNote({ title: 'hello', body: 'world' })
  assert.equal(noteById(n.id).title, 'hello')
})
JS
cat > README.md <<'MD'
# notes-api
Tiny Express + SQLite notes service. `npm test` runs node:test. No auth yet.
MD
