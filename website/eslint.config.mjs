import js from '@eslint/js';
import astro from 'eslint-plugin-astro';
import ts from 'typescript-eslint';
import globals from 'globals';
export default [
{ ignores: ['dist/**', '.astro/**', 'node_modules/**'] },
js.configs.recommended, ...ts.configs.recommended, ...astro.configs.recommended,
...astro.configs['jsx-a11y-recommended'],
{ languageOptions: { globals: { ...globals.browser, ...globals.node } } },
];
