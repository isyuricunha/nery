import { currentMessages } from '../i18n/messages';

const c = currentMessages();
type Topic = keyof typeof c.speech;
type Stage = 'preview' | 'walker' | 'occasion';
const toggle = document.querySelector<HTMLInputElement>('#speech-toggle')!;
const another = document.querySelector<HTMLButtonElement>('#speech-another')!;
const bubbles = [...document.querySelectorAll<HTMLElement>('.speech-bubble')];
let enabled = true;
try { enabled = localStorage.getItem('nery-speech') !== 'off'; } catch { /* Storage is optional. */ }
const indices = new Map<string, number>();
const timers = new Map<HTMLElement, ReturnType<typeof setTimeout>>();
const triggers = new WeakMap<HTMLElement, HTMLButtonElement>();
const walkerBubble = document.querySelector<HTMLElement>('#walker-speech')!;
const walkerShell = document.querySelector<HTMLElement>('.walker-shell')!;

export function positionWalkerSpeech(x: number): void {
  if (walkerBubble.hidden) return;
  const width = walkerBubble.offsetWidth;
  const left = Math.max(12, Math.min(x, window.innerWidth - width - 12));
  const shift = left - x;
  walkerShell.style.setProperty('--bubble-shift', `${shift}px`);
  walkerShell.style.setProperty('--bubble-tail', `${Math.max(12, Math.min(width-24, 42-shift))}px`);
}

function hide(bubble: HTMLElement): void {
  clearTimeout(timers.get(bubble));
  bubble.hidden = true;
}

function markToggle(): void {
  toggle.disabled = false;
  toggle.checked = enabled;
  another.disabled = !enabled;
}

export function say(topic: Topic, target: Stage, trigger: HTMLButtonElement): void {
  if (!enabled || document.hidden) return;
  const bubble = document.querySelector<HTMLElement>(`#${target}-speech`);
  if (!bubble) return;
  triggers.set(bubble, trigger);
  const lines: string[] = c.speech[topic];
  const index = indices.get(topic) ?? 0;
  bubble.querySelector('p')!.textContent = lines[index % lines.length];
  indices.set(topic, index + 1);
  bubble.hidden = false;
  if (target === 'walker') positionWalkerSpeech(walkerShell.getBoundingClientRect().left);
  clearTimeout(timers.get(bubble));
  // Long enough to read, with no typing animation or automatic chatter.
  timers.set(bubble, setTimeout(() => {
    if (!bubble.matches(':focus-within, :hover')) hide(bubble);
  }, 12000));
}

toggle.addEventListener('change', () => {
  enabled = toggle.checked;
  try { localStorage.setItem('nery-speech', enabled ? 'on' : 'off'); } catch { /* Storage is optional. */ }
  if (!enabled) bubbles.forEach(hide);
  markToggle();
});
another.addEventListener('click', () => say('hello', 'occasion', another));
function dismiss(bubble: HTMLElement) {
  triggers.get(bubble)?.focus({ preventScroll: true });
  hide(bubble);
}
bubbles.forEach(bubble => bubble.querySelector('button')!.addEventListener('click', () => dismiss(bubble)));
document.addEventListener('visibilitychange', () => { if (document.hidden) bubbles.forEach(hide); });
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  for (const bubble of bubbles) {
    if (bubble.contains(document.activeElement)) dismiss(bubble);
    else hide(bubble);
  }
});
markToggle();
