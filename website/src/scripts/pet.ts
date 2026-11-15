// Browser renderer for Nery Mizuki / Petdex v2.
// Nine canonical states live in spritesheet.webp (v2 fixed layout).
// The website uses separately DRAWN 16-frame walks (walk-16.webp) to
// reduce stutter; no crossfaded double-shoes or partial-limb reflections.
import { petAssetVersion, walkAssetVersion } from '../generated/pet-asset-version';

const states = [
  { name: 'Idle',              durations: [280, 110, 110, 140, 140, 320], loop: true },
  { name: 'Walking right',     durations: [120, 120, 120, 120, 120, 120, 120, 220], loop: true },
  { name: 'Walking left',      durations: [120, 120, 120, 120, 120, 120, 120, 220], loop: true },
  { name: 'Waving',            durations: [140, 140, 140, 280], loop: false },
  { name: 'Jumping',           durations: [140, 140, 140, 140, 280], loop: false },
  { name: 'Failed',            durations: [140, 140, 140, 140, 140, 140, 140, 240], loop: false },
  { name: 'Waiting for input', durations: [150, 150, 150, 150, 150, 260], loop: true },
  { name: 'Working',           durations: [120, 120, 120, 120, 120, 220], loop: true },
  { name: 'Reviewing',         durations: [150, 150, 150, 150, 150, 280], loop: true },
] as const;

const W = 192;
const H = 208;
const WALK_FRAMES = 16;
const WALK_CYCLE_MS = 960;
const WALK_DISTANCE_PX = 64;
const WALK_SPEED_PX_S = WALK_DISTANCE_PX * 1000 / WALK_CYCLE_MS;
const STATE_TRANSITION_MS = 120;
const TURN_PAUSE_MS = 180;
const AFTER_IDLE_MS = 8000;

const preview = document.querySelector<HTMLCanvasElement>('#pet-preview')!;
const walker = document.querySelector<HTMLCanvasElement>('#pet-walker')!;
const shell = document.querySelector<HTMLElement>('.walker-shell')!;
const label = document.querySelector<HTMLElement>('#pet-state')!;
const buttons = [...document.querySelectorAll<HTMLButtonElement>('[data-state]')];
const hitTargets = [
  document.querySelector<HTMLButtonElement>('#preview-hit')!,
  document.querySelector<HTMLButtonElement>('#walker-hit')!,
];

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const atlas = new Image();
const walkAtlas = new Image();

type Layer = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  row: number;
  since: number;
  changedAt: number;
  previous: HTMLCanvasElement | null;
};

const layers: Layer[] = [preview, walker].map(canvas => {
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Nery requires a 2D canvas.');
  return { canvas, ctx, row: -1, since: 0, changedAt: 0, previous: null };
});

let loaded = 0;
let ready = false;
let selected = 0;
let selectedSince = performance.now();
let activeWaveUntil = 0;
let x = 24;
let direction = 1;
let velocity = 0;
let walkDistance = 0;
let turnUntil = 0;
let lastActivity = performance.now();
let lastTick = 0;
let rafId: number | null = null;
let lastLabel = '';

const clamp = (v: number, low: number, high: number) => Math.max(low, Math.min(high, v));
const ease = (t: number) => t * t * (3 - 2 * t);
const isWalk = (row: number) => row === 1 || row === 2;
const totalMs = (row: number) => states[row].durations.reduce((sum, value) => sum + value, 0);

function nativeFrame(row: number, elapsed: number): number {
  const { durations, loop } = states[row];
  const total = totalMs(row);
  let t = loop ? elapsed % total : Math.min(elapsed, total - 0.001);
  for (let i = 0; i < durations.length; i++) {
    if (t < durations[i] || i === durations.length - 1) return i;
    t -= durations[i];
  }
  return 0;
}

function drawFrame(layer: Layer, row: number, frame: number, alpha = 1): void {
  const { ctx, canvas } = layer;
  ctx.save();
  ctx.globalAlpha = alpha;
  if (isWalk(row)) {
    // Rows 0-1 face right, rows 2-3 face left. Eight columns each.
    const sourceRow = (row === 1 ? 0 : 2) + Math.floor(frame / 8);
    const sourceCol = frame % 8;
    ctx.drawImage(walkAtlas, sourceCol * W, sourceRow * H, W, H,
      0, 0, canvas.width, canvas.height);
  } else {
    ctx.drawImage(atlas, frame * W, row * H, W, H,
      0, 0, canvas.width, canvas.height);
  }
  ctx.restore();
}

function paint(layer: Layer, row: number, now: number, phase?: number): void {
  const { canvas, ctx } = layer;
  if (layer.row !== row) {
    // A directional turn must never show left and right feet at once.
    const wasWalking = isWalk(layer.row);
    const startsWalking = isWalk(row);
    const mayDissolve = !wasWalking && !startsWalking && !reducedMotion.matches;
    if (layer.row >= 0 && mayDissolve) {
      const snapshot = document.createElement('canvas');
      snapshot.width = canvas.width;
      snapshot.height = canvas.height;
      snapshot.getContext('2d')!.drawImage(canvas, 0, 0);
      layer.previous = snapshot;
    } else {
      layer.previous = null;
    }
    layer.row = row;
    layer.since = now;
    layer.changedAt = now;
  }

  const elapsed = Math.max(0, now - layer.since);
  let frame: number;
  if (reducedMotion.matches) {
    frame = 0;
  } else if (isWalk(row)) {
    // Native Petdex only has 8 walking cells; the website renders 16
    // real source poses, one per 60 ms, with zero crossfade/ghosting.
    const progress = phase ?? ((elapsed % WALK_CYCLE_MS) / WALK_CYCLE_MS);
    frame = Math.floor((progress % 1) * WALK_FRAMES) % WALK_FRAMES;
  } else {
    frame = nativeFrame(row, elapsed);
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const old = layer.previous;
  if (old) {
    const t = ease(clamp((now - layer.changedAt) / STATE_TRANSITION_MS, 0, 1));
    if (t < 1) {
      // Weighted premultiplied-alpha sum: no opacity dip or flickering.
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = 1 - t;
      ctx.drawImage(old, 0, 0);
      ctx.globalAlpha = 1;
      drawFrame(layer, row, frame, t);
      ctx.restore();
    } else {
      layer.previous = null;
      drawFrame(layer, row, frame);
    }
  } else {
    drawFrame(layer, row, frame);
  }
}

function resize(): void {
  [preview, walker].forEach((canvas, index) => {
    const cssWidth = index === 0 ? 192 : 96;
    const scale = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(cssWidth * scale);
    canvas.height = Math.round((cssWidth * H / W) * scale);
  });
  layers.forEach(layer => {
    layer.row = -1;
    layer.previous = null;
  });
  x = clamp(x, 0, Math.max(0, window.innerWidth - 96));
  if (ready) update(performance.now(), false);
}

function update(now: number, advance: boolean): void {
  const dt = lastTick === 0 ? 0 : clamp(now - lastTick, 0, 50);
  lastTick = now;
  const still = now - lastActivity > AFTER_IDLE_MS || reducedMotion.matches;
  const waving = now < activeWaveUntil;
  const turning = now < turnUntil;
  const shouldMove = !still && !waving && !turning;

  if (advance && !reducedMotion.matches) {
    const targetSpeed = shouldMove ? direction * WALK_SPEED_PX_S : 0;
    velocity += (targetSpeed - velocity) * (1 - Math.exp(-dt / 130));
    const before = x;
    const lastX = Math.max(0, window.innerWidth - 96);
    x = clamp(x + velocity * dt / 1000, 0, lastX);
    walkDistance += Math.abs(x - before);
    if (shouldMove && ((x >= lastX && direction > 0) || (x <= 0 && direction < 0))) {
      velocity = 0;
      direction = -direction;
      turnUntil = now + TURN_PAUSE_MS;
      walkDistance = 0;
    }
    if (!shouldMove && Math.abs(velocity) < 1 && !waving) {
      velocity = 0;
    }
  }

  shell.style.transform = `translate3d(${x.toFixed(2)}px,0,0)`;
  // One-shot animation buttons go back to idle on completion.
  if (!waving && (selected === 3 || selected === 4) &&
      now - selectedSince >= totalMs(selected)) {
    selected = 0;
    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(Number(button.dataset.state) === 0));
    });
  }

  const previewRow = waving ? 3 : selected;
  const moving = shouldMove || (!turning && !waving && Math.abs(velocity) > 1);
  const walkerRow = waving ? 3 : moving && !reducedMotion.matches ? (velocity >= 0 ? 1 : 2) : 0;
  paint(layers[0], previewRow, now);
  const travelPhase = (walkDistance % WALK_DISTANCE_PX) / WALK_DISTANCE_PX;
  paint(layers[1], walkerRow, now, isWalk(walkerRow) ? travelPhase : undefined);

  const currentLabel = states[previewRow].name + (reducedMotion.matches ? ' · static pose' : '');
  if (currentLabel !== lastLabel) {
    lastLabel = currentLabel;
    label.textContent = currentLabel;
  }
}

function tick(now: number): void {
  update(now, true);
  rafId = requestAnimationFrame(tick);
}

function restart(): void {
  if (rafId !== null) cancelAnimationFrame(rafId);
  rafId = null;
  if (!ready || document.hidden) return;
  lastTick = performance.now();
  layers.forEach(layer => { if (reducedMotion.matches) layer.previous = null; });
  update(lastTick, false);
  if (!reducedMotion.matches) rafId = requestAnimationFrame(tick);
}

function activity(): void { lastActivity = performance.now(); }
for (const event of ['pointermove', 'pointerdown', 'keydown', 'scroll'] as const) {
  window.addEventListener(event, activity, { passive: true });
}
buttons.forEach(button => button.addEventListener('click', () => {
  selected = Number(button.dataset.state);
  selectedSince = performance.now();
  activeWaveUntil = 0;
  if (layers[0].row === selected) layers[0].since = selectedSince;
  buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  activity();
  if (ready) update(selectedSince, false);
}));

hitTargets.forEach(hit => hit.addEventListener('click', () => {
  activeWaveUntil = performance.now() + totalMs(3);
  activity();
  if (ready) update(performance.now(), false);
  if (reducedMotion.matches) setTimeout(() => {
    if (performance.now() >= activeWaveUntil && ready) update(performance.now(), false);
  }, totalMs(3) + 25);
}));

function onLoaded(): void {
  loaded++;
  if (loaded !== 2) return;
  ready = true;
  resize();
  restart();
}
function onError(): void {
  label.textContent = 'Nery could not load the animation. See her artwork kit above.';
  shell.hidden = true;
}
atlas.addEventListener('load', onLoaded);
walkAtlas.addEventListener('load', onLoaded);
atlas.addEventListener('error', onError);
walkAtlas.addEventListener('error', onError);
atlas.src = `/spritesheet.webp?v=${petAssetVersion}`;
walkAtlas.src = `/walk-16.webp?v=${walkAssetVersion}`;

window.addEventListener('resize', resize);
reducedMotion.addEventListener('change', restart);
document.addEventListener('visibilitychange', restart);
