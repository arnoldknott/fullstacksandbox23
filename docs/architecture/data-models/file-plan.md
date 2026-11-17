# File resource plan

This is a separate future refactoring plan based on the existing
[DemoFile model](../../../backend/src/models/demo_file.py) and
[file operations](../../../backend/src/crud/base.py). It does not expand
[Text/Number steps 1–4](recursive-text-number-plan.md).

Use the generic `data.py` modules at each backend layer described in
[source organization](recursive-text-number-plan.md#source-organization).
Keep the existing DemoFile modules available until their migration is complete.

## Storage and naming

Use one Resource model, `File`, rather than separate models for pictures, audio,
video, and documents.

- Store bytes at a deterministic location derived from the file identifier.
- Keep `name` as the display/download filename and allow duplicate names.
- Do not add a separate storage key while the identifier fully determines it.
- Return the original name through the download response's `Content-Disposition`
  header; do not rename the disk file for a download.
- Renaming a display filename must not move bytes or change their identifier.

Byte size can be obtained from filesystem metadata rather than persisted as a
second source of truth.

## Media type

Recommend persisting a server-detected `media_type`, not a value trusted from the
filename extension or the upload's declared content type. Both client-provided
values can be wrong, including after a user renames a file.

Detect common formats by inspecting bytes with a maintained content-identification
library, for example one using libmagic signatures. Some containers require
format-aware inspection to distinguish their contents. Choose the dependency and
supported detection behavior during implementation; do not add tooling now.

Detection is a classification aid, not proof that a file is valid, harmless, or
unambiguous. Text formats and files valid as multiple formats can be ambiguous.
Use `application/octet-stream` and attachment delivery when a specific safe
handling mode cannot be established. Inline rendering needs a separate explicit
allowlist/validation policy; a detected media type alone must not enable execution
of uploaded active content.

Detect once on upload and again when bytes are replaced. Renaming `name` does not
change the detected media type. Set download `Content-Type` from server-controlled
metadata and prevent browser content-type sniffing. Treat unexpected detector
failures as explicit operational errors, distinct from an unidentified format.

Persisting this derived field avoids repeating content inspection for every
listing/download and supports frontend viewer selection. If on-demand detection
is preferred instead, decide that before implementation and keep one authoritative
derivation path.

## Hierarchy and interpretation

Reuse shared resource hierarchy and cycle prevention, supporting:

```text
File   → Text | Number | File
Text   → File
Number → File
```

Text children can supply captions, descriptions, and discussion; Number children
can represent counts such as likes or downloads. The frontend defines their
meaning. Atomic counter updates and vote rules require explicit behavior; the
hierarchy does not supply them.

Apply existing parent-link, row-access, and bounded-read contracts. Do not
automatically copy Text/Number relationship-label rules to File without agreeing
whether relationships to File need labels.

## Uploads and migration

Do not introduce a new application-level upload-size limit in this refactor.
Infrastructure limits and finite storage still apply. Stream transfers rather
than reading whole uploads into application memory.

Define failure handling for partial uploads, replacements, and deletion so
database metadata and disk bytes remain consistent. Preserve authorized download
checks and do not expose physical storage paths as resource identifiers.

Migrate existing filename-based files to identifier-based paths with verified
metadata-to-byte mapping, content inspection, and a recoverable migration process.
Do not delete or overwrite existing bytes before verifying their replacements.
Keep DemoFile interfaces available until their consumers and stored files are
migrated.
