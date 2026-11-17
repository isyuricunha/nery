# Nery Mizuki — occasion kit v2.0

An additive set for Yuri Cunha's projects, products and personal pages.
The original eight-pose kit remains unchanged.

| Pose | Occasion |
| --- | --- |
| Launch celebration | Project launches, releases and milestones |
| Heart | Personal pages and moments of affection |
| Birthday | Birthdays and personal celebrations |

Transparent PNG and lossless WebP exports live in `transparent/`; native sizes
are recorded in `manifest.json`. Avoid enlarging the small celebration and heart
drawings beyond their native sizes. The birthday illustration has a larger source.

The two animation sheets, prompts and references are recorded in
`pet/frames-generated/occasions-v1/provenance.json`. Rebuild the exports and the
web-only atlas with `python scripts/build_occasions.py` (Pillow and NumPy required).
GIF previews are in `pet/occasions/`.

Copyright © 2026 Yuri Cunha. All rights reserved. These assets remain proprietary
under the terms in [the mascot license](../LICENSE.md).
