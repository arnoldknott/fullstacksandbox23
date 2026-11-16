# Code resource plan

This is a future design plan, not an implemented model or an expansion of
[Text/Number steps 1–4](recursive-text-number-plan.md).

Use the generic `data.py` modules at each backend layer described in
[source organization](recursive-text-number-plan.md#source-organization).
Keep the existing application-specific Presentation modules separate.

## Purpose and model

Generalize code-backed resources into a Resource named `Code`. A frontend-defined
category such as `presentation` selects its application meaning without a
separate backend model or namespace per category.

Retain source-location metadata and optional frontend path metadata. Reuse the
resource hierarchy, access policies, and existing snapshot/incremental-update
contracts rather than introducing a second resource system.

Presentation remains unchanged until its data, frontend consumers, and existing
constraints can be migrated deliberately.

## Categories and paths

Propose lowercase ASCII letters, digits, and hyphens for category values,
consistent with Group categories. Category is a classification, not an access
grant.

The proposed lookup key is `(category, path)`, with uniqueness within a category.
Before implementation, define whether `path` is relative to that category's route
prefix or already a complete frontend path. For example, category `presentation`
and path `example` could resolve to `/presentation/example`.

Category-scoped uniqueness is sufficient only if frontend routing gives
categories distinct prefixes or otherwise prevents collisions between resolved
routes. Preserve explicit normalization and validation; do not silently weaken
the current globally unique Presentation path constraint during migration.

Define null-category behavior if categories are optional before choosing the
database uniqueness constraint.

## Source location and verification

Use the same source-location validation/verification contract for every Code
category. A presentation must not have a different verification mechanism merely
because of its category.

The current [Presentation model](../../../backend/src/models/presentation.py)
stores `source` as a string and validates the optional path as a URL component;
that alone does not verify that source code exists or is trusted. Inventory any
additional checks in consumers before implementation, preserve them, and specify
any missing source verification explicitly.

Storing a Code record does not authorize executing arbitrary uploaded or remotely
referenced code. Code execution infrastructure is outside this plan.

## Delivery boundary

Before implementation, agree the category/path routing contract, category
optionality, and source-location verification requirements. Then add focused
tests and migrate Presentation consumers without losing paths, identifiers,
permissions, or hierarchy relationships. Do not remove Presentation in advance.
