# EntityContainer guidance

Applies to files in this folder, especially:
- entityContainer.svelte.ts
- entityContainer.svelte.test.ts

Also follow the parent guidance in ../../AGENTS.md.

## Intent

EntityContainer is a reactive state container for:
- entities and pendingEntities
- identities
- metadata: accessPolicies, accessRights, hierarchies
- selections as slim id-only subsets

Selections must stay id-only and must not store full objects.

## Core invariants

- selections is a record of selectionName -> string[] ids.
- A selection may represent entity ids or identity ids depending on the creator method.
- addSelection throws if name already exists.
- removeSelection, addToSelection, removeFromSelection throw if name does not exist.
- getSelectedEntities(name?) returns:
  - all entities when name is missing
  - entities matching ids in selections[name] when name is provided
- getSelectedIdentities(name?) follows the same behavior for identities.

## Reactive behavior

- Selection-producing helpers must remain reactive through Svelte rune effects.
- Assignments to selections should replace arrays or record entries in a way that preserves update propagation.
- Avoid introducing non-reactive caches that can desync from entities, identities, or metadata.

## Helper method contract

- createReactiveSelection is the generic helper for entity-based derived selections.
- createFilteredEntitySelection, createAllLinkedSelection, createUserHasSpecificAccessRightSelection, and createAccessPolicyResourceSelection should preserve this pattern and return derived selected entities.
- createAccessPolicyIdentitySelection is identity-based and returns derived selected identities; keep this distinction explicit.
- fromOtherSelection means filter from that existing selection; undefined means filter from the full source collection.

## Safety and consistency rules

- Keep id semantics explicit: entity id vs identity id.
- Keep method naming aligned with return type: Entity vs Identity.
- Keep EntityContainerInterface signatures in sync with implementation whenever methods change.
- Preserve SocketIO compatibility because SocketIO extends EntityContainer.

## Test expectations

When changing selection logic, update or add tests in entityContainer.svelte.test.ts for:
- happy path behavior
- error conditions for missing or duplicate selections
- reactive helper behavior for each specialized selection creator
- identity-based selection behavior separately from entity-based selection behavior
- edge cases with empty metadata maps and missing optional relations
