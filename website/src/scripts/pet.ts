// One shared cel atlas and timing manifest drive both website companions.
// No opacity dissolves, limb warps or frame interpolation.
import { motion } from '../generated/motion-data';
import { motionAssetVersion } from '../generated/pet-asset-version';
import { completed, durationOf, frameAt } from './animation-timing';

const preview = document.querySelector<HTMLCanvasElement>('#pet-preview')!;
const walker = document.querySelector<HTMLCanvasElement>('#pet-walker')!;
const shell = document.querySelector<HTMLElement>('.walker-shell')!;
const label = document.querySelector<HTMLElement>('#pet-state')!;
const buttons = [...document.querySelectorAll<HTMLButtonElement>('[data-state]')];
const hits = [...document.querySelectorAll<HTMLButtonElement>('#preview-hit, #walker-hit')];
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const atlas = new Image();
const states = motion.states;
const W = motion.cellWidth;
const H = motion.cellHeight;
const WALK_DISTANCE = motion.walkDistance;
const WALK_CYCLE = durationOf(states[1].durations);
const SPEED = WALK_DISTANCE * 1000 / WALK_CYCLE;
const WALKER_WIDTH = 96;
const REST_AFTER = 8000;
const TURN_PAUSE = 200;

const layers = [preview, walker].map(canvas => {
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Nery requires a 2D canvas.');
  return { canvas, ctx, row: -1, frame: -1 };
});

let ready = false;
let raf: number | null = null;
let lastTick = 0;
let clock = 0;
let selected = 0;
let selectedSince = 0;
let waveUntil = 0;
let lastActivity = performance.now();
let x = 24;
let direction = 1;
let velocity = 0;
let distance = 0;
let turningUntil = 0;
let idleSince = 0;
let lastWalkerRow = -1;

function markSelection(): void {
  buttons.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.state) === selected)));
}

function paint(layer: typeof layers[number], row: number, elapsed: number, phase?: number): void {
  const state = states[row];
  const frame = reduced.matches ? state.staticFrame : phase === undefined
    ? frameAt(state.durations, elapsed, state.loop)
    : Math.floor((phase % 1) * state.count) % state.count;
  if (layer.row === row && layer.frame === frame) return;
  layer.ctx.clearRect(0, 0, layer.canvas.width, layer.canvas.height);
  layer.ctx.drawImage(atlas, frame * W, row * H, W, H, 0, 0, layer.canvas.width, layer.canvas.height);
  layer.row = row;
  layer.frame = frame;
  layer.canvas.dataset.state = state.id;
  layer.canvas.dataset.frame = String(frame);
}

function render(dt = 0): void {
  if (!ready) return;
  clock += dt;
  const selectedState = states[selected];
  if (!reduced.matches && selectedState.returnToIdle && completed(selectedState.durations, clock - selectedSince)) {
    selected = 0;
    selectedSince = clock;
    markSelection();
  }
  const waving = clock < waveUntil;
  const turning = clock < turningUntil;
  const resting = performance.now() - lastActivity >= REST_AFTER;
  const move = !reduced.matches && !resting && !waving && !turning;
  const target = move ? direction * SPEED : 0;
  velocity += (target - velocity) * (1 - Math.exp(-dt / 150));
  if (Math.abs(velocity) < 0.15) velocity = 0;
  const limit = Math.max(0, window.innerWidth - WALKER_WIDTH);
  const before = x;
  x = Math.min(limit, Math.max(0, x + velocity * dt / 1000));
  distance += Math.abs(x - before);
  if (move && limit > 0 && ((direction > 0 && x >= limit) || (direction < 0 && x <= 0))) {
    direction *= -1;
    velocity = 0;
    distance = 0;
    turningUntil = clock + TURN_PAUSE;
  }
  // Stop completely for a greeting, never slide a stationary waving pose.
  if (waving || reduced.matches) velocity = 0;
  shell.style.transform = `translate3d(${x.toFixed(3)}px,0,0)`;
  const moving = clock >= turningUntil && !waving && !reduced.matches && Math.abs(velocity) > 0.15;
  const walkerRow = waving ? 3 : moving ? (direction > 0 ? 1 : 2) : 0;
  if (walkerRow !== lastWalkerRow) {
    idleSince = clock;
    lastWalkerRow = walkerRow;
  }
  paint(layers[0], selected, clock - selectedSince);
  paint(layers[1], walkerRow, clock - idleSince, moving ? distance / WALK_DISTANCE : undefined);
  const text = states[selected].label + (reduced.matches ? ' · static pose' : '');
  if (label.textContent !== text) label.textContent = text;
}

function tick(now: number): void {
  const dt = lastTick ? Math.min(50, Math.max(0, now - lastTick)) : 0;
  lastTick = now;
  render(dt);
  raf = requestAnimationFrame(tick);
}

function restart(): void {
  if (raf !== null) cancelAnimationFrame(raf);
  raf = null;
  lastTick = 0;
  if (!ready || document.hidden) return;
  render();
  if (!reduced.matches) raf = requestAnimationFrame(tick);
}

function resize(): void {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  layers.forEach((layer, index) => {
    const width = index === 0 ? W : WALKER_WIDTH;
    layer.canvas.width = Math.round(width * dpr);
    layer.canvas.height = Math.round(width * H / W * dpr);
    layer.row = -1;
  });
  x = Math.min(x, Math.max(0, window.innerWidth - WALKER_WIDTH));
  render();
}

function activity(): void { lastActivity = performance.now(); }
function select(row: number, greet = false): void {
  selected = row;
  selectedSince = clock;
  waveUntil = greet ? clock + durationOf(states[3].durations) : 0;
  if (greet) velocity = 0;
  markSelection();
  activity();
  render();
}
buttons.forEach(button => button.addEventListener('click', () => select(Number(button.dataset.state))));
hits.forEach(hit => hit.addEventListener('click', () => select(3, true)));
for (const event of ['pointermove', 'pointerdown', 'keydown', 'scroll'] as const) {
  window.addEventListener(event, activity, { passive: true });
}
window.addEventListener('resize', resize);
document.addEventListener('visibilitychange', restart);
reduced.addEventListener('change', () => {
  // A change in preferences must immediately remove any existing movement.
  velocity = 0;
  restart();
});
atlas.addEventListener('load', () => {
  if (atlas.naturalWidth !== W * motion.columns || atlas.naturalHeight !== H * states.length) {
    fail();
    return;
  }
  ready = true;
  resize();
  restart();
});
function fail(): void {
  ready = false;
  restart();
  label.textContent = 'Nery could not load the animation. See her artwork kit above.';
  shell.hidden = true;
  [...buttons, ...hits].forEach(button => { button.disabled = true; });
}
atlas.addEventListener('error', fail);
atlas.src = `/motion.webp?v=${motionAssetVersion}`;
