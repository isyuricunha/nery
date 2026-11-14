# Nery Mizuki

The official character home of **Nery Mizuki**, the mascot of [Mnerys](https://github.com/isyuricunha/mnerys) ("Built to be yours") and of Yuri Cunha's web properties.

This repository is the **canonical source of truth** for the character: the approved artwork kit, the identity and usage rules, and the license. Projects that feature Nery copy the assets from a tagged release of this repository and record the kit version they use. She is deliberately **not packaged** (no npm or similar): every project integrates and adapts her artwork for its own surface, and this repository exists so those adaptations never drift from the approved look.

Nery is the **mascot, never the logo**: the Mnerys geometric M stays the logo across UI, favicon, PWA and wordmark.

## The character

- **Name:** Nery Mizuki
- **Style:** friendly 2D anime chibi
- **Look:** copper-red hair, amber eyes, cream hair bows, charcoal hoodie with warm orange details
- **Palette:** dark charcoal `#211915`, warm surface `#2A211D`, terracotta accent `#CC785C`, soft cream `#F0E9E3`

Full identity, personality and do/don't rules: [docs/IDENTITY.md](docs/IDENTITY.md).

## Repository layout

```text
assets/mascot/
├── LICENSE.md                    Proprietary mascot asset license (v1.1)
├── mascot.json                   Character metadata and license reference
├── nery-mizuki-avatar.webp       Current UI avatar (kept for compatibility)
└── kit-v1/
    ├── manifest.json             Kit inventory: dimensions, provenance, limits
    ├── source/                   Approved 1536x1024 character sheet + 8 original crops
    ├── transparent/              8 poses with real alpha, PNG + WebP
    ├── avatars/                  128/256/512 px avatars, PNG + WebP
    └── preview/                  Kit preview composition

docs/
├── IDENTITY.md                   Who Nery is and how to use her
└── ARTWORK-STATUS.md             Provenance, native sizes and known limitations

CHANGELOG.md                      Kit and license history
```

## Kit v1 contents

The approved character sheet (1536x1024) carries eight poses, exported with real alpha in PNG and WebP:

| Context | Asset (relative to `assets/mascot/kit-v1/`) |
| --- | --- |
| Welcome / success | `transparent/nery-happy.webp` |
| Thinking / waiting | `transparent/nery-thinking.webp` |
| Working / tools | `transparent/nery-coding.webp` |
| Break / onboarding | `transparent/nery-coffee.webp` |
| Rest / idle | `transparent/nery-sleeping.webp` |
| Friendly integrations | `transparent/nery-with-cat.webp` |
| Character presentation | `transparent/nery-fullbody.png` |
| Alternative avatar | `avatars/nery-avatar-256.webp` |

## Using Nery in a project

1. Download the kit from the latest tagged release of this repository (or the matching `kit-vX` folder on the main branch).
2. Copy the assets your surface needs and record the kit version in your project (for example `Nery kit v1.0`).
3. Adapt presentation (placement, sizes, motion) freely; never redraw the character or invent features she does not have. New poses and expressions are produced and approved through this repository.
4. Respect the identity rules ([docs/IDENTITY.md](docs/IDENTITY.md)) and the license ([assets/mascot/LICENSE.md](assets/mascot/LICENSE.md)).

Known artwork limitations (native sizes, alpha edges) are documented in [docs/ARTWORK-STATUS.md](docs/ARTWORK-STATUS.md). In short: poses keep their original resolution (the full-body pose is 195x403 px), transparency was machine-extracted and hand-cleaned, and nothing here is an upscaled painting.

## Where she appears

- **Mnerys** (production): welcome, onboarding, empty states and interface accents.
- **Yuri Cunha's web properties** (yuricunha.com and its subdomains): authorized in the license v1.1 for the rights holder's own properties.

## License

The Nery Mizuki character and artwork are **proprietary**: **Copyright (c) 2026 Yuri Cunha, all rights reserved**, under the [Nery Mizuki Proprietary Mascot Asset License](assets/mascot/LICENSE.md). The license permits installation and display within an authorized Mnerys instance, and (since v1.1) use within Yuri Cunha's own properties as distributed by the rights holder through this official repository. Redistribution, independent reuse, packaging and derivative artwork require the rights holder's express written permission. This is **not** an open-source image license, and it is separate from the AGPL-3.0 license of the Mnerys code.

## Mirrors

- GitHub (primary): <https://github.com/isyuricunha/nery>
- GitLab: <https://gitlab.com/isyuricunha/nery>
- YuGit: <https://git.yuricunha.com/isyuricunha/nery>
