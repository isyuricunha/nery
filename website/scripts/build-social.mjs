import sharp from 'sharp';
import { fileURLToPath } from 'node:url';
import { mkdir, writeFile, copyFile } from 'node:fs/promises';

const directory = new URL('../public/social/', import.meta.url);
await mkdir(directory, { recursive: true });
for (const language of ['en', 'pt-br']) {
  const pt = language === 'pt-br';
  const label = pt ? 'A mascote pessoal de Yuri Cunha.' : 'Yuri Cunha’s personal mascot.';
  const subtitle = pt ? 'Seus projetos. Seus produtos. Sua Mizuki.' : 'His projects. His products. His Mizuki.';
  const background = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
    <rect width="1200" height="630" fill="#100e0d"/>
    <rect x="716" y="36" width="438" height="558" rx="56" fill="#28201a" stroke="#825b41"/>
    <path d="M74 112H170" stroke="#e6ad86" stroke-width="3"/>
    <g font-family="Arial,Helvetica,sans-serif">
      <text x="74" y="83" fill="#e6ad86" font-size="22" letter-spacing="4">N / M</text>
      <text x="70" y="260" fill="#f5eee6" font-size="116" font-weight="700" letter-spacing="-7">Nery</text>
      <text x="70" y="377" fill="#e6ad86" font-size="116" font-weight="700" letter-spacing="-7">Mizuki.</text>
      <text x="74" y="441" fill="#f5eee6" font-size="26">${label}</text>
      <text x="74" y="482" fill="#bfb2a6" font-size="21">${subtitle}</text>
      <text x="74" y="571" fill="#bfb2a6" font-size="18">nery.yuricunha.com</text>
    </g>
  </svg>`);
  const portrait = fileURLToPath(new URL('../../assets/mascot/kit-v1/transparent/nery-portrait.png', import.meta.url));
  const character = await sharp(portrait).resize({ width: 410, height: 530, fit: 'inside', withoutEnlargement: true }).png().toBuffer();
  const png = await sharp(background).composite([{ input: character, left: 730, top: 65 }]).png().toBuffer();
  await writeFile(new URL(`nery-${language}.png`, directory), png);
}
await copyFile(new URL('nery-en.png', directory), new URL('../public/og.png', import.meta.url));
