import en from './en.json';
import ptBR from './pt-br.json';

export type Locale = 'en' | 'pt-br';
export const messages = { en, 'pt-br': ptBR };
export function currentMessages() {
  return messages[document.documentElement.lang === 'pt-BR' ? 'pt-br' : 'en'];
}
