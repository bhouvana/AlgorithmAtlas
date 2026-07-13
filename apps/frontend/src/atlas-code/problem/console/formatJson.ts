// JSON.stringify(v, null, 2) puts every array element on its own line, which
// turns something as simple as `nums: [1, 3, 4, 2, 2]` into six lines. Keep
// arrays of primitives inline; only break onto multiple lines for arrays of
// objects/arrays or for object keys, where vertical layout actually helps.
export function formatCompactJson(value: unknown, indent = 0): string {
  const pad = '  '.repeat(indent);
  const childPad = '  '.repeat(indent + 1);

  if (Array.isArray(value)) {
    if (value.length === 0) return '[]';
    const isPrimitive = value.every((v) => v === null || typeof v !== 'object');
    if (isPrimitive) {
      return `[${value.map((v) => JSON.stringify(v)).join(', ')}]`;
    }
    const items = value.map((v) => `${childPad}${formatCompactJson(v, indent + 1)}`).join(',\n');
    return `[\n${items}\n${pad}]`;
  }

  if (value !== null && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) return '{}';
    const lines = entries
      .map(([k, v]) => `${childPad}${JSON.stringify(k)}: ${formatCompactJson(v, indent + 1)}`)
      .join(',\n');
    return `{\n${lines}\n${pad}}`;
  }

  return JSON.stringify(value);
}
