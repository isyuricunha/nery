import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const en = JSON.parse(await readFile(new URL('../src/i18n/en.json', import.meta.url)));
const pt = JSON.parse(await readFile(new URL('../src/i18n/pt-br.json', import.meta.url)));
function shape(value) {
  if (Array.isArray(value)) return value.map(shape);
  if (typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, shape(value[key])]));
  assert.equal(typeof value, 'string');
  assert.ok(value.trim(), 'Translations must not be blank');
  return 'string';
}
test('English and PT-BR cover the same text, controls, states and speech topics', () => {
  assert.deepEqual(shape(en), shape(pt));
  assert.equal(en.states.length, 9);
  assert.equal(pt.states.length, 9);
});
test('runtime and page copy keep Nery tied to Yuri', () => {
  assert.match(en.description, /Yuri Cunha’s personal mascot/);
  assert.match(pt.description, /mascote pessoal de Yuri Cunha/);
  assert.match(en.speech.hello[0], /Yuri/);
  assert.match(pt.speech.hello[0], /Yuri/);
});
