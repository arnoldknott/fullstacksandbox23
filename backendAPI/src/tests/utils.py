"""Defines utility functions for testing, for example test datasets and dependencies (for example a logged in user if required)."""

from uuid import uuid4

user_id = "12345678-1234-1234-1234-123456789012"
user_id_nonexistent = "87654321-4321-4321-4321-210987654321"
one_test_user = {
    "azure_user_id": "12345678-1234-1234-1234-123456789012",
    "azure_tenant_id": "12345678-1234-1234-1234-123456789012",
}

azure_home_tenant = str(uuid4())
many_test_users = [
    {
        "azure_user_id": str(uuid4()),
        "azure_tenant_id": azure_home_tenant,
    },
    {
        "azure_user_id": str(uuid4()),
        "azure_tenant_id": azure_home_tenant,
    },
    {
        "azure_user_id": str(uuid4()),
        "azure_tenant_id": str(uuid4()),  # foreign tenant here.
    },
]
# TBD: add data for groups

# Mocks payload to detect scope api.write:
token_payload_user_id = {
    "oid": one_test_user["azure_user_id"],
}
token_payload_tenant_id = {
    "tid": one_test_user["azure_tenant_id"],
}
token_payload_scope_api_read = {
    "scp": "api.read",
}
token_payload_scope_api_write = {
    "scp": "api.write",
}
token_payload_scope_api_read_write = {
    "scp": "api.read api.write",
}
token_payload_roles_user = {
    "roles": ["User"],
}
token_payload_roles_admin = {
    "roles": ["Admin"],
}
token_payload_roles_admin_user = {
    "roles": ["Admin", "User"],
}
token_payload_roles_user_admin = {
    "roles": ["User", "Admin"],
}
token_payload_one_group = {
    "groups": ["12345678-1234-1234-1234-123456789012"],
}
token_payload_many_groups = {
    "groups": [str(uuid4()), str(uuid4()), str(uuid4())],
}

group_id1 = str(uuid4())
group_id2 = str(uuid4())
group_id3 = str(uuid4())
test_current_user = {
    "user_id": one_test_user["azure_user_id"],
    "roles": ["User"],
}

test_current_user_admin = {
    "user_id": one_test_user["azure_user_id"],
    "roles": ["Admin"],
}

test_current_user_admin_user = {
    "user_id": one_test_user["azure_user_id"],
    "roles": ["Admin", "User"],
}

test_current_user_with_one_group = {
    "user_id": one_test_user["azure_user_id"],
    "roles": ["User"],
    "groups": [group_id1],
}

test_current_user_with_many_groups = {
    "user_id": one_test_user["azure_user_id"],
    "roles": ["User"],
    "groups": [group_id1, group_id2, group_id3],
}

resource_id1 = str(uuid4())
resource_id2 = str(uuid4())
resource_id3 = str(uuid4())
resource_id4 = str(uuid4())
one_test_policy_read = {
    "identity_id": one_test_user["azure_user_id"],
    "identity_type": "User",
    "resource_id": resource_id1,
    "resource_type": "ProtectedResource",
    "action": "read",
}

one_test_policy_write = {
    "identity_id": one_test_user["azure_user_id"],
    "identity_type": "User",
    "resource_id": resource_id1,
    "resource_type": "ProtectedResource",
    "action": "write",
}

one_test_policy_own = {
    "identity_id": one_test_user["azure_user_id"],
    "identity_type": "User",
    "resource_id": resource_id1,
    "resource_type": "ProtectedResource",
    "action": "own",
}

# same as one_test_policy_own, but with different identity_id
one_test_policy_share = {
    "identity_id": str(uuid4()),
    "identity_type": "User",
    "resource_id": resource_id1,
    "resource_type": "ProtectedResource",
    "action": "own",
}

one_test_policy_public_read = {
    "resource_id": resource_id1,
    "resource_type": "ProtectedResource",
    "action": "read",
    "public": True,
}

many_test_policies = [
    {
        "identity_id": many_test_users[1]["azure_user_id"],
        "identity_type": "User",
        "resource_id": resource_id1,
        "resource_type": "ProtectedResource",
        "action": "read",
    },
    {
        "identity_id": one_test_user["azure_user_id"],
        "identity_type": "User",
        "resource_id": resource_id2,
        "resource_type": "ProtectedResource",
        "action": "own",
    },
    {
        "identity_id": many_test_users[0]["azure_user_id"],
        "identity_type": "User",
        "resource_id": resource_id2,
        "resource_type": "ProtectedResource",
        "action": "write",
    },
    {
        "identity_id": many_test_users[2]["azure_user_id"],
        "identity_type": "User",
        "resource_id": str(uuid4()),
        "resource_type": "ProtectedResource",
        "action": "own",
    },
    # effectively overrides the first policy with more rights (own > read)
    {
        "identity_id": many_test_users[1]["azure_user_id"],
        "identity_type": "User",
        "resource_id": resource_id1,
        "resource_type": "ProtectedResource",
        "action": "own",
    },
]


one_test_demo_resource = {
    "name": "Name of Test Resource",
    "description": "Some fancy description of my test resource.",
    "language": "en-US",
}

specific_test_category_id1 = str(uuid4())
specific_test_category_id2 = str(uuid4())
many_test_demo_resources = [
    {
        "name": "Name of Test Resource",
        "description": "Some fancy description of my test resource.",
        "language": "en-US",
        # "category_id": specific_test_category_id2,
    },
    {
        "name": "Another Test Resource's name",
        "description": "The description of the second test resource.",
        "language": "en-GB",
        # "category_id": specific_test_category_id1,
    },
    {
        "name": "A second cat 2 resource",
        "description": "category 2 is popular.",
        "language": "es-ES",
        # "category_id": specific_test_category_id2,
    },
    {
        "name": "Test resource without category",
        "description": "This resource is not assigned to a category.",
        "language": "en-GB",
    },
]

many_test_categories = [
    {
        "name": "Category 1",
        "description": "Some description for this category",
    },
    {
        "name": "Category 2",
        "description": "Another category's description",
    },
    {
        "name": "Lonely 3",
        "description": "Well, lonely because no demo resources are linked to it.",
    },
]


many_test_tags = [
    {
        "name": "One",
    },
    {
        "name": "Two",
    },
    {
        "name": "Three",
    },
    {
        "name": "FourMore",
    },
]

many_test_protected_resources = [
    {
        "name": "First Protected Resource",
        "description": "this one is secret and under access control.",
    },
    {
        "name": "Number 2 Protected Resource",
        "description": "Another secret resource - protected by access control.",
    },
    {
        "name": "One more protected resource",
        "description": "with all kinds of secret description text, that can only be accessed after passing access control.",
    },
    {
        "name": "And yet another protected resource",
        "description": "with all kinds of secret description text, that can only be accessed after passing access control.",
    },
]


many_test_public_resources = [
    {
        "comment": "Some random user wrote a public comment on our homepage, referring to some stuff somewhere. Nobody really knows how it was and what it was about.",
    },
    {
        "comment": "Another public comment, that is not really helpful, but at least it is public. So everyone can read it and it might trigger more opinions.",
    },
    {
        "comment": "A third public comment. That one is ways more helpful, as the author is actually referring to what's shown on the page..",
    },
    {
        "comment": "And one more. Whatever that is about. It's public, so it's here. Somebody wrote this as some point in time. Maybe it's helpful.",
    },
]
