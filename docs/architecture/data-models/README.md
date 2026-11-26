# Data models

## Entities

The application distinguishes two kinds of entity:

```text
Entity = Resource | Identity
```

- A **Resource** represents application content or another managed object, such
  as a Presentation, Text, Number, Question, Message, or Numerical.
- An **Identity** represents an application user, group, or related identity
  record. Users and groups receive access grants.

This is a conceptual classification, not a single entity table or a requirement
for one shared Python model. Concrete entity types have their own tables and
schemas. [ResourceType and IdentityType](../../../backend/src/core/types.py)
identify the two families; their values match concrete model class names.

An identity object can itself be an access-policy target when controlling who
may read or manage that object. This does not change its classification to a
Resource.

## Identifier-to-type mapping

The shared identifier/type table is
[`IdentifierTypeLink`](../../../backend/src/models/access.py), physically named
`identifiertypelink`. It maps an identifier to its concrete entity type, for both
resources and identities:

| Column | Purpose |
| --- | --- |
| `id` | A Universally Unique Identifier (UUID), the primary key identifying the entity |
| `type` | Its concrete model name, such as `Presentation`, `Message`, `User`, or `Group` |

The identifier-type table covers both resources and identities. Its type
validator accepts values from either `ResourceType` or
`IdentityType`. The type identifies the concrete model; the corresponding enum
family distinguishes Resource from Identity.

For example:

```text
identifier A → type Presentation → Resource → presentation table
identifier B → type Group        → Identity → group table
```

The [model factory](../../../backend/src/models/base.py) gives generated table
models an `id` primary key referencing `identifiertypelink.id`.
[BaseCRUD](../../../backend/src/crud/base.py) registers identifiers during entity
creation. [get_types_from_ids](../../../backend/src/crud/access.py) resolves
identifiers through the shared table, allowing generic hierarchy operations to
choose the appropriate entity family and check allowed parent/child types.
CRUD and Socket.IO registries also use concrete model names to select handlers.

The mapping stores an identifier and type, not content, hierarchy membership, or an
access grant. Knowing an identifier or its type does not authorize access.

## Existing hierarchy storage

Resources and identities use separate shared edge tables, rather than a
parent column in every concrete entity table:

| Table/model | Edge fields | Additional behavior |
| --- | --- | --- |
| `ResourceHierarchy` | `parent_id`, `child_id`, `inherit` | Optional parent-scoped `order` and `label` |
| `IdentityHierarchy` | `parent_id`, `child_id`, `inherit` | Optional parent-scoped `label`; no `order` |

Both models are defined in [access.py](../../../backend/src/models/access.py).
The parent/child pair identifies an edge; a child can have multiple parents.
Allowed parent/child **types** are declared in each hierarchy's `relations` map.
Concrete model relationships expose those shared edges through the model
factory's relationship configuration.

Current examples include:

```text
Resource hierarchy:
Presentation → Question → Message | Numerical
Presentation → Text | Number
Text | Number → Text | Number
ProtectedResource → ProtectedChild → ProtectedGrandChild

Identity hierarchy:
UeberGroup → Group → SubGroup → SubSubGroup → User
AzureGroup → User
```

These illustrate supported paths, not the complete allowed-edge maps. Existing
type restrictions make many paths generation-specific. Shared hierarchy creation
rejects direct self-links and indirect cycles in both tables after authorization
and allowed-type checks. Reachability includes non-inheriting edges and
inaccessible intermediate nodes; cycle conflicts do not expose the path.
See [hierarchy cycle prevention](../security/inner-access-control.md#hierarchy-cycle-prevention)
for the error contract, transaction locking, and pre-deployment data check.

### Permission inheritance versus content loading

The edge's `inherit` flag controls permissions, not whether the structural
relationship exists:

- **Identity inheritance walks upward:** a user can receive permissions granted
  to inheriting ancestor groups.
- **Resource inheritance walks downward:** permissions on a parent resource can
  apply to inheriting descendants.

These directions compose: a group grant on a parent resource can reach a member
on a descendant resource when both inheritance paths permit it.

[AccessPolicyCRUD.filters_allowed](../../../backend/src/crud/access.py) calculates
effective access using recursive Common Table Expressions (CTEs) for ordinary
authenticated callers. It is not restricted to the entities fetched for display.
Current anonymous read/update checks use direct public policies; administrators
retain their established exceptions.

[BaseCRUD.read](../../../backend/src/crud/base.py) separately loads one level of
declared hierarchy relationships and filters each related entity for read access.
It can load parent relationships as well as children. This is not a recursive
content-tree response.

See [inner access control](../security/inner-access-control.md) and
[collection child loading](../security/collection-child-loading.md) for the
authoritative permission and loading contracts.

## Recursive resources: Text and Number

Generic resources are defined in [`models/data.py`](../../../backend/src/models/data.py),
with matching [`crud/data.py`](../../../backend/src/crud/data.py),
[`routers/api/v1/data.py`](../../../backend/src/routers/api/v1/data.py), and
[`routers/socketio/v1/data.py`](../../../backend/src/routers/socketio/v1/data.py).
Application-specific resources such as Presentation retain their own modules.

| Model | Attributes |
| --- | --- |
| `Text` | Required `content`; optional `category`, `language`, and encrypted-at-rest `confidential` |
| `Number` | Required finite floating-point `value`; optional `category`; no language or tolerance |

Both belong to the Resource family and reuse `ResourceHierarchy`:

```text
Presentation → Text | Number
Text         → Text | Number
Number       → Text | Number
```

A presentation can have collections of texts and numbers. Both resources can
have multiple parents, without stored generation numbers. Optional labels belong
to `ResourceHierarchy` relationships, not resource rows; standalone resources
have no label, and different parents can label the same child differently.
Labels use lowercase ASCII letters, digits, and hyphens only. They bind coded
interactive elements to resources; live response relationships can remain
unlabeled. Labels must be unique within each parent and resource type; a Text
and a Number under the same parent, or relationships under different parents,
can reuse the same label.

The `/api/v1/text` and `/api/v1/number` collection endpoints support lookup by `parent-id` and
`label`. Ordinary entity responses do not include relationship labels. Extended
Socket.IO reads requested with `request-access-data=true` return accessible labels
alongside `order` in the existing `hierarchies` field. Labels remain parent-scoped
relationship metadata, not attributes of the child resource.

Update relationship metadata with
`PUT /api/v1/access/hierarchy/{parent_id}/child/{child_id}` and a JSON object
containing `inherit` and/or `label`. Omitted fields stay unchanged;
`"label": null` clears a label. The identifiers come from the URL; update
values passed as query parameters are rejected.

The concurrency protocol uses one transaction-scoped advisory lock per
hierarchy, protecting cycle checks and relationship-label uniqueness through
commit. Types remain in `IdentifierTypeLink`; no copied type or resource-row
label is needed. Ordinary reads and content-only updates do not acquire these
locks. See the [concurrency design](recursive-text-number-plan.md#concurrent-hierarchy-mutations).

Optional categories use the same lowercase ASCII letters, digits, and hyphens
constraint. Frontends can use freely chosen categories to select components and
handling; categories may repeat and do not control access. They belong to the
resource, so a shared child has the same category under every parent.

Text language defaults to null and accepts alpha-2 language codes. Content is
required, including when only `confidential` is meaningful (use an empty string).
Confidential content is encrypted at rest but returned decrypted to authorized
readers; it is not a separate permission boundary.

The Text and Number setup forms validate categories and parent-specific labels
using the shared frontend [`isKebabCase`](../../../frontend_svelte/src/lib/entities.ts)
helper. Invalid values block saving;
cleared optional categories are sent as null. Creation forms with a known parent
offer an optional relationship label and send it separately from the resource
payload. A label does not become a Text or Number attribute.
The linked Text and Number tables show the label for the current parent, or `—`
for an unlabeled relationship. Socket.IO notifications for a new link or a link
update under that parent trigger an authorized re-read of the child to refresh its label. REST
relationship updates do not emit a Socket.IO status; a reload or subsequent read
refreshes the display.

**TBD (vague idea; pending frontend user interface design):** When the frontend
supports linking existing resources or copying them under a parent, consider
providing a parent-link editor where users can set the label for each
parent-child relationship. The design and placement are not decided.

**TBD:** Replace `DemoResource` with `Text` in the long run. At that point,
convert existing demo resource language values such as `en-US`, `da-DK`, and
`de-DE` to the two-letter language codes accepted by `Text`, and remove the
locale-specific cases from
[`getLanguageFlag`](../../../frontend_svelte/src/lib/entities.ts). Review the
English flag choice: `en-US` currently displays the United States flag, while
`en` displays the United Kingdom flag.

Collection, identifier, and snapshot reads return one level of independently
access-filtered relationships. The shared read path returns direct related
records without expanding their relationships, using the existing Read schemas
for all models. Parent-scoped edge labels are included only in extended reads.
Both namespaces support incremental reads,
subscriptions, submissions, linking, unlinking, relationship changes, sharing,
and deletion without a connect-time full collection transfer.

Authenticated callers can create standalone resources. Anonymous submissions
require a parent with direct public `connect` access and an explicit resulting
public policy. Anonymous updates require direct public `write` or `own`.
Delete and policy management retain authenticated admission.

Existing resources and interfaces remain available. The next presentation will
evaluate the new models before any legacy presentation migration. Generate and
apply the development database migration using the existing workflow before
using the new tables and relationship label column.

## Proposed recursive application Group

The later identity-side simplification is:

```text
Group → Group | User
```

Replace generation-specific application groups with one recursive Group model
and interface family, using `IdentityHierarchy` and preserving upward permission
inheritance and multiple parents. Keep provider-backed AzureGroup distinct.

Group's proposed `category` uses lowercase ASCII letters, digits, and hyphens,
allowing the frontend to select icons or other presentation behavior for values such as
`ueber-group` and `sub-group` without separate interfaces. These categories do not
control permissions or hierarchy depth and can be shared by multiple groups,
including siblings. Category optionality remains a decision for step 5.
The per-parent relationship-label uniqueness rule does not apply to categories.
Identity hierarchies support labels using the same rules as resource hierarchies.

Shared cycle prevention is part of the initial work; application-group
consolidation is a later step. Existing memberships, policies, identifiers, and
frontend consumers must be migrated before old group interfaces are removed.

## Future Code and File resources

Presentation retains its existing interfaces. A later Code resource could classify
code-backed functionality through frontend-defined categories while preserving
source-location and routing requirements. See the [Code plan](code-plan.md) for
category-scoped path uniqueness and source-verification decisions.

A separate [File plan](file-plan.md) covers identifier-based disk filenames,
non-unique display names, server-detected media types, and recursive relationships
with Text and Number. Media-specific rendering does not require separate resource
models.

## Implementation plans

The [recursive Text/Number and Group plan](recursive-text-number-plan.md) owns
the resource contracts, ordering and labels, public admission rules,
cycle-prevention scope, validation, evaluation, and migration boundaries.
