import './preferences';

const header = document.querySelector<HTMLElement>('.site-header')!;
new ResizeObserver(() => {
  document.documentElement.style.setProperty('--header-height', `${header.offsetHeight}px`);
}).observe(header);

const options = [...document.querySelectorAll<HTMLAnchorElement>('[data-language]')];
function markLanguagePreference(preference: string) {
  for (const link of options) {
    if (link.dataset.language === preference) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
  }
}

function syncLanguagePreference() {
  let preference: string | null = null;
  try { preference = localStorage.getItem('nery-language'); } catch { /* Optional persistence. */ }
  if (new URLSearchParams(location.search).get('lang') === 'en') preference = 'en';
  markLanguagePreference(preference === 'en' || preference === 'pt-br' ? preference : 'auto');
}
syncLanguagePreference();
window.addEventListener('pageshow', syncLanguagePreference);
window.addEventListener('storage', event => {
  if (event.key === 'nery-language' || event.key === null) syncLanguagePreference();
});

for (const link of options) {
  const choice = link.dataset.language!;
  const selectLanguage = () => {
    const destination = new URL(link.href);
    destination.search = location.search;
    destination.searchParams.delete('lang');
    destination.hash = location.hash;
    if (choice === 'auto') {
      destination.searchParams.set('lang', 'auto');
    } else {
      try {
        localStorage.setItem('nery-language', choice);
      } catch {
        if (choice === 'en') destination.searchParams.set('lang', 'en');
      }
      markLanguagePreference(choice);
    }
    link.href = destination.href;
  };
  link.addEventListener('click', selectLanguage);
  link.addEventListener('auxclick', event => { if (event.button === 1) selectLanguage(); });
}
const preferences = document.querySelector<HTMLDetailsElement>('#preferences')!;
preferences.addEventListener('keydown', event => {
  if (event.key === 'Escape' && preferences.open) {
    preferences.open = false;
    preferences.querySelector('summary')?.focus();
  }
});
const closeOutside = (event: Event) => {
  if (event.target instanceof Node && !preferences.contains(event.target)) preferences.open = false;
};
document.addEventListener('click', closeOutside);
document.addEventListener('focusin', closeOutside);
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
