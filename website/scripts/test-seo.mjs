import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

// Check the actual exported HTML so omissions in the template fail the release check.
for (const [locale, file, language, path] of [
  ['en', 'index.html', 'en', '/'], ['pt-br', 'pt-br/index.html', 'pt-BR', '/pt-br'],
]) {
  test(`${locale}: exported page has complete, consistent search metadata`, async () => {
    const html = await readFile(new URL(`../dist/${file}`, import.meta.url), 'utf8');
    const canonical = `https://nery.yuricunha.com${path}`;
    assert.ok(html.includes(`lang="${language}"`));
    assert.ok(html.includes(`rel="canonical" href="${canonical}"`));
    assert.equal((html.match(/<h1\b/g) || []).length, 1);
    assert.match(html, /<meta name="description" content="[^"]{60,200}"/);
    assert.match(html, /<meta name="robots" content="index,follow,max-image-preview:large"/);
    for (const lang of ['en','pt-BR','x-default']) assert.ok(html.includes(`hreflang="${lang}"`));
    assert.ok(html.includes(`https://nery.yuricunha.com/social/nery-${locale}.png`));
    const avif = [...html.matchAll(/<source[^>]+>/g)].find(match => match[0].includes('type="image/avif"'));
    assert.ok(avif);
    assert.match(avif[0], /srcset=/);
    const graph = JSON.parse(html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1])['@graph'];
    assert.equal(graph.filter(node => node['@type']==='WebSite').length, 1);
    const page = graph.find(node => node['@type']==='WebPage');
    assert.equal(page.url, canonical);
    assert.equal(page.inLanguage, language);
    assert.equal(page.isPartOf['@id'], 'https://nery.yuricunha.com/#website');
    assert.equal(graph.find(node => node['@type']==='CreativeWork').creator['@id'], 'https://yuricunha.com/#person');
    const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
    assert.equal(ids.length, new Set(ids).size, 'IDs must be unique');
    const png = await readFile(new URL(`../dist/social/nery-${locale}.png`, import.meta.url));
    assert.equal(png.readUInt32BE(16), 1200);
    assert.equal(png.readUInt32BE(20), 630);
  });
}
test('sitemap covers both languages and excludes error and review pages', async () => {
  const xml = await readFile(new URL('../dist/sitemap-0.xml', import.meta.url), 'utf8');
  assert.equal((xml.match(/<loc>/g) || []).length, 2);
  assert.match(xml, /hreflang="en"/);
  assert.match(xml, /hreflang="pt-BR"/);
  assert.doesNotMatch(xml, /404|review\.html/);
});
test('error and developer preview pages are explicitly excluded from indexing', async () => {
  for (const file of ['404.html','motion-review.html','walk-review.html','occasions-review.html','walk-candidate-review.html']) {
    const html = await readFile(new URL(`../dist/${file}`, import.meta.url), 'utf8');
    assert.match(html, /name="robots" content="noindex,follow"/);
    if (file==='404.html') assert.doesNotMatch(html, /rel="canonical"/);
  }
});
