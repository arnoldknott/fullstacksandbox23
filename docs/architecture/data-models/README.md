# Data models

## Entities

The application distinguishes two kinds of entity:

```text
Entity = Resource | Identity
```

- A **Resource** represents application content or another managed object, such
  as a Presentation, Question, Message, or Numerical.
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
| `ResourceHierarchy` | `parent_id`, `child_id`, `inherit` | Optional `order`, scoped to the parent |
| `IdentityHierarchy` | `parent_id`, `child_id`, `inherit` | No resource-order column |

Both models are defined in [access.py](../../../backend/src/models/access.py).
The parent/child pair identifies an edge; a child can have multiple parents.
Allowed parent/child **types** are declared in each hierarchy's `relations` map.
Concrete model relationships expose those shared edges through the model
factory's relationship configuration.

Current examples include:

```text
Resource hierarchy:
Presentation → Question → Message | Numerical
ProtectedResource → ProtectedChild → ProtectedGrandChild

Identity hierarchy:
UeberGroup → Group → SubGroup → SubSubGroup → User
AzureGroup → User
```

These illustrate supported paths, not the complete allowed-edge maps. Existing
type restrictions make many paths generation-specific. Direct self-links are
validated today; indirect-cycle prevention is proposed in the
[recursive resource plan](recursive-text-number-plan.md#step-1-shared-cycle-prevention).

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

## Proposed recursive resources: Text and Number

These models are planned, not implemented:

| Model | Proposed attributes |
| --- | --- |
| `Text` | Required `content`; optional `label`, `language`, and encrypted-at-rest `confidential` |
| `Number` | Required numeric `value`; optional `label`; no language or tolerance |

Both belong to the Resource family and reuse `ResourceHierarchy`:

```text
Presentation → Text | Number
Text         → Text | Number
Number       → Text | Number
```

A presentation can have collections of texts and numbers. Both resources can
have multiple parents, without stored generation numbers. Labels are optional
even for children and use lowercase ASCII letters, digits, and hyphens only.
They bind coded interactive elements to resources; live responses can remain
unlabeled. Labels must be unique within each parent across both Text and Number;
different parents can reuse the same label.

Keep existing resources and interfaces available. The next presentation will
evaluate the new models before any legacy presentation migration.

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
Text/Number's per-parent label uniqueness rule does not apply; a separate Group
`label` can be considered later if needed.

Shared cycle prevention is part of the initial work; application-group
consolidation is a later step. Existing memberships, policies, identifiers, and
frontend consumers must be migrated before old group interfaces are removed.

## Implementation plan

The [recursive Text/Number and Group plan](recursive-text-number-plan.md) owns
the detailed proposed changes, ordering and labels, public admission rules,
cycle-prevention scope, validation, evaluation, and migration boundaries. No
model, endpoint, namespace, or database migration is implemented by these
documentation changes.
