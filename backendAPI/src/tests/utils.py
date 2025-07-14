"""Defines utility functions for testing, for example test datasets and dependencies (for example a logged in user if required)."""

from uuid import uuid4

user_id = "12345678-1234-1234-1234-123456789012"
user_id_nonexistent = "87654321-4321-4321-4321-210987654321"
# one_test_user = {
#     "azure_user_id": "12345678-1234-1234-1234-123456789012",
#     "azure_tenant_id": "12345678-1234-1234-1234-123456789012",
# }
# another_test_user = {
#     "azure_user_id": "1b2b3c4d-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
#     "azure_tenant_id": "12345678-1234-1234-1234-123456789012",
# }

azure_home_tenant = str(uuid4())
many_test_azure_users = [
    {
        "azure_user_id": "12345678-1234-1234-1234-123456789012",
        "azure_tenant_id": "12345678-1234-1234-1234-123456789012",
        "groups": [
            "12345678-1234-1234-1234-123456789012",
            "12a34b56-12ab-34cd-56ef-78ab90cd12ef",
            str(uuid4()),
        ],
    },
    {
        "azure_user_id": "1b2b3c4d-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
        "azure_tenant_id": "12345678-1234-1234-1234-123456789012",
        "groups": [
            "12345678-1234-1234-1234-123456789012",
            str(uuid4()),
            "12a34b56-12ab-34cd-56ef-78ab90cd12ef",
        ],
    },
    {
        "azure_user_id": str(uuid4()),
        "azure_tenant_id": azure_home_tenant,
        "groups": [str(uuid4()), str(uuid4())],
    },
    {"azure_user_id": str(uuid4()), "azure_tenant_id": azure_home_tenant, "groups": []},
    {
        "azure_user_id": str(uuid4()),
        "azure_tenant_id": str(uuid4()),  # foreign tenant here.
        "groups": [str(uuid4()), "12345678-1234-1234-1234-123456789012", str(uuid4())],
    },
]
# TBD: add data for groups

# Mocks payload to detect scope api.write:
token_payload_user_id = {
    "oid": many_test_azure_users[0]["azure_user_id"],
    "name": "Test User",
}
token_payload_another_user_id = {
    "oid": many_test_azure_users[1]["azure_user_id"],
    "name": "Another Test User",
}
token_payload_random_user_id = {
    "oid": many_test_azure_users[2]["azure_user_id"],
    "name": "Random Test User",
}
token_payload_tenant_id = {
    "tid": many_test_azure_users[0]["azure_tenant_id"],
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
token_payload_scope_socketio = {
    "scp": "socketio",
}
token_payload_scope_read_socketio = {
    "scp": "socketio api.read",
}
token_payload_scope_write_socketio = {
    "scp": "socketio api.write",
}
token_payload_scope_api_read_write_socketio = {
    "scp": "api.read api.write socketio",
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
token_payload_one_random_group = {
    "groups": [str(uuid4())],
}
token_payload_many_groups = {
    # "groups": [str(uuid4()), str(uuid4()), str(uuid4())],
    "groups": many_test_azure_users[0]["groups"],
}

token_user1_read = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read,
    **token_payload_roles_user,
}

token_user1_write = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_write,
    **token_payload_roles_user,
}

token_user1_read_write = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write,
    **token_payload_roles_user,
}

token_user1_socketio = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_socketio,
    **token_payload_roles_user,
}

token_user1_read_socketio = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_read_socketio,
    **token_payload_roles_user,
}

token_user1_write_socketio = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_write_socketio,
    **token_payload_roles_user,
}

token_user1_read_write_socketio = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write_socketio,
    **token_payload_roles_user,
}

token_user1_read_groups = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read,
    **token_payload_roles_user,
    **token_payload_many_groups,
}

token_user1_read_write_groups = {
    **token_payload_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write,
    **token_payload_roles_user,
    **token_payload_many_groups,
}

token_user2_read = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read,
    **token_payload_roles_user,
}

token_user2_write = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_write,
    **token_payload_roles_user,
}

token_user2_read_write = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write,
    **token_payload_roles_user,
}

token_user2_socketio = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_socketio,
    **token_payload_roles_user,
}

token_user2_read_socketio = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_read_socketio,
    **token_payload_roles_user,
}

token_user2_write_socketio = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_write_socketio,
    **token_payload_roles_user,
}

token_user2_read_write_socketio = {
    **token_payload_another_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write_socketio,
    **token_payload_roles_user,
}

token_admin = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_roles_admin,
}

token_admin_read = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read,
    **token_payload_roles_admin,
}

token_admin_write = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_write,
    **token_payload_roles_admin,
}

token_admin_read_write = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write,
    **token_payload_roles_admin,
}

token_admin_socketio = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_socketio,
    **token_payload_roles_admin,
}

token_admin_read_socketio = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_read_socketio,
    **token_payload_roles_admin,
}

token_admin_write_socketio = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_write_socketio,
    **token_payload_roles_admin,
}


token_admin_read_write_socketio = {
    **token_payload_random_user_id,
    **token_payload_tenant_id,
    **token_payload_scope_api_read_write_socketio,
    **token_payload_roles_admin,
}

# Sessions in cache for testing purposes

session_id_user1_read = uuid4()
session_id_user1_write = uuid4()
session_id_user1_read_write = uuid4()
session_id_user1_socketio = uuid4()
session_id_user1_read_socketio = uuid4()
session_id_user1_write_socketio = uuid4()
session_id_user1_read_write_socketio = uuid4()
session_id_user1_read_groups = uuid4()
session_id_user1_read_write_groups = uuid4()

session_id_user2_read = uuid4()
session_id_user2_write = uuid4()
session_id_user2_read_write = uuid4()
session_id_user2_socketio = uuid4()
session_id_user2_read_socketio = uuid4()
session_id_user2_write_socketio = uuid4()
session_id_user2_read_write_socketio = uuid4()

session_id_admin = uuid4()
session_id_admin_read = uuid4()
session_id_admin_write = uuid4()
session_id_admin_read_write = uuid4()
session_id_admin_socketio = uuid4()
session_id_admin_read_socketio = uuid4()
session_id_admin_write_socketio = uuid4()
session_id_admin_read_write_socketio = uuid4()

session_id_invalid_token1 = uuid4()
session_id_invalid_token2 = uuid4()

sessions = [
    {
        "session_id": session_id_user1_read,
        "token_payload": token_user1_read,
    },
    {
        "session_id": session_id_user1_write,
        "token_payload": token_user1_write,
    },
    {
        "session_id": session_id_user1_read_write,
        "token_payload": token_user1_read_write,
    },
    {
        "session_id": session_id_user1_socketio,
        "token_payload": token_user1_socketio,
    },
    {
        "session_id": session_id_user1_read_socketio,
        "token_payload": token_user1_read_socketio,
    },
    {
        "session_id": session_id_user1_write_socketio,
        "token_payload": token_user1_write_socketio,
    },
    {
        "session_id": session_id_user1_read_write_socketio,
        "token_payload": token_user1_read_write_socketio,
    },
    {
        "session_id": session_id_user1_read_groups,
        "token_payload": token_user1_read_groups,
    },
    {
        "session_id": session_id_user1_read_write_groups,
        "token_payload": token_user1_read_write_groups,
    },
    {
        "session_id": session_id_user2_read,
        "token_payload": token_user2_read,
    },
    {
        "session_id": session_id_user2_write,
        "token_payload": token_user2_write,
    },
    {
        "session_id": session_id_user2_read_write,
        "token_payload": token_user2_read_write,
    },
    {
        "session_id": session_id_user2_socketio,
        "token_payload": token_user2_socketio,
    },
    {
        "session_id": session_id_user2_read_socketio,
        "token_payload": token_user2_read_socketio,
    },
    {
        "session_id": session_id_user2_write_socketio,
        "token_payload": token_user2_write_socketio,
    },
    {
        "session_id": session_id_user2_read_write_socketio,
        "token_payload": token_user2_read_write_socketio,
    },
    {"session_id": session_id_admin_read, "token_payload": token_admin_read},
    {"session_id": session_id_admin_write, "token_payload": token_admin_write},
    {
        "session_id": session_id_admin_read_write,
        "token_payload": token_admin_read_write,
    },
    {"session_id": session_id_admin_socketio, "token_payload": token_admin_socketio},
    {
        "session_id": session_id_admin_read_socketio,
        "token_payload": token_admin_read_socketio,
    },
    {
        "session_id": session_id_admin_write_socketio,
        "token_payload": token_admin_write_socketio,
    },
    {
        "session_id": session_id_admin_read_write_socketio,
        "token_payload": token_admin_read_write_socketio,
    },
    {
        "session_id": session_id_invalid_token1,
        "token_payload": {"invalid_token": "This is an invalid token"},
    },
    {
        "session_id": session_id_invalid_token2,
        "token_payload": {"invalid_token": "This is another invalid token"},
    },
]

# Test identity IDs and user data for testing purposes

identity_id_admin = str(uuid4())
identity_id_user1 = str(uuid4())
identity_id_user2 = str(uuid4())
identity_id_user3 = str(uuid4())
identity_id_group1 = str(uuid4())
identity_id_group2 = str(uuid4())
identity_id_group3 = str(uuid4())
identity_id_subgroup1 = str(uuid4())
identity_id_subgroup2 = str(uuid4())
identity_id_subgroup3 = str(uuid4())
identity_id_subsubgroup1 = str(uuid4())
identity_id_subsubgroup2 = str(uuid4())
identity_id_subsubgroup3 = str(uuid4())
identity_id_subsubgroup4 = str(uuid4())
identity_id_subsubgroup5 = str(uuid4())


many_identity_ids = [
    identity_id_admin,
    identity_id_user1,
    identity_id_user2,
    identity_id_user3,
    identity_id_group1,
    identity_id_group2,
    identity_id_group3,
    identity_id_subgroup1,
    identity_id_subgroup2,
    identity_id_subgroup3,
    identity_id_subsubgroup1,
    identity_id_subsubgroup2,
    identity_id_subsubgroup3,
    identity_id_subsubgroup4,
    identity_id_subsubgroup5,
]

azure_group_id1 = str(uuid4())
azure_group_id2 = str(uuid4())
azure_group_id3 = str(uuid4())
azure_group_id4 = str(uuid4())

many_azure_group_ids = [
    azure_group_id1,
    azure_group_id2,
    azure_group_id3,
    azure_group_id4,
]

current_user_data_admin = {
    "user_id": identity_id_admin,
    "azure_token_roles": ["Admin"],
}
current_user_data_user1 = {
    "user_id": identity_id_user1,
    "azure_token_roles": ["User"],
}
current_user_data_user2 = {
    "user_id": identity_id_user2,
    "azure_token_roles": ["User"],
}
current_user_data_user3 = {
    "user_id": identity_id_user3,
    "azure_token_roles": ["User"],
    "azure_token_groups": [str(uuid4()), str(uuid4())],
}

many_current_users_data = [
    current_user_data_admin,
    current_user_data_user1,
    current_user_data_user2,
    current_user_data_user3,
]
# group_id1 = str(uuid4())
# group_id2 = str(uuid4())
# group_id3 = str(uuid4())
# test_current_user = {
#     "user_id": many_test_azure_users[0]["azure_user_id"],
#     "roles": ["User"],
# }

# test_current_user_admin = {
#     "user_id": many_test_azure_users[0]["azure_user_id"],
#     "roles": ["Admin"],
# }

# test_current_user_admin_user = {
#     "user_id": many_test_azure_users[0]["azure_user_id"],
#     "roles": ["Admin", "User"],
# }

# test_current_user_with_one_group = {
#     "user_id": many_test_azure_users[0]["azure_user_id"],
#     "roles": ["User"],
#     "groups": [group_id1],
# }

# test_current_user_with_many_groups = {
#     "user_id": many_test_azure_users[0]["azure_user_id"],
#     "roles": ["User"],
#     "groups": [group_id1, group_id2, group_id3],
# }

many_test_ueber_groups = [
    {
        "name": "Ueber Group 1",
        "description": "The first Ueber Group.",
    },
    {
        "name": "Über Group 2",
        "description": "The second Über Group.",
    },
    {
        "name": "3rd Ueber Group",
        "description": "The third Ueber Group.",
    },
]

many_test_groups = [
    {
        "name": "Group 1",
        "description": "The first Group.",
    },
    {
        "name": "2nd Group",
        "description": "The second Group.",
    },
    {
        "name": "Third Group",
        "description": "The third Group.",
    },
    {
        "name": "Group 4",
        "description": "The fourth Group.",
    },
]

many_test_sub_groups = [
    {
        "name": "Sub Group 1",
        "description": "The first Sub Group.",
    },
    {
        "name": "2nd Sub Group",
        "description": "The second Sub Group.",
    },
    {
        "name": "Third Sub Group",
        "description": "The third Sub Group.",
    },
    {
        "name": "Sub Group 4",
        "description": "The fourth Sub Group.",
    },
    {
        "name": "Sub Group 5",
        "description": "The fifth Sub Group.",
    },
]

many_test_sub_sub_groups = [
    {
        "name": "Sub Sub Group 1",
        "description": "The first Sub Sub Group.",
    },
    {
        "name": "2nd Sub Sub Group",
        "description": "The second Sub Sub Group.",
    },
    {
        "name": "Third Sub Sub Group",
        "description": "The third Sub Sub Group.",
    },
    {
        "name": "Sub Sub Group 4",
        "description": "The fourth Sub Sub Group.",
    },
    {
        "name": "Sub Sub Group 5",
        "description": "The fifth Sub Sub Group.",
    },
    {
        "name": "Sub Sub Group 6",
        "description": "The sixth Sub Sub Group.",
    },
]


# for testing the connection between session and cache:
azure_oid1 = str(uuid4())
azure_oid2 = str(uuid4())
azure_oid3 = str(uuid4())
azure_user_account_1 = {
    "homeAccountId": f"{azure_oid1}.{azure_home_tenant}",
    "username": "user1@example.com",
    "environment": "login.microsoftonline.com",
    "tenantId": azure_home_tenant,
    "localAccountId": azure_oid1,
    "authorityType": "MSSTS",
}

azure_user_account_2 = {
    "homeAccountId": f"{azure_oid2}.{azure_home_tenant}",
    "username": "user2@example.com",
    "environment": "login.microsoftonline.com",
    "tenantId": azure_home_tenant,
    "localAccountId": azure_oid2,
    "authorityType": "MSSTS",
}

azure_foreign_tenant_id = str(uuid4())
azure_user_account_3 = {
    "homeAccountId": f"{azure_oid3}.{azure_foreign_tenant_id}",
    "username": "user3@example.com",
    "environment": "login.microsoftonline.com",
    "tenantId": azure_foreign_tenant_id,
    "localAccountId": azure_oid2,
    "authorityType": "MSSTS",
}

many_azure_user_accounts = [
    azure_user_account_1,
    azure_user_account_2,
    azure_user_account_3,
]

resource_id1 = str(uuid4())
resource_id2 = str(uuid4())
resource_id3 = str(uuid4())
resource_id4 = str(uuid4())
resource_id5 = str(uuid4())
resource_id6 = str(uuid4())
resource_id7 = str(uuid4())
resource_id8 = str(uuid4())
resource_id9 = str(uuid4())
resource_id10 = str(uuid4())


many_resource_ids = [
    resource_id1,
    resource_id2,
    resource_id3,
    resource_id4,
    resource_id5,
    resource_id6,
    resource_id7,
    resource_id8,
    resource_id9,
    resource_id10,
]


many_entity_ids = many_resource_ids + many_identity_ids + many_azure_group_ids


many_entity_type_links = [
    {
        "id": resource_id1,
        "type": "DemoResource",
    },
    {
        "id": resource_id2,
        "type": "DemoResource",
    },
    {
        "id": resource_id3,
        "type": "ProtectedResource",
    },
    {
        "id": resource_id4,
        "type": "Category",
    },
    {
        "id": resource_id5,
        "type": "Category",
    },
    {
        "id": resource_id6,
        "type": "Tag",
    },
    {
        "id": resource_id7,
        "type": "Tag",
    },
    {
        "id": resource_id8,
        "type": "ProtectedResource",
    },
    {
        "id": resource_id9,
        "type": "DemoResource",
    },
    {
        "id": resource_id10,
        "type": "Tag",
    },
    {
        "id": identity_id_user1,
        "type": "User",
    },
    {
        "id": identity_id_group1,
        "type": "Group",
    },
    {
        "id": identity_id_user3,
        "type": "User",
    },
    {
        "id": identity_id_group2,
        "type": "Group",
    },
    {
        "id": identity_id_subgroup1,
        "type": "SubGroup",
    },
    {
        "id": identity_id_subgroup2,
        "type": "SubGroup",
    },
    {
        "id": identity_id_subsubgroup1,
        "type": "SubSubGroup",
    },
    {
        "id": identity_id_subgroup3,
        "type": "SubGroup",
    },
    {
        "id": identity_id_subsubgroup2,
        "type": "SubSubGroup",
    },
    {
        "id": identity_id_subsubgroup3,
        "type": "SubSubGroup",
    },
    {
        "id": azure_group_id1,
        "type": "AzureGroup",
    },
    {
        "id": azure_group_id2,
        "type": "AzureGroup",
    },
    {
        "id": identity_id_group3,
        "type": "Group",
    },
    {
        "id": azure_group_id3,
        "type": "AzureGroup",
    },
    {
        "id": azure_group_id4,
        "type": "AzureGroup",
    },
]

# Note: it's not the azure_user_id that get's stored in the database, but the user_id!
one_test_policy_read = {
    "identity_id": identity_id_user1,
    "resource_id": resource_id3,  # used to be 1
    "action": "read",
}

one_test_policy_write = {
    "identity_id": identity_id_user1,
    "resource_id": resource_id1,
    "action": "write",
}

one_test_policy_own = {
    "identity_id": identity_id_user1,
    "resource_id": resource_id5,  # used to be 1
    "action": "own",
}

# same as one_test_policy_own, but with different identity_id
one_test_policy_share = {
    "identity_id": identity_id_user3,
    "resource_id": resource_id5,  # used to be 1
    "action": "own",
}

one_test_policy_public_read = {
    "resource_id": resource_id1,
    "action": "read",
    "public": True,
}

many_test_policies = [
    {
        "identity_id": identity_id_user2,
        "resource_id": resource_id1,
        "action": "own",
    },
    {
        "identity_id": identity_id_user1,
        "resource_id": resource_id2,
        "action": "own",
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id2,
        "action": "write",
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id3,
        "action": "own",
    },
    # used to effectively override the first policy with more rights (own > read)
    {
        "identity_id": identity_id_user2,
        "resource_id": resource_id4,  # used to be 1
        "action": "own",
    },
    one_test_policy_write,
    one_test_policy_read,
    one_test_policy_own,
    one_test_policy_share,
    one_test_policy_public_read,
]

many_test_access_logs = [
    {
        "identity_id": identity_id_user1,
        "resource_id": resource_id1,
        "action": "own",
        "status_code": 201,
    },
    {
        "identity_id": identity_id_user1,
        "resource_id": resource_id2,
        "action": "own",
        "status_code": 201,
    },
    {
        "identity_id": identity_id_user1,
        "resource_id": resource_id1,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id2,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id3,
        "action": "own",
        "status_code": 201,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id3,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id2,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id2,
        "action": "read",
        "status_code": 200,
    },
    {  # admin write access
        "identity_id": identity_id_admin,
        "resource_id": resource_id3,
        "action": "write",
        "status_code": 200,
    },
    {  # public read access
        "resource_id": resource_id1,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user1,
        "resource_id": resource_id2,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id3,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user2,
        "resource_id": resource_id1,
        "action": "write",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user1,
        "resource_id": resource_id2,
        "action": "write",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id3,
        "action": "read",
        "status_code": 200,
    },
    {
        "identity_id": identity_id_user3,
        "resource_id": resource_id3,
        "action": "write",
        "status_code": 200,
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
    },
    {
        "name": "Another Test Resource's name",
        "description": "The description of the second test resource.",
        "language": "en-GB",
    },
    {
        "name": "A second cat 2 resource",
        "description": "category 2 is popular.",
        "language": "es-ES",
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

child_resource_id1 = str(uuid4())
child_resource_id2 = str(uuid4())
child_resource_id3 = str(uuid4())
child_resource_id4 = str(uuid4())
child_resource_id5 = str(uuid4())
child_resource_id6 = str(uuid4())
child_resource_id7 = str(uuid4())
child_resource_id8 = str(uuid4())
child_resource_id9 = str(uuid4())
child_resource_id10 = str(uuid4())

many_test_child_resource_entities = [
    {
        "id": child_resource_id1,
        "type": "ProtectedChild",
    },
    {
        "id": child_resource_id2,
        "type": "ProtectedChild",
    },
    {
        "id": child_resource_id3,
        "type": "ProtectedGrandChild",
    },
    {
        "id": child_resource_id4,
        "type": "ProtectedGrandChild",
    },
    {
        "id": child_resource_id5,
        "type": "ProtectedGrandChild",
    },
    {
        "id": child_resource_id6,
        "type": "ProtectedChild",
    },
    {
        "id": child_resource_id7,
        "type": "ProtectedChild",
    },
    {
        "id": child_resource_id8,
        "type": "ProtectedGrandChild",
    },
    {
        "id": child_resource_id9,
        "type": "ProtectedChild",
    },
    {
        "id": child_resource_id10,
        "type": "ProtectedGrandChild",
    },
]

child_identity_id1 = str(uuid4())
child_identity_id2 = str(uuid4())
child_identity_id3 = str(uuid4())
child_identity_id4 = str(uuid4())
child_identity_id5 = str(uuid4())
child_identity_id6 = str(uuid4())
child_identity_id7 = str(uuid4())
child_identity_id8 = str(uuid4())
child_identity_id9 = str(uuid4())

# TBD: consider linking to many_entity_type_links - there are plenty of identities there already!
many_test_child_identities = [
    {
        "id": child_identity_id1,
        "type": "User",
    },
    {
        "id": child_identity_id2,
        "type": "Group",
    },
    {
        "id": child_identity_id3,
        "type": "Group",
    },
    {
        "id": child_identity_id4,
        "type": "User",
    },
    {
        "id": child_identity_id5,
        "type": "SubGroup",
    },
    {
        "id": child_identity_id6,
        "type": "SubSubGroup",
    },
    {
        "id": child_identity_id7,
        "type": "AzureGroup",
    },
    {
        "id": child_identity_id8,
        "type": "User",
    },
    {
        "id": child_identity_id9,
        "type": "SubGroup",
    },
]

many_test_protected_child_resources = [
    {
        "title": "First Protected Child",
    },
    {
        "title": "Number 2 Protected Child",
    },
    {
        "title": "One more protected child",
    },
    {
        "title": "And yet another protected child",
    },
    {
        "title": "For the fun of it: one more protected child",
    },
    {
        "title": "As we are on it - let's add another child.",
    },
]

many_test_protected_grandchild_resources = [
    {
        "text": "First Protected Grand Child",
    },
    {
        "text": "Number 2 Protected Grand Child",
    },
    {
        "text": "One more protected grand child",
    },
    {
        "text": "And yet another protected grand child",
    },
    {
        "text": "For the fun of it: one more protected grand child",
    },
    {
        "text": "As we are on it - let's add another grand child.",
    },
    {
        "text": "And another one Grand Child protected Resource.",
    },
    {
        "text": "And one more protected grand child - juhuuu 92304u2342.",
    },
    {
        "text": "And yet another protected grand child - 234234234.",
    },
    {
        "text": "For the fun of it: one more protected grand child - 234234234.",
    },
]

# TBD: configure the family of protected resources with parent-child relationships in three generations with AccessPolicies!
