"""Defines utility functions for testing, for example test datasets and dependencies (for example a logged in user if required)."""

demo_resource_test_input = {
    "name": "Name of Test Resource",
    "description": "Some fancy description of my test resource.",
    "language": "en-US",
}

demo_resource_test_inputs = [
    {
        "name": "Name of Test Resource",
        "description": "Some fancy description of my test resource.",
        "language": "en-US",
        # "category_id": 2,
    },
    {
        "name": "Another Test Resource's name",
        "description": "The description of the second test resource.",
        "language": "en-GB",
    },
]

demo_resource_test_inputs_with_category = [
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

demo_categories_test_inputs = [
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
