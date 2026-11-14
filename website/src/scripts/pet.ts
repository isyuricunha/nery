// Petdex v2: 192 × 208 frames, 8 columns, 11 rows; only 6 frames per active row.
const rows = ['Idle', 'Running right', 'Running left', 'Waving', 'Jumping', 'Failed', 'Waiting', 'Running', 'Review'];
const preview = document.querySelector<HTMLCanvasElement>('#pet-preview')!;
const walker = document.querySelector<HTMLCanvasElement>('#pet-walker')!;
const shell = document.querySelector<HTMLElement>('.walker-shell')!;
const label = document.querySelector<HTMLElement>('#pet-state')!;
const buttons = [...document.querySelectorAll<HTMLButtonElement>('[data-state]')];
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const sheet = new Image();
sheet.src = '/spritesheet.webp';
let ready = false;
let selected = 0;
let x = 24;
let direction = 1;
let lastActivity = performance.now();
let previous = 0;
let frameRequest = 0;
let wavingUntil = 0;
let previewHover = false;
let walkerHover = false;
let lastLabel = '';
const contexts = [preview, walker].map(canvas => canvas.getContext('2d'));
function resize() {
  [preview, walker].forEach((canvas, i) => {
    const width = i === 0 ? 192 : 96;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(width * 208 / 192 * ratio);
  });
  x = Math.max(0, Math.min(x, innerWidth - 96));
  if (ready) render(performance.now(), false);
}
function draw(canvas: HTMLCanvasElement, index: number, row: number, frame: number) {
  const context = contexts[index];
  if (!context) return;
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(sheet, frame * 192, row * 208, 192, 208, 0, 0, canvas.width, canvas.height);
}
function render(now: number, advance: boolean) {
  const elapsed = Math.min((now - previous) / 1000, .05);
  previous = now;
  const quiet = now - lastActivity > 8000;
  const waving = now < wavingUntil;
  const staticPose = reduced.matches;
  const previewRow = waving ? 3 : previewHover ? 8 : selected;
  const walkerRow = waving ? 3 : walkerHover ? 8 : quiet || staticPose ? 0 : direction > 0 ? 1 : 2;
  const frame = staticPose ? 0 : Math.floor((now % 1100) / (1100 / 6));
  if (advance && !staticPose && !quiet && !waving && !walkerHover) {
    x += direction * 42 * elapsed;
    const edge = Math.max(0, innerWidth - 96);
    if (x >= edge) { x = edge; direction = -1; }
    if (x <= 0) { x = 0; direction = 1; }
  }
  shell.style.transform = `translateX(${x}px)`;
  draw(preview, 0, previewRow, frame);
  draw(walker, 1, walkerRow, frame);
  if (lastLabel !== rows[previewRow]) {
    lastLabel = rows[previewRow];
    label.textContent = `${lastLabel}${staticPose ? ' · static pose' : ''}`;
  }
}
function loop(now: number) {
  render(now, true);
  frameRequest = requestAnimationFrame(loop);
}
function restart() {
  cancelAnimationFrame(frameRequest);
  lastLabel = '';
  if (!ready || document.hidden) return;
  render(performance.now(), false);
  if (!reduced.matches) frameRequest = requestAnimationFrame(loop);
}
function refresh() { if (ready && reduced.matches) render(performance.now(), false); }
function activity() { lastActivity = performance.now(); }
for (const event of ['pointermove', 'pointerdown', 'keydown', 'scroll'] as const) {
  window.addEventListener(event, activity, {passive:true});
}
buttons.forEach(button => button.addEventListener('click', () => {
  selected = Number(button.dataset.state);
  wavingUntil = 0;
  buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  refresh();
}));
[document.querySelector<HTMLButtonElement>('#preview-hit')!, document.querySelector<HTMLButtonElement>('#walker-hit')!].forEach((hit, i) => {
  hit.addEventListener('click', () => {
    wavingUntil = performance.now() + 2200;
    activity(); refresh();
    // Reduced motion has no animation loop; release the static wave once.
    if (reduced.matches) setTimeout(() => { wavingUntil = 0; refresh(); }, 2200);
  });
  const hover = (active: boolean) => { if (i === 0) previewHover = active; else walkerHover = active; refresh(); };
  hit.addEventListener('pointerenter', () => hover(true));
  hit.addEventListener('pointerleave', () => hover(false));
  hit.addEventListener('focus', () => hover(true));
  hit.addEventListener('blur', () => hover(false));
});
sheet.addEventListener('load', () => { ready = true; resize(); restart(); });
sheet.addEventListener('error', () => { label.textContent = 'The pet could not load. Meet Nery in the artwork kit above.'; shell.hidden = true; });
window.addEventListener('resize', resize);
reduced.addEventListener('change', restart);
document.addEventListener('visibilitychange', restart);
