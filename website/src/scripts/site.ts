import './preferences';

const header = document.querySelector<HTMLElement>('.site-header')!;
new ResizeObserver(() => {
  document.documentElement.style.setProperty('--header-height', `${header.offsetHeight}px`);
}).observe(header);

for (const link of document.querySelectorAll<HTMLAnchorElement>('.language-switch a')) {
  link.addEventListener('click', () => { link.hash = window.location.hash; });
}
const preferences = document.querySelector<HTMLDetailsElement>('#preferences')!;
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && preferences.open) {
    preferences.open = false;
    preferences.querySelector('summary')?.focus();
  }
});
document.addEventListener('click', event => {
  if (event.target instanceof Node && !preferences.contains(event.target)) preferences.open = false;
});
const links = [...document.querySelectorAll<HTMLAnchorElement>('.main-nav a')];
const observer = new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    links.forEach(link => {
      if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
}, { rootMargin: '-20% 0px -55% 0px' });
for (const id of ['identity', 'pet', 'kit', 'usage']) observer.observe(document.getElementById(id)!);
