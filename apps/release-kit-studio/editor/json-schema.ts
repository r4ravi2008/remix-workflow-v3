import { Schema } from 'effect'

const strictObjects = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(strictObjects)
  if (typeof value !== 'object' || value === null) return value
  const mapped = Object.fromEntries(
    Object.entries(value).map(([key, part]) => [key, strictObjects(part)]),
  )
  return 'properties' in mapped
    ? { ...mapped, additionalProperties: false }
    : mapped
}
export const jsonSchema = (schema: Schema.Constraint) => {
  const document = Schema.toJsonSchemaDocument(schema)
  return strictObjects({
    $schema: 'https://json-schema.org/draft/2020-12/schema',
    ...document.schema,
    $defs: document.definitions,
  })
}
