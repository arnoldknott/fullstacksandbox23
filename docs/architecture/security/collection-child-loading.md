# Collection child-loading and access filtering

This document describes how `BaseCRUD.read` loads an entity's hierarchy children and applies
access control to them. It is part of the inner access-control layer; see the change boundary in
[AGENTS.md](../../../AGENTS.md#security-layers-and-change-boundaries) and the inner-layer contract in
[inner-access-control.md](inner-access-control.md).

## How children are loaded

`BaseCRUD.read` in [`backend/src/crud/base.py`](../../../backend/src/crud/base.py) reads the target
entities in one access-filtered query, then loads each hierarchy child collection in its own query
with `selectinload`. For every hierarchy relationship of the model it adds:

- `selectinload(<relationship>)`, which loads that relationship's children in a separate query keyed by
  the parent ids, and
- `with_loader_criteria(<child model>, <child model>.id.in_(access_ids))`, where
  `access_ids = filters_allowed(select(<child model>.id), Action.read, <child model>, current_user)`.

Because each relationship is loaded in its own query, sibling collections add rows rather than
multiplying them, and the child access filter is evaluated once per relationship.

The hierarchy relationships themselves are declared by `_build_hierarchy_relationship` in
[`backend/src/models/base.py`](../../../backend/src/models/base.py) as `viewonly`, `lazy="noload"`
secondary relationships whose link model is `ResourceHierarchy` or `IdentityHierarchy`. Non-hierarchy
relationships (for example direct-FK side tables such as `User.user_profile`) are skipped by `read`;
their access is governed by access to the parent model.

## Access-control behaviour

- Each child collection is filtered by `filters_allowed(Action.read, <child model>, current_user)`, so
  read access to a parent never grants read access to a child the caller is not authorised for.
- A parent with no accessible children is still returned, with an empty child list.
- The anonymous/public path and the Microsoft administrator/group short-circuits in `filters_allowed`
  (see [`backend/src/crud/access.py`](../../../backend/src/crud/access.py)) apply unchanged.
- `read` loads only direct children (one hierarchy level).

## Ordering

- A resource parent orders its children by the `ResourceHierarchy.order` column (the only hierarchy
  that carries an order); every other direction — identity parents and the child-to-parent direction —
  orders children by the related entity's own `id`. `IdentityHierarchy` has no `order` column.
- A collection read with no explicit `order_by` (for example the Socket.IO connect snapshot via
  `read()`) orders the top-level entities by their own `id`. Child ordering does not influence parent
  ordering. Callers that need a specific parent order must pass an explicit `order_by`.

## Scope

This behaviour is centralised in `BaseCRUD.read`, so it applies to every model with hierarchy children
(for example categories, module/section/topic, protected-resource chains, and identity groups), for
both REST and Socket.IO reads.
