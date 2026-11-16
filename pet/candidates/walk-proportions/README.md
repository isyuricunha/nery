# Walking proportion references

These are historical review assets, **not inputs to the live pet build**.
The rounded A proportion was selected as a reference. The active locomotion
revision combines that direction with the existing Idle artwork; see
`pet/frames-generated/motion-v5/` and `pet/preview/walk-review.html`.

- `rounded.gif`: sixteen fully illustrated cels, emphasizing the original
  fuller chibi proportions. Its gait still needs refinement after proportion
  selection; this is not a completed walking fix.
- `articulated.gif`: a thirty-two-frame skeletal candidate with fuller thighs
  and calves, shorter bone segments, continuous stance support and arm swing.
  The earlier skinny articulated version was rejected and is not included as
  a runtime asset.
- `comparison.html`: the actual GIFs at normal speed beside the previous walk.
- `rounded/walk.png`, `rig/`, `positions-guide.png` and `prompts.json`: sources.

`previous.gif` preserves the runtime before locomotion revision v5. Failure
alignment remains independently saved at milestone `2c0aeff`.

Rebuild from the repository root:

```bash
python pet/candidates/walk-proportions/render_rounded.py
python pet/candidates/walk-proportions/render_articulated.py
python pet/candidates/walk-proportions/render_comparison.py
```

All generated imagery follows the repository's proprietary mascot license.
