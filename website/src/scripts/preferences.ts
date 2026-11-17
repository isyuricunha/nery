import { currentMessages } from '../i18n/messages';

export const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const c = currentMessages();
function read(key: string): boolean {
  try { return localStorage.getItem(key) !== 'off'; } catch { return true; }
}
let animations = read('nery-motion');
let walker = read('nery-walker');
export const motionEnabled = () => animations && !reduced.matches;
export const walkerEnabled = () => walker;
const motionInput = document.querySelector<HTMLInputElement>('#motion-enabled')!;
const walkerInput = document.querySelector<HTMLInputElement>('#walker-enabled')!;
function sync(): void {
  motionInput.checked = motionEnabled();
  motionInput.disabled = reduced.matches;
  walkerInput.checked = walker;
  walkerInput.disabled = false;
  document.querySelector('#motion-help')!.textContent = reduced.matches ? c.motionReduced : c.motionHelp;
  document.documentElement.dataset.motion = motionEnabled() ? 'on' : 'off';
  document.dispatchEvent(new Event('nery:preferences'));
}
function save(key: string, value: boolean): void {
  try { localStorage.setItem(key, value ? 'on' : 'off'); } catch { /* Optional preference persistence. */ }
  sync();
}
motionInput.addEventListener('change', () => { animations = motionInput.checked; save('nery-motion', animations); });
walkerInput.addEventListener('change', () => { walker = walkerInput.checked; save('nery-walker', walker); });
reduced.addEventListener('change', sync);
sync();
