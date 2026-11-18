import { occasionKit } from '../generated/occasion-poses';
import { masterArt } from '../generated/web-art';
import { messages, type Locale } from '../i18n/messages';

const originals = [
  ['portrait', 745, 905], ['happy', 222, 198], ['thinking', 214, 197],
  ['coding', 225, 218], ['coffee', 225, 222], ['sleeping', 312, 228],
  ['with-cat', 294, 198], ['fullbody', 195, 403],
] as const;

export const artworkFilters = ['all', 'everyday', 'occasions', 'masters'] as const;

export function artworks(locale: Locale) {
  const c = messages[locale];
  return [
    ...originals.map(([id, width, height], index) => ({
      id, width, height, src: `/kit/nery-${id}.webp`, group: 'everyday',
      title: c.poses[index], description: c.poseDescriptions[index],
    })),
    ...occasionKit.poses.map((pose, index) => ({
      ...pose, src: `/kit-v2/${pose.file}`, group: 'occasions',
      title: c.occasionNames[index], description: c.occasionDescriptions[index],
    })),
    ...masterArt.map(pose => ({
      ...pose, group: 'masters',
      title: c.masterArt[pose.id].title, description: c.masterArt[pose.id].description,
    })),
  ];
}
