# Recursive text and number resource plan

## Scope and decisions

This is an implementation plan, not a description of implemented interfaces.

The initial work is limited to:

1. Shared resource and identity hierarchy cycle prevention.
2. Parallel recursive `Text` and `Number` resources, their REST interfaces and
   Socket.IO namespaces, and optional presentation child collections.

The next presentation will use the new resources to evaluate them. Existing
presentations and frontend endpoints will not be migrated as part of this work.
Question, Message, Numerical, the protected-resource family, and the existing
group interfaces remain available. Remove legacy interfaces and models only
after their existing data and all consuming presentations and frontend endpoints
have been migrated.

Multiple parents are supported. There is no stored generation number or
type-defined maximum depth. Concurrency locking and concurrent cycle-creation
guarantees are explicitly out of scope. Audio, video, pictures, a generic media
framework, and an `internalText` interface are also out of scope.

Application-group consolidation is planned below, but is not part of the initial
implementation. Its frontend is currently a developer playground rather than an
end-user dependency; its existing data and authorization behavior still need to
be preserved.

## Resource model

Use the existing [model factory](../../../backend/src/models/base.py),
[BaseCRUD](../../../backend/src/crud/base.py), and
[ResourceHierarchy](../../../backend/src/models/access.py). Do not introduce a
parallel hierarchy table or a single-parent foreign key.

| Model | Attributes |
| --- | --- |
| `Text` | Required string `content`; nullable string `label`; nullable language code `language`; nullable encrypted string `confidential`; nullable fields default to null |
| `Number` | Required numeric `value`; nullable string `label`, defaulting to null; no language or tolerance field |

The proposed numeric representation is the existing Numerical model's
floating-point representation. Confirm a requirement for exact decimal arithmetic
before changing that representation; do not silently stringify values.

`confidential` preserves Message's existing behavior: plaintext in authorized
interface responses, encrypted at rest using the
[application encryption contract](../security/README.md#database-field-encryption).
It is not a separate field-level permission boundary. Public read access can
therefore expose its decrypted value.

Allow these resource edges:

```text
Presentation → Text | Number
Text         → Text | Number
Number       → Text | Number
```

Both resources can be created standalone by authenticated callers. Child
collections can be empty. Preserve Presentation's existing Question relationship
alongside its new Text and Number relationships.

### Labels for coded interactive elements

Labels are optional on both Text and Number, including resources with parents.
When present, a label must be non-empty and contain only lowercase ASCII letters,
digits, and hyphens: `^[a-z0-9-]+$`. Reject invalid values rather than silently
lowercasing or sanitizing them. An absent label is null.

A presentation can hard-code semantic labels such as `heading`, `closing`, or
`participant-count` to bind its interactive elements to database resources.
Labels may be publicly visible and must not contain secrets. They identify the
element's resource, not every live response submitted to it. Responses can remain
unlabeled and use resource and parent/child identifiers.

Labels must be unique among a parent's labeled Text and Number children, across
both types. Resolve a coded
binding by `(parent identifier, label)`, then retain the resolved resource
identifier for updates and subscriptions.

The rules are:

- Different parents can have different resources labeled `heading`.
- The same resource, with its row-level label unchanged, can be reused under
  multiple parents.
- A parent cannot have two different children labeled `heading`, even when one
  is Text and the other Number.
- Any number of unlabeled children are allowed.
- Linking a labeled child must check its new parent's labeled children.
- Changing a shared child's label must check every existing parent.
- Standalone labels need not be unique until the resource is attached.

A label is an addressable role, not a sorting key. A coded presentation can place
`heading` and `closing` in separate layout slots without consulting hierarchy
order. Hierarchy order still applies to consumers that render a generic sequence.

### Ordering

Use the existing `ResourceHierarchy.order` to arrange a parent's children,
including Text and Number together. Order belongs to the parent–child
relationship, so a shared child can occupy different positions under different
parents.

For example:

| Hierarchy order | Child |
| --- | --- |
| 1 | Text: “Participants” |
| 2 | Number: `42` |
| 3 | Text: “Thank you” |

When displaying a mixed sequence, the consumer uses each accessible child's
parent-edge order to combine the Text and Number collections. A presentation
using labels for fixed layout slots, or displaying the collections separately,
does not need to combine them. No new unified collection endpoint or media
abstraction is needed.

### Interactive question and responses

Hierarchy also represents relationships between interactive content, rather than
just the order in which siblings appear. For example:

```text
Presentation
└── Text: “What would you like to explore?” (label: topics-question)
    ├── Text: “Community gardens” (a participant's answer)
    │   ├── Text: “How could we get started?” (another participant's comment)
    │   └── Number: 3 (a vote count)
    └── Text: “Shared workshops” (another participant's answer)
```

The presentation code can resolve `topics-question` under its presentation and
use the resulting identifier to subscribe and attach answers. Answers are created
on the fly and need no labels; their identifiers identify them for later
interactions. A comment or a numeric vote count can be linked to an answer, and
further discussion can extend the hierarchy as needed. The presentation determines
what these resources mean; the hierarchy does not by itself implement voting or
enforce one vote per participant.

Reads load one level at a time, so retrieving comments or vote counts requires
reading the relevant answers as parents. Each edge can propagate permissions when
`inherit=true`; every returned resource is independently checked for read access.
Anonymous participants still require the appropriate direct public policies and
endpoint admission described below.

## Step 1: shared cycle prevention

### Invariant

Both hierarchies must be directed acyclic graphs. Before inserting
`parent → child`, reject:

- a direct self-link; or
- a link where the proposed parent is already reachable from the child.

Inspect all structural edges, including `inherit=false`. Permission inheritance
being disabled does not make a structural cycle acceptable.

### Enforcement

Implement the reachability check at the shared
[hierarchy CRUD creation boundary](../../../backend/src/crud/access.py), after
ordinary endpoint/row authorization and allowed-type checks, and before insertion.
REST hierarchy operations, Socket.IO linking, and child creation must use that
same boundary.

The reachability query must examine the complete relevant hierarchy rather than
an access-filtered fragment. Otherwise an inaccessible intermediate node could
hide a cycle. Return a generic conflict without disclosing the hidden path.

Use a recursive Common Table Expression (CTE) that deduplicates visited
identifiers, so the check also terminates if pre-existing data contains a cycle.
Retain direct self-link validation; a database self-link check constraint can
reinforce it through the normal schema migration workflow. Indirect-cycle
prevention is not supplied by that constraint.

Preserve unrelated authorization errors and established access checks. Ensure
cycle conflicts are logged and propagated explicitly rather than swallowed or
turned into success-shaped results. Inspect existing hierarchy data before
deployment; report existing cycles for deliberate correction, not automatic
deletion.

Do not add locks or concurrency machinery. This check prevents cycles against
the graph visible to the request, but simultaneous requests could still create a
cycle collectively. This limitation must remain explicit.

### Permission traversal remains independent

Preserve [effective permission evaluation](../security/inner-access-control.md):

- identity inheritance walks upward through `inherit=true` edges;
- resource inheritance walks downward through `inherit=true` edges;
- permissions can propagate through arbitrarily many generations;
- authenticated callers retain existing direct, public, inherited, and
  administrator behavior;
- ordinary anonymous read/update checks retain direct public-policy behavior.

Do not limit permission traversal to the content returned by a read.

The current [BaseCRUD.read](../../../backend/src/crud/base.py) separately loads
immediate declared hierarchy relationships with `selectinload`, applying
`filters_allowed(Action.read)` through `with_loader_criteria` to related rows.
It includes configured parent relationships as well as child relationships.
Recursive permission CTEs compute accessibility; they do not recursively fetch
content. See [collection child loading](../security/collection-child-loading.md).

## Step 2: parallel resource interfaces

### Backend integration

Add Text and Number to resource registration, model imports/forward-reference
rebuilding, allowed hierarchy types, CRUD registration, REST router mounting,
and Socket.IO namespace mounting. Reuse existing helpers and expose thin
resource-specific adapters rather than a new configurable endpoint framework.

Plan REST interfaces under `/api/v1/text` and `/api/v1/number`, with:

- collection and identifier reads;
- parent-filtered snapshots with existing include/sort options;
- standalone or parent-attached creation;
- updates and deletion.

Use explicit framework aliases for first-party query parameters such as
`parent-id` and `public-action`. Resource types must allow all three parent types
listed above without adding a route for every parent/child type combination.

Use `/text` and `/number` Socket.IO namespaces with the established read,
subscribe, submit, link, unlink, delete, share, and ordering mechanisms.

Follow [REST snapshots and incremental Socket.IO](../data-transfer/internal/rest-snapshot-incremental-socketio.md):
cursor headers, authorized subscriptions, parent-scoped replay, and mutation
notifications must continue to work. Snapshot-aware connections must not receive
an additional full collection transfer.

### Bounded relationship representations

Keep content responses one hierarchy level deep. Self-related and mutually
related models must not serialize the whole graph or recurse back through parent
references. Use shallow related-entity representations where necessary, retaining
identifier and attribute information and independent row-level filtering.

Verify this for collection reads as well as identifier reads: loading several
related top-level entities in one database session must not accidentally produce
deeper responses through shared in-memory instances.

### Admission and row permissions

Retain provider authentication and guards. Anonymous admission is an alternative
for approved operations, not a replacement for trusted caller identity.

| Operation | Admission and inner access requirements |
| --- | --- |
| Read, snapshot, subscribe | Anonymous admission allowed; enforce per-row `read` access |
| Standalone create | Authenticated; normal creator ownership |
| Parent-attached submission | Anonymous allowed only with an explicit public submission policy and adequate public `connect` permission on the parent; create an explicit resulting public policy on the new row |
| Update | Anonymous admission allowed; require direct public `write` or `own` on the target for anonymous callers |
| Link an existing child | Preserve `connect` on the parent and `own` on the child; anonymous admission does not remove either check |
| Delete, share, manage policies | Keep authenticated admission and established ownership checks |

The action order remains `own > write > connect > read`. No new action vocabulary
or deny-policy semantics are introduced.

Anonymous creation has no pre-existing child row to authorize. Check the parent's
public permission explicitly before the existing public-creation flow establishes
any temporary creator identity. Do not accidentally broaden that check through
authenticated inheritance on the temporary identity.

Reuse existing public-policy creation and validate requested actions before
persistence. Public read on a parent does not permit submissions. Anonymous
update must not change hierarchy or policy data through content fields.

Do not split Text into internal/external models now. A future protected interface
over the same data would not itself make a row internal: other interfaces would
still expose it when their admission rules and its public policies permit access.
Any future requirement for mandatory outer authentication must be enforced across
all interfaces accessing the affected rows.

### Focused validation

Run tests inside the dedicated test environment using existing tooling. Cover:

- self-links and indirect cycles in both hierarchy tables, including
  non-inheriting edges and inaccessible intermediate nodes;
- allowed shared-child/diamond graphs, with no false cycle rejection;
- same-type and cross-type Text/Number edges and Presentation children;
- effective permissions beyond the single fetched content level;
- inaccessible immediate relationships being omitted without hiding an
  accessible parent;
- bounded representations for both identifier and collection reads;
- nullable language, numeric validation, and confidential encryption/decryption,
  including related texts loaded from a Number or Presentation;
- optional labels and allowed characters, deterministic access-filtered label
  resolution, rejection of duplicate labeled siblings
  across both types, shared-child link/rename conflicts, and unlabeled responses;
- public read versus connect versus write, anonymous submission/update failures,
  authenticated standalone creation, and ownership-protected operations;
- snapshots, cursors, subscriptions, parent-scoped replay, and incremental events;
- multiple-parent ordering and deletion without deleting shared standalone
  children;
- preservation of existing quiz, presentation, protected-resource, and identity
  behavior.

Use exposed REST endpoints and Socket.IO events for their behavior, plus focused
shared-helper tests where needed. Do not introduce migration-specific tests for
ordinary autogenerated tables/constraints.

Leave models ready for the developer to generate the development migration using
the [existing migration workflow](../../postgres/README.md#schema-migration-workflow);
do not hand-author or pre-generate ordinary schema revisions.

## Step 3: build the next presentation

The developer builds the next presentation using the parallel Text/Number
interfaces, labeled interactive elements, and live submissions. Leave existing
presentations on their current interfaces.

## Step 4: evaluate the new presentation

Evaluate the new models' behavior and usability in that presentation, including
labels, nested responses, access policies, ordering, and real-time updates.
Use the results to decide whether adjustments are needed before migrating old
presentations. Steps 3 and 4 are separate from implementing steps 1 and 2.

## Later resource migration

Migrate existing presentations only after evaluation. Do not dual-write all
legacy resources.

Later migrations must preserve identifiers where feasible, hierarchy edges,
per-parent order, inheritance flags, policies, and relevant access-log/replay
history. Resolve type registration and compatibility references deliberately.
Confidential ciphertext must be decrypted and re-encrypted for its new row
location; copying Message ciphertext directly to Text violates associated-data
binding. Retain Numerical tolerance in the legacy model until that model is
retired; do not add it to Number.

## Step 5: application-group consolidation plan

Consolidate application-managed UeberGroup, Group, SubGroup, and SubSubGroup into:

```text
Group → Group | User
```

Use `IdentityHierarchy` and the same shared cycle-prevention mechanism. Preserve
upward identity permission inheritance, multiple parents, existing group
attributes, memberships, policies, and administrator exceptions. Resource and
identity hierarchies remain separate tables with different inheritance directions;
their shared structure does not mean merging them.

Keep provider-backed AzureGroup distinct. Its provider identity and integration
semantics are not merely another application-group nesting level.

### Group categories

Add a Group `category` using the same character constraints as Text and Number labels:
a non-empty value containing only lowercase ASCII letters, digits, and hyphens
(`^[a-z0-9-]+$`). Reject invalid values rather than silently normalizing them.

The frontend can use category values such as `ueber-group`, `sub-group`, or other
development-defined categories to choose icons and presentation behavior.
These categories replace separate generation-specific interface families; they
do not introduce new models, endpoints, or namespaces per category. Categories do not
determine hierarchy depth, membership, or authorization.

Unlike Text/Number labels that identify a specific child within a parent, Group
categories are reusable classifications. Multiple groups, including siblings,
can share a category; Text/Number's per-parent label uniqueness rule does not
apply. Keep `label` available as a separate future attribute if groups later need
addressable identifiers; do not add it in this step.
Confirm category optionality before implementing step 5; this decision does not
block steps 1 and 2.

Before changing the existing Group interface:

1. Review model/schema differences and frontend consumers; define bounded
   self-related Group representations.
2. Extend Group to accept Group children and User members, add the category and its
   validation, and preserve existing inheritance semantics.
3. Migrate legacy application-group rows and identifier types, retaining
   identifiers where feasible and all memberships and access policies.
4. Update playground frontend consumers to the single Group REST interface and
   namespace, including category-based icon selection and
   snapshot/subscription/replay behavior.
5. Retire legacy group endpoints and namespaces only after their consumers and
   data are migrated.

Existing test names can retain “über”, “sub”, and “sub-sub” as descriptions of
positions in the graph. Update their fixtures and interface calls to exercise
recursive Group rather than retaining separate models solely for test naming.
Preserve existing identity-inheritance regression scenarios and add the new
self-type/multiple-parent cases.

This consolidation does not gate evaluation of the next presentation.
