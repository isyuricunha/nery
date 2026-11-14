import { copyFile, mkdir, readdir } from 'node:fs/promises';
const root = new URL('../', import.meta.url);
const copy = (from, to) => copyFile(new URL(from, root), new URL(to, root));
await mkdir(new URL('public/kit/', root), {recursive:true});
await mkdir(new URL('public/fonts/', root), {recursive:true});
await copy('../assets/mascot/nery-mizuki-avatar.webp', 'public/nery-mizuki-avatar.webp');
await copy('../pet/nery/spritesheet.webp', 'public/spritesheet.webp');
await copy('../pet/nery/pet.json', 'public/pet.json');
for (const name of await readdir(new URL('../assets/mascot/kit-v1/transparent/', root))) {
if (name.endsWith('.webp')) await copy(`../assets/mascot/kit-v1/transparent/${name}`, `public/kit/${name}`);
}
await copy('node_modules/@fontsource-variable/geist/files/geist-latin-wght-normal.woff2', 'public/fonts/geist-latin-wght-normal.woff2');
