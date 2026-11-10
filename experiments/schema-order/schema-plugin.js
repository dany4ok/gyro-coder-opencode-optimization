import { appendFileSync } from 'node:fs'
import { join } from 'node:path'

export default {
  id: 'benchmark.edit-schema-order',
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.update('edit', (tool) => {
        const input = tool.input
        const props = input?.properties
        const expected = ['newString', 'path', 'oldString']
        if (!props || !expected.every((name) => Object.hasOwn(props, name)) || !expected.every((name) => input.required?.includes(name))) {
          appendFileSync(join(ctx.location.directory, 'schema-plugin.jsonl'), JSON.stringify({applied:false, inputKeys:Object.keys(input || {})}) + '\n')
          return
        }
        const properties = Object.fromEntries([...expected, ...Object.keys(props).filter((name) => !expected.includes(name))].map((name) => [name, props[name]]))
        tool.input = {...input, properties, required:[...expected, ...input.required.filter((name) => !expected.includes(name))]}
        appendFileSync(join(ctx.location.directory, 'schema-plugin.jsonl'), JSON.stringify({applied:true, before:Object.keys(props), after:Object.keys(properties), required:tool.input.required}) + '\n')
      })
    })
  },
}
