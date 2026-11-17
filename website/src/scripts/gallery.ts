import { currentMessages } from '../i18n/messages';

const c = currentMessages();
const cards = [...document.querySelectorAll<HTMLElement>('[data-artwork]')];
const openers = [...document.querySelectorAll<HTMLButtonElement>('[data-art-index]')];
const filters = [...document.querySelectorAll<HTMLButtonElement>('[data-filter]')];
const dialog = document.querySelector<HTMLDialogElement>('#artwork-dialog')!;
const image = document.querySelector<HTMLImageElement>('#artwork-large')!;
const title = document.querySelector<HTMLElement>('#artwork-title')!;
const description = document.querySelector<HTMLElement>('#artwork-description')!;
let active = 0;
let opener: HTMLButtonElement | undefined;

function visibleIndices(): number[] {
  return cards.flatMap((card, i) => card.hidden ? [] : [i]);
}
function show(index: number): void {
  active = index;
  const data = openers[index].dataset;
  image.src = data.src!;
  image.alt = `Nery Mizuki — ${data.title}`;
  image.width = Number(data.width);
  image.height = Number(data.height);
  image.style.setProperty('--native-width', `${data.width}px`);
  title.textContent = data.title!;
  description.textContent = data.description!;
}
function step(direction: number): void {
  const indices = visibleIndices();
  const next = (indices.indexOf(active) + direction + indices.length) % indices.length;
  show(indices[next]);
}
filters.forEach(button => button.addEventListener('click', () => {
  const group = button.dataset.filter;
  filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
  cards.forEach(card => { card.hidden = group !== 'all' && card.dataset.group !== group; });
  document.querySelector('#gallery-result')!.textContent = c.artworkCount.replace('{count}', String(visibleIndices().length));
}));
openers.forEach((button, i) => {
  button.disabled = false;
  button.addEventListener('click', () => { opener = button; show(i); dialog.showModal(); });
});
document.querySelector<HTMLElement>('.filter-group')!.hidden = false;
document.querySelector('#artwork-previous')!.addEventListener('click', () => step(-1));
document.querySelector('#artwork-next')!.addEventListener('click', () => step(1));
dialog.addEventListener('keydown', event => {
  if (event.key === 'ArrowRight') { event.preventDefault(); step(1); }
  if (event.key === 'ArrowLeft') { event.preventDefault(); step(-1); }
});
dialog.addEventListener('close', () => opener?.focus({ preventScroll: true }));
