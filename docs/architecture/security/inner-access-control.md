# Inner access-control layer

## Purpose and boundary

The inner security layer controls access to first-party application entities after the outer security layer has admitted a request or event. It answers:

> May this caller perform this action on this resource?

The outer layer establishes a trusted caller context. The inner layer uses the internal user identifier and relevant Microsoft claims from that context, but it does not validate provider tokens. A caller must pass both layers. Public access is also subject to this rule: the outer guard must allow anonymous admission before an anonymous caller can use a public policy.

The implementation is centered on [`AccessPolicyCRUD`](../../../backend/src/crud/access.py), with the data model in [`models/access.py`](../../../backend/src/models/access.py). Application create/read/update/delete (CRUD) classes apply it through [`BaseCRUD`](../../../backend/src/crud/base.py).

## Access policies

An access policy grants one action on one resource to either an identity or the public:

| Field | Meaning |
| --- | --- |
| `resource_id` | The protected application entity. Identities can also be resources when access to the identity object itself is controlled. |
| `identity_id` | The user or group receiving the grant. It is absent for a public policy. |
| `action` | The highest action granted by this policy. |
| `public` | Marks a policy as available without an identity-specific grant. |

A policy is exactly one of:

- an identity policy: `identity_id` is set and `public` is false; or
- a public policy: `identity_id` is absent and `public` is true.

There can be at most one policy for an identity/resource pair and at most one public policy per resource. Policies are grants; the model has no explicit deny policy. When several grants apply, the strongest effective action wins.

## Actions

Actions form this order:

```text
own > write > connect > read
```

A stronger grant satisfies checks for every weaker action. Therefore:

| Granted action | Satisfies checks for |
| --- | --- |
| `read` | `read` |
| `connect` | `connect`, `read` |
| `write` | `write`, `connect`, `read` |
| `own` | `own`, `write`, `connect`, `read` |

In the generic CRUD path, reads require `read`, updates require `write`, and deletion requires `own`. Managing access policies also normally requires effective `own` access to the target resource. Resource-specific code may impose additional requirements; it must not weaken these checks.

## Identity inheritance

`IdentityHierarchy` relates a parent identity, such as a group, to a child identity, such as a user or subgroup. The edge's `inherit` flag controls permission propagation.

For an authenticated user, access evaluation starts with the user's identity and recursively walks **up** edges whose `inherit` value is true. A policy granted to any reached parent identity is therefore effective for the user.

```text
Group --(inherit=true)--> User
  |
  +-- policy: write Resource A

Result: User has write access to Resource A.
```

An edge with `inherit=false` still records the relationship but does not propagate access through that edge. Every edge in a multi-level path must have `inherit=true` for a grant at the top to reach the user.

## Resource inheritance

`ResourceHierarchy` relates a parent resource to a child resource. Its `inherit` flag independently controls whether the child receives permissions from the parent.

Access evaluation first finds resources with a matching direct, inherited-identity, or public grant. It then recursively walks **down** resource edges whose `inherit` value is true. A grant on a parent is consequently effective on every descendant reached through inheriting edges.

```text
Identity -- policy: read --> Folder
                              |
                         inherit=true
                              v
                           Document

Result: Identity can read both Folder and Document.
```

Resource inheritance does not copy policy rows. It computes effective access when data is queried, so changing a hierarchy edge changes which inherited grants apply. An `inherit=false` edge preserves the parent/child structure without propagating the parent's permissions.

Identity and resource inheritance compose. For example, a group policy on a parent resource reaches a user on a descendant resource only when the identity path from user to group and the resource path from parent to descendant both consist of `inherit=true` edges.

## Public sharing

Public sharing is represented by an `AccessPolicy` row with `public=true`, no `identity_id`, and an action. It is an action-scoped grant, not a property that makes every operation unrestricted. A public `read` policy permits reading; it does not permit writing or ownership operations.

For an authenticated caller, public policies participate in the normal effective-access calculation and propagate through resource edges marked `inherit=true`. For an anonymous caller, the current implementation matches only resources with a direct public policy; it does not propagate that policy to descendants. Code must not rely on anonymous resource inheritance unless that behavior is implemented and tested explicitly.

Public sharing affects only the inner layer. It does not make a guarded endpoint anonymous. The endpoint or event must explicitly admit anonymous callers, and all returned entities must still pass the access-policy filter.

## Effective-access evaluation

For a requested action and resource, the implementation evaluates access as follows:

1. Expand the requested action to the actions that satisfy it. For example, a `read` check accepts `read`, `connect`, `write`, or `own` grants.
2. For an authenticated non-administrator, collect the user's identity plus every inheriting ancestor identity.
3. Find base resources with a qualifying policy for one of those identities, the user directly, or the public.
4. Add descendants reachable from those base resources through `inherit=true` resource edges.
5. Allow only resources in that effective set.

For anonymous callers, evaluation uses direct public policies only. A caller with the Microsoft `Admin` role bypasses the normal resource filter. The implementation also contains narrow bootstrap exceptions for policy creation on a user's own identity object and for qualifying Microsoft group objects; these exceptions must remain narrow and must not be generalized into ordinary access grants.

Because policies only grant access, the effective result is the strongest applicable direct, identity-inherited, resource-inherited, or public action. There is no deny precedence to resolve.

## Enforcement and fail-closed behavior

The access filter is part of the database statement, rather than a post-query visibility check:

- collection and item reads select only entities with effective `read` access;
- updates select the target through a `write` filter;
- deletes select the target through an `own` filter;
- hierarchy and policy operations apply their own access-controlled queries; and
- related entities loaded through configured hierarchies are filtered independently.

Missing access is commonly exposed as an empty result or `404 Not Found`, depending on the CRUD operation, so callers cannot rely on distinguishing a missing resource from an inaccessible one. Unexpected access-evaluation errors fail closed.

New resource CRUD implementations must inherit from and preserve the established `BaseCRUD` access path. Direct database access from routers, Socket.IO namespaces, or jobs must not bypass this layer.

## Regression coverage

The inner layer already has substantial regression coverage:

- [protected-resource tests](../../../backend/src/routers/api/v1/tests/test_protected_resource.py) cover direct, child, and grandchild resource access; multi-level resource inheritance; missing policies; broken `inherit` paths; administrator access; relationship filtering; and hierarchy removal;
- [identity tests](../../../backend/src/routers/api/v1/tests/test_identities.py) cover direct group inheritance, indirect über-group/group/sub-group inheritance, missing membership, and an `inherit=false` boundary;
- [access CRUD tests](../../../backend/src/crud/tests/test_access_crud.py) cover policy validation and mutation, action selection, administrator behavior, hierarchy authorization, and owner/non-owner cases; and
- [access endpoint tests](../../../backend/src/routers/api/v1/tests/test_access.py) and Socket.IO tests cover the exposed policy, hierarchy, and real-time interfaces.

This is regression coverage to preserve, not a list of tests that must be recreated. Changes to policies, action ordering, hierarchy traversal, public behavior, administrator exceptions, or CRUD enforcement still change the inner security layer and require user consultation under the repository change boundary.

For an approved behavior change, extend the narrowest existing suite for the affected path. Add a new combination only when it is not already represented—for example, anonymous versus authenticated public inheritance, or inherited `write`/`own` behavior if that behavior changes. Verify the exposed REST or Socket.IO interface as well as the lower-level CRUD helper when the change affects that interface.
