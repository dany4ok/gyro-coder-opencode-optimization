import { spawnSync } from 'node:child_process'
import { join } from 'node:path'

export default {
  id: 'benchmark.exclusive-edit',
  async setup(ctx) {
    const root = ctx.location.directory
    await ctx.tool.transform((editor) => {
      editor.remove('edit')
      editor.add({
        name: 'safe_python_edit',
        description: 'Edit txreconcile.py only. Replace one exact unique oldString with newString; syntax is checked under an exclusive file handle before writing.',
        input: { type: 'object', properties: { oldString: { type: 'string' }, newString: { type: 'string' } }, required: ['oldString', 'newString'], additionalProperties: false },
        async execute(input) {
          const result = spawnSync('C:\\Python315\\python.exe', [join(root, 'safe_edit.py')], { cwd: root, input: JSON.stringify(input), encoding: 'utf8', timeout: 10000 })
          if (result.error || result.status !== 0) throw new Error('Edit rejected: ' + (result.stdout || result.stderr || String(result.error)))
          return { content: result.stdout }
        },
      })
    })
  },
}
