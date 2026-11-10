import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { appendFileSync, readFileSync } from 'node:fs'
import { isAbsolute, join, relative, resolve } from 'node:path'

export default {
  id: 'benchmark.preedit-syntax',
  async setup(ctx) {
    const root = resolve(ctx.location.directory)
    const log = join(root, 'syntax-hook.jsonl')
    await ctx.tool.hook('execute.before', (event) => {
      if (event.tool !== 'edit') return
      const input = event.input || {}
      if (typeof input.path !== 'string' || !input.path.toLowerCase().endsWith('.py')) return
      const path = resolve(root, input.path)
      const rel = relative(root, path)
      if (rel === '..' || rel.startsWith('..\\') || rel.startsWith('../') || isAbsolute(rel)) return
      if (typeof input.oldString !== 'string' || typeof input.newString !== 'string' || !input.oldString) return
      const original = readFileSync(path, 'utf8')
      const first = original.indexOf(input.oldString)
      if (first < 0 || original.indexOf(input.oldString, first + 1) >= 0) return
      const candidate = original.slice(0, first) + input.newString + original.slice(first + input.oldString.length)
      const check = spawnSync('C:\\Python315\\python.exe', ['-c', 'import ast,sys; ast.parse(sys.stdin.read(),filename=sys.argv[1])', path], { input: candidate, encoding: 'utf8', timeout: 5000 })
      const status = check.error ? 'checker_error' : check.status === 0 ? 'ok' : 'syntax_error'
      const sha256 = (text) => createHash('sha256').update(text, 'utf8').digest('hex')
      appendFileSync(log, JSON.stringify({ tool: event.tool, status, original_sha256: sha256(original), candidate_sha256: sha256(candidate) }) + '\n')
      if (status !== 'ok') throw new Error('Python pre-edit validation rejected the proposed replacement; original file was not changed by this hook. ' + (check.stderr || String(check.error || 'checker failed')).slice(-2000))
    })
  },
}
