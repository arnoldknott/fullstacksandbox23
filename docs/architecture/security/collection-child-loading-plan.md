# Collection child-loading plan (cartesian fan-out fix)

Status: proposed. No code changed yet. This plan preserves the inner access-control
semantics; see the change boundary in [AGENTS.md](../../../AGENTS.md#security-layers-and-change-boundaries)
and the inner-layer contract in [inner-access-control.md](inner-access-control.md).

## Problem

`BaseCRUD.read` in [`backend/src/crud/base.py`](../../../backend/src/crud/base.py) eager-loads
every hierarchy child by stacking one outer join per relationship onto the same hierarchy table
(`resourcehierarchy` / `identityhierarchy`) inside a single `SELECT`, then materialises them with
`contains_eager`. When a model has two or more sibling child collections, the rows multiply.

Measured on production for the questions overview (`/api/v1/question/snapshot`):

- `Question` has three hierarchy relationships: `presentations` (parent side), `messages` (child
  side), `numericals` (child side) — see the `Question` model in
  [`backend/src/models/quiz.py`](../../../backend/src/models/quiz.py) and the hierarchy map in
  [`backend/src/models/access.py`](../../../backend/src/models/access.py) (`ResourceHierarchy.relations`).
- 18 questions expanded to **92,516 joined rows** (`messages × numericals` per question) in a single
  statement. `EXPLAIN ANALYZE` reported ~350 ms in PostgreSQL, but the wall-clock cost was ~2 s: the
  backend must fetch all 92,516 rows and run `results = response.unique().all()` plus ORM hydration in
  Python.
- The cost scales with the number of children per parent (answers per question), which production has
  far more of than staging. It is unrelated to the size of the `accesslog` table.

## Why the single-query join was used, and why it is not required

The single multi-join with `contains_eager` was chosen so that `filters_allowed()` also filters the
children: reading a parent must not implicitly grant read access to children the caller is not
authorised for (for example, when no `inherit` flag is set on the hierarchy relationship and no other
policy grants the action on the child). That correctness requirement stays.

The row explosion, however, is a property of putting multiple sibling collections in one flat
statement — SQL must emit `messages × numericals` rows per parent regardless of access control. The
access rule only requires each child set to be filtered by `filters_allowed()`; it does not require
the children to share a statement with each other or with the parent. Loading each relationship in its
own access-filtered query changes multiplication into addition
(`18 + presentations + messages + numericals`).

## Enabling fact

The hierarchy relationships are already real SQLAlchemy relationships built by
`_build_hierarchy_relationship` in [`backend/src/models/base.py`](../../../backend/src/models/base.py):
`link_model` is the hierarchy table, `viewonly=True`, `lazy="noload"`, with explicit
`primaryjoin`/`secondaryjoin`. Because they are proper secondary relationships, `selectinload` works
natively and the per-child access filter can be injected with `with_loader_criteria`. This keeps the
change small and contained to one method, leaving `filters_allowed()` untouched.

## Decision: child ordering

Children are user-visible in order, so ordering must be preserved. The current code orders
a parent's children by `ResourceHierarchy.order`. Because `order` lives on the association table and
`selectinload` orders by the child query, the parent-side hierarchy relationships must declare an
`order_by` on the association `order` column. This is added in `_build_hierarchy_relationship` for
parent-type relationships only (child-side relationships have no meaningful order from the child).

## Phase 1 — primary fix (contained to `BaseCRUD.read`)

Replace the `for relationship in class_mapper(self.model).relationships:` block (outer joins,
per-relationship `COUNT`, `contains_eager`) with, per hierarchy relationship:

- `selectinload(getattr(self.model, relationship.key))`
- `with_loader_criteria(related_model, related_model.id.in_(access_ids), include_aliases=True)` where
  `access_ids = filters_allowed(select(related_model.id), Action.read, related_model, current_user)`

The per-relationship `count_related_statement` is removed (an empty `selectinload` result is simply an
empty list). `response.unique()` becomes unnecessary because there is no cartesian product; it is kept
as a harmless safeguard.

```python
from sqlalchemy.orm import selectinload, with_loader_criteria

statement = select(self.model)
statement = self.policy_crud.filters_allowed(
    statement, Action.read, self.model, current_user
)

for relationship in class_mapper(self.model).relationships:
    related_model = self.type.get_model(relationship.mapper.class_.__name__)
    related_type = self.type(related_model.__name__)
    is_hierarchy = any(
        (self.entity_type == parent and related_type in children)
        or (self.entity_type in children and related_type == parent)
        for parent, children in self.relations.items()
    )
    if not is_hierarchy:
        continue
    access_ids = self.policy_crud.filters_allowed(
        select(related_model.id), Action.read, related_model, current_user
    )
    statement = statement.options(
        selectinload(getattr(self.model, relationship.key)),
        with_loader_criteria(
            related_model,
            related_model.id.in_(access_ids),
            include_aliases=True,
        ),
    )

# filters / order_by / group_by / having / limit / offset unchanged
```

### Ordering change

In `_build_hierarchy_relationship`, for `RelationshipHierarchyType.parent` relationships, add
`order_by` on the association `order` column so `selectinload` returns children in hierarchy order,
matching the previous `contains_eager` behaviour. Child-side relationships are left unordered as
before.

## Preserved semantics (must not regress)

- Each child collection is still filtered by `filters_allowed(Action.read, related_model, user)`;
  children the caller cannot read are excluded.
- Parents with zero accessible children are still returned (with an empty child list).
- Anonymous/public path and Microsoft administrator/group short-circuits in `filters_allowed`
  (see [`backend/src/crud/access.py`](../../../backend/src/crud/access.py)) are unchanged.
- Only direct children are loaded (one level), exactly as today.
- Child ordering by `ResourceHierarchy.order` is preserved via the added `order_by`.

## Deferred phases (only if measurement still shows cost after Phase 1)

These touch the inner security layer more deeply and require explicit sign-off before implementation.

- **Phase 2 — memoise the accessible-id set per request.** `filters_allowed` is currently rebuilt many
  times per request (main read, each relationship, and `read_access_rights` four times), each with
  recursive inheritance CTEs. Resolve "resource ids this identity can read (with inheritance)" once and
  reuse it as `id IN (:set)`. Same rules, less recomputation. Bound is reasonable because administrators
  short-circuit.
- **Phase 3 — inheritance closure table.** Maintain a transitive closure on hierarchy/policy writes so
  reads never recurse. Larger change: write-path complexity and invalidation. Defer unless deep
  hierarchies remain a measured bottleneck after Phase 1.

## Affected files

- [`backend/src/crud/base.py`](../../../backend/src/crud/base.py) — `read()` relationship block (primary change).
- [`backend/src/models/base.py`](../../../backend/src/models/base.py) — `_build_hierarchy_relationship` (`order_by` for parent-type relationships).
- [`backend/src/crud/access.py`](../../../backend/src/crud/access.py) — `filters_allowed` untouched in Phase 1; Phase 2 would add a per-request memo helper.

## Verification

1. Backend access-control tests in the test environment must stay green (child access filtering).
   Enter with `./scripts/enter_backend_test.sh`, then run the CRUD read and access-policy suites.
2. Reconstructed query row count drops from 92,516 to ~18 plus a few hundred child rows.
3. `curl -s -o /dev/null -w "%{time_total}\n"` against staging `/api/v1/question/snapshot` before and
   after.
4. Manual checks: parents with no accessible children still returned; child ordering preserved.

## Scope note

The fix is centralised in `BaseCRUD.read`, so it benefits every model with two or more child
relationships (categories, module/section/topic, protected-resource chains, identity groups), not just
questions.
