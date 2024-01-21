"""Defines utility functions for testing, for example test datasets and dependencies (for example a logged in user if required)."""
from uuid import uuid4

# user_test_input = {
#     "azure_user_id": UUID("12345678-1234-1234-1234-123456789012"),
#     "azure_tenant_id": UUID("12345678-1234-1234-1234-123456789012"),
# }

user_test_input = {
    "azure_user_id": "12345678-1234-1234-1234-123456789012",
    "azure_tenant_id": "12345678-1234-1234-1234-123456789012",
}

azure_home_tenant = str(uuid4())
user_test_inputs = [
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

# Mocks payload to detect scope api.write:
token_payload_scope_api_write = {
    "scp": "api.write",
}
token_payload_scope_api_read_write = {
    "scp": "api.read api.write",
}
token_payload_roles_user = {
    "roles": "User",
}
token_payload_roles_admin = {"roles": ["User", "Admin"]}

demo_resource_test_input = {
    "name": "Name of Test Resource",
    "description": "Some fancy description of my test resource.",
    "language": "en-US",
}

# demo_resource_test_inputs = [
#     {
#         "name": "Name of Test Resource",
#         "description": "Some fancy description of my test resource.",
#         "language": "en-US",
#         # "category_id": 2,
#     },
#     {
#         "name": "Another Test Resource's name",
#         "description": "The description of the second test resource.",
#         "language": "en-GB",
#     },
# ]

demo_resource_test_inputs = [
    {
        "name": "Name of Test Resource",
        "description": "Some fancy description of my test resource.",
        "language": "en-US",
        "category_id": 2,
    },
    {
        "name": "Another Test Resource's name",
        "description": "The description of the second test resource.",
        "language": "en-GB",
        "category_id": 1,
    },
    {
        "name": "A second cat 2 resource",
        "description": "category 2 is popular.",
        "language": "es-ES",
        "category_id": 2,
    },
    {
        "name": "Test resource without category",
        "description": "This resource is not assigned to a category.",
        "language": "en-GB",
    },
]

categories_test_inputs = [
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


tag_test_inputs = [
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
