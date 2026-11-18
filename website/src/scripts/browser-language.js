(() => {
  const url = new URL(window.location.href);
  if (url.pathname !== '/' || url.searchParams.get('lang') === 'en') return;
  const useBrowser = url.searchParams.get('lang') === 'auto';

  let preference;
  try {
    if (useBrowser) localStorage.removeItem('nery-language');
    else preference = localStorage.getItem('nery-language');
  } catch { /* Storage may be blocked. */ }
  if (preference !== 'en' && preference !== 'pt-br') {
    const languages = navigator.languages?.length ? navigator.languages : [navigator.language];
    const supported = languages.map(language => language?.toLowerCase().split('-')[0]);
    preference = supported.find(language => language === 'en' || language === 'pt') === 'pt'
      ? 'pt-br' : 'en';
  }
  if (preference === 'pt-br') url.pathname = '/pt-br';
  if (useBrowser) url.searchParams.delete('lang');
  if (preference === 'pt-br' || useBrowser) {
    window.location.replace(url.href);
  }
})();
