---
name: kurogane-metahuman-explore
description: Run guarded, reference-led Kurogane MetaHuman Explore work across Blender and Unreal. Use when resuming or iterating the protected Frey-derived face or body, custom-mesh round trips, visual-measurement controls, hairline, approved hair and facial hair, human-wraith garment previews, candidate replay, visual capture comparison, or crash recovery.
---

# Kurogane MetaHuman Explore

## Purpose

Continue reversible MetaHuman experiments without confusing a promising preview
with an accepted asset. Keep the approved reference as visual authority, preserve
the protected source exactly, and leave each candidate reproducible from durable
records.

Use Blender as the fast geometry-formation loop and Unreal as the milestone
integration and final visual-context loop. Do not spend Unreal-scale time proving
an idea that a neutral-clay Blender render can reject.

This skill does not grant protocol, save, production-assembly, merge, push,
download, or cloud authority.

## Reconstruct Current Truth

Before changing the live character:

1. Read the newest MetaHuman handoff, authoritative asset catalog, campaign
   records, captures, and exact protected-asset hash.
2. Inspect the live Unreal process and current editor state. Distinguish a live
   unsaved candidate from a replayed or persisted candidate.
3. Confirm the active work mode. Use Explore while comparing unfrozen
   candidates; Validate only one explicitly frozen candidate.
4. Treat the approved face/body reference as the authority for every visible
   element. Retired demon armour, Yamiyo, and Akatsuki are out of scope.
5. Keep scope to the protected Frey-derived MetaHuman, human-wraith garments,
   and selected hair/facial hair.
6. Resolve four asset roles before any save: immutable source, immutable Explore
   baseline, explicitly mutable scratch character, and named retained candidate.
   Never let one file serve as both baseline and scratch.

If durable records and the live UI disagree, preserve the discrepancy and
reconstruct the candidate from records. Do not guess which state is authoritative.

## Protect the Baseline

- Hash the protected asset before and after each candidate.
- If the existing workflow already overwrites an asset called a baseline, stop
  before the next save. Record its current hash and state, then split baseline,
  scratch, and retained-candidate roles under exact save authority.
- Keep Explore candidates unsaved unless the user grants exact save or promotion
  authority. Avoid Save All and canonical content writes.
- When saving is authorized, save only the explicitly mutable scratch asset or a
  new named candidate. Never overwrite the immutable source or Explore baseline.
- Unreal may still create recovery packages under `Saved/Autosaves` while the
  source under `Content` remains unchanged. Record that distinction; prove the
  protected source hash rather than claiming that no recovery write occurred.
- Use local installed assets only. Do not invoke cloud services, downloads,
  autorigging, high-resolution generation, or production assembly.
- Keep one MetaHuman asset editor open. Never call
  `AssetEditorSubsystem.CloseAllEditorsForAsset` on a MetaHuman asset; UE 5.8 can
  assert in `SStandaloneAssetEditorToolkitHost`.
- After a crash, decline unaccepted package restoration and replay the sealed
  baseline-to-candidate sequence. Verify every replay delta before continuing.

## Iterate in Separable Layers

Change one visual layer at a time:

1. **Reference and landmarks** — Create direct front, profile, and body
   comparisons. Use registered, matched-scale overlays for proportion work.
   Project and identify landmark indices before editing geometry; never infer
   semantic indices from appearance alone.
2. **Structure** — Adjust bone or landmark geometry while holding skin detail
   and groom context stable. One layer may require coupled anatomical moves: a
   cheek hollow, for example, needs a projecting shelf and a recessed valley,
   not merely a stronger scalar indentation.
3. **Apparent age** — Treat structural age and skin-detail age as separate
   controls. A gaunt mesh can still read young if the face-detail layer remains
   youthful.
4. **Groom context** — Add approved local hair, brows, moustache, beard,
   eyelashes, and peachfuzz without changing geometry.
5. **Body and garments** — Inspect the complete silhouette with the selected
   human-wraith garments before judging proportions.
6. **Capture and compare** — Capture the same framing and lighting for the
   reference and each candidate. Record the result before moving to the next
   layer.

## Use a Two-Speed Geometry Loop

For structural face work:

1. Start from a hash-identified Blender parent with unchanged MetaHuman topology.
2. Render neutral clay at matched reference scale before editing.
3. State one geometric hypothesis and the visual observation that would reject it.
4. Run a small parameter sweep to new, non-overwriting scratch outputs.
5. Reject obviously wrong geometry in Blender; do not import every sweep to Unreal.
6. Bring only a promising checkpoint through the supported MetaHuman template-fit
   path, then inspect skin, expressions, grooms, and complete-character silhouette.

Reusable deformation scripts must assert the expected parent hash, vertex count,
and topology, refuse overwrite, and record input/output hashes. Topology and
triangle-orientation checks are sufficient for ordinary Explore sweeps; defer
heavier integration evidence to a retained checkpoint.

For local MetaHuman preview selection, prefer the supported Collection flow:

- `get_preview_collection`
- `try_add_item_from_wardrobe_item`
- `set_single_slot_selection`
- `on_edit_preview_collection`
- `assemble_for_preview`

This is a reversible preview pipeline, not production assembly. In the
MetaHuman viewport, focus the viewport and press `F` to cycle Face and Body
framing rather than relying on fragile screen coordinates.

Bind preview identity to the returned palette item key. Re-adding a local
WardrobeItem can produce display labels such as `Name (2)` or `Name (3)` even
when the underlying item is correct. Treat the returned key plus the exact
WardrobeItem hash as authoritative; use the display label only as a checked
diagnostic.

## Control Identity and Solver Coupling

- Treat the face-coefficient vector as a structured patch packet, not a flat
  homogeneous vector. When blending donors, change only selected PCA spans and
  preserve each patch's fixed transform fields, structural metadata, the neck,
  and every unselected span exactly.
- If local brow, nose, and jaw edits cannot overcome a soft upstream identity,
  test a stronger identity-source contribution first. A stronger global blend
  can pull the eyes smaller, reduce canthal tilt, and widen the midface, so
  explicitly re-lock the user's measured eye and midface constraints afterward.
- `commit_face_state` strongly attenuates and couples literal landmark
  translation requests. Gate measured final geometry, protected metrics, and
  untargeted propagation; do not require literal requested deltas or a previous
  equivalent coefficient hash.
- Before any solver commit, capture the complete coefficient vector. On a
  rejected attempt, restore that exact vector with
  `set_face_model_coefficients` and verify both landmark geometry and the
  protected asset hash. Do not depend on inverse landmark requests as the
  primary rollback.
- Remove beard and moustache temporarily when evaluating mouth, chin, jaw, and
  age structure. Restore facial hair only after the clean geometry gate, and
  reject a mechanically valid groom if its visible density or coverage is wrong.

## Prove the Measurement

- A metric is not a gate until it is specific to the claimed property. Perturb
  plausible nuisance variables—lighting direction, framing, scale, material, or
  hair—and reject a metric that moves for unrelated reasons.
- Test the control itself. Bad exposure, crushed shadows, mismatched cameras, or
  guessed sampling pixels invalidate the experiment even when it emits numbers.
- Treat advisory consultation as hypothesis generation. Demonstrate the mechanism
  locally before adopting the conclusion.
- A visible contradiction with the approved reference overrides a numerical
  pass. Diagnose the metric instead of increasing deformation to satisfy it.

## Apply Visual Gates

Judge against the reference, not against the previous candidate:

- face silhouette, asymmetry, eye size and depth, brow severity, nose
  projection, mouth width and shape, jaw width, chin, and profile;
- apparent age, skin roughness, weathering, and human-wraith markings;
- hair silhouette, bun or topknot visibility, forehead exposure, and hairline;
- hairline center balance and rightward or leftward skew as a gate separate
  from scalp coverage and topology;
- facial-hair density, coverage, and silhouette. Reject a technically valid
  goatee if it reads as a full beard or hides the intended mouth or jaw shape;
- garment silhouette and compatibility with the approved human-wraith look.

Do not freeze hair or facial hair from a face-only crop. Capture both the front
face and full body or head silhouette first.

## Record Every Useful Cycle

For each candidate, record:

- parent candidate and replay order;
- exact protected asset and local wardrobe-item hashes;
- exact scratch or retained-candidate input/output hashes;
- changed landmarks, appearance controls, and preview slots;
- before and after protected-asset hash;
- front, profile, and body or head captures that were actually inspected;
- pass or fail observations by visual layer;
- whether the state is unsaved, replayable, frozen, or promoted.

Keep execution, geometry, and visual results distinct. A command may have
`execution_status: PASS` while `visual_status: REJECT` or `UNRESOLVED`; never
label that candidate simply `PASS`.

Routine scratch sweeps may remain temporary. When an experiment changes what the
team believes, copy the decisive inputs, outputs, control renders, command, hashes,
and compact result into the campaign before relying on the finding.

Capture only high-signal learning: reusable controls, root causes, validated
failure modes, and safeguards. Do not turn every visual opinion into doctrine.

## Declare a Safe Hold

A hold is safe only when:

- the protected asset hash is unchanged;
- the exact current candidate is captured and replayable;
- required front, profile, and body evidence is saved;
- the handoff, authoritative catalog, and checksum sidecar reflect the current
  result and explicit next action;
- no unresolved UI-only state is being mistaken for durable progress.

If the Mac is locked while an uncaptured unsaved candidate is live, report the
lock as an active blocker rather than declaring a safe hold. Continue non-UI
evidence work when useful, then resume capture after unlock.
