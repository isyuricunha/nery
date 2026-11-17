import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const css = await readFile(new URL('../src/styles/site.css', import.meta.url), 'utf8');
const palette = Object.fromEntries([...css.matchAll(/--([\w-]+):\s*(#\w{6})/g)].map(match => [match[1],match[2]]));
function luminance(hex) {
  const [r,g,b] = hex.slice(1).match(/../g).map(pair => {
    const channel = parseInt(pair,16)/255;
    return channel <= 0.04045 ? channel/12.92 : ((channel+0.055)/1.055)**2.4;
  });
  return 0.2126*r+0.7152*g+0.0722*b;
}
function ratio(a,b) {
  const x=luminance(a), y=luminance(b);
  return (Math.max(x,y)+0.05)/(Math.min(x,y)+0.05);
}
test('all text tokens pass AA on the darkest and lightest text surfaces', () => {
  for (const foreground of ['text','muted','accent','gold']) {
    for (const background of ['bg','surface','surface-raised']) {
      assert.ok(ratio(palette[foreground],palette[background])>=4.5,`${foreground} on ${background}`);
    }
  }
  assert.ok(ratio('#24150e',palette.accent)>=4.5,'Primary button text');
  assert.ok(ratio(palette.gold,'#30251e')>=4.5,'Speech and gradient-stage text');
});
test('control boundaries and keyboard focus have sufficient non-text contrast', () => {
  for (const background of ['bg','surface','surface-raised']) {
    assert.ok(ratio(palette.control,palette[background])>=3,`Control boundary on ${background}`);
    assert.ok(ratio(palette.focus,palette[background])>=3,`Focus ring on ${background}`);
  }
});
