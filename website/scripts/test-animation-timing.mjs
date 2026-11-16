import assert from 'node:assert/strict';
import test from 'node:test';
import { frameAt, durationOf, completed } from '../src/scripts/animation-timing.ts';

test('last cel keeps its full exposure before one-shot completion', () => {
  const times = [100, 80, 180];
  assert.equal(durationOf(times), 360);
  assert.equal(frameAt(times, 180, false), 2);
  assert.equal(frameAt(times, 359.99, false), 2);
  assert.equal(completed(times, 359.99), false);
  assert.equal(completed(times, 360), true);
  assert.equal(frameAt(times, 15000, false), 2);
});

test('loop wraps without holding an extra duplicate endpoint', () => {
  const times = [60, 60, 60, 60];
  assert.equal(frameAt(times, 239.99, true), 3);
  assert.equal(frameAt(times, 240, true), 0);
  assert.equal(frameAt(times, 300, true), 1);
});

test('replaying an action restarts exactly at its first drawing', () => {
  assert.equal(frameAt([100, 80, 180], 0, false), 0);
  assert.equal(frameAt([100, 80, 180], -10, false), 0);
});
