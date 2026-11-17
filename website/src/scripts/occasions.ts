import { occasions } from '../generated/occasions-data';
import { currentMessages } from '../i18n/messages';
import { completed, frameAt } from './animation-timing';
import { say } from './speech';

const c = currentMessages();
const canvas = document.querySelector<HTMLCanvasElement>('#occasion-preview')!;
const ctx = canvas.getContext('2d');
const buttons = [...document.querySelectorAll<HTMLButtonElement>('[data-occasion]')];
const hit = document.querySelector<HTMLButtonElement>('#occasion-hit')!;
const label = document.querySelector<HTMLElement>('#occasion-state')!;
import { reduced, motionEnabled } from './preferences';
const atlas = new Image();
let ready = false;
let selected = 0;
let elapsed = 0;
let playing = false;
let lastTick = 0;
let raf: number | null = null;

function render(): void {
  if (!ready || !ctx) return;
  const state = occasions.states[selected];
  const frame = reduced.matches ? state.staticFrame : frameAt(state.durations, elapsed, false);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(atlas, frame*occasions.cellWidth, state.row*occasions.cellHeight,
    occasions.cellWidth, occasions.cellHeight, 0, 0, canvas.width, canvas.height);
  canvas.dataset.state = state.id;
  canvas.dataset.frame = String(frame);
  label.textContent = c.occasionStates[selected] + (!motionEnabled() ? ` · ${reduced.matches ? c.staticPose : c.paused}` : '');
}

function tick(now: number): void {
  if (lastTick) elapsed += Math.min(50, Math.max(0, now-lastTick));
  lastTick = now;
  render();
  if (completed(occasions.states[selected].durations, elapsed)) playing = false;
  raf = playing ? requestAnimationFrame(tick) : null;
}

function restart(): void {
  if (raf !== null) cancelAnimationFrame(raf);
  raf = null;
  lastTick = 0;
  render();
  if (ready && playing && motionEnabled() && !document.hidden) raf = requestAnimationFrame(tick);
}

function play(index: number): void {
  selected = index;
  elapsed = 0;
  playing = true;
  buttons.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.occasion) === selected)));
  say(selected === 0 ? 'celebrate' : 'heart', 'occasion');
  restart();
}

function resize(): void {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = occasions.cellWidth*dpr;
  canvas.height = occasions.cellHeight*dpr;
  render();
}

buttons.forEach(button => button.addEventListener('click', () => play(Number(button.dataset.occasion))));
hit.addEventListener('click', () => play(selected));
window.addEventListener('resize', resize);
document.addEventListener('visibilitychange', restart);
document.addEventListener('nery:preferences', restart);
atlas.addEventListener('load', () => {
  if (atlas.naturalWidth !== occasions.cellWidth*occasions.columns || atlas.naturalHeight !== occasions.cellHeight*occasions.states.length) {
    fail();
    return;
  }
  ready = true;
  [...buttons, hit].forEach(button => { button.disabled = false; });
  resize();
  restart();
});
function fail(): void {
  ready = false;
  playing = false;
  restart();
  label.textContent = c.loadError;
  [...buttons, hit].forEach(button => { button.disabled = true; });
}
atlas.addEventListener('error', fail);
const loader = new IntersectionObserver(entries => {
  if (entries.some(entry => entry.isIntersecting)) {
    atlas.src = canvas.dataset.atlas!;
    loader.disconnect();
  }
}, { rootMargin: '500px' });
loader.observe(canvas);
