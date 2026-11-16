/** Select drawn cels by their exposure time. Never blend neighboring poses. */
export function frameAt(durations: readonly number[], elapsed: number, loop: boolean): number {
  const total = durationOf(durations);
  let time = loop ? Math.max(0, elapsed) % total : Math.min(Math.max(0, elapsed), total - 0.001);
  for (let index = 0; index < durations.length; index++) {
    if (time < durations[index]) return index;
    time -= durations[index];
  }
  return durations.length - 1;
}

export function durationOf(durations: readonly number[]): number {
  return durations.reduce((sum, value) => sum + value, 0);
}

/** Return a full one-shot action to rest only after its last cel was exposed. */
export function completed(durations: readonly number[], elapsed: number): boolean {
  return elapsed >= durationOf(durations);
}
