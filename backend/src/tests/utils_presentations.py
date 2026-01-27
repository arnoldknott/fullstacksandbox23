one_test_presentation = {
    "source": "https://example.com/presentation",
    "path": "/presentations/intro-to-fastapi",
}

wrong_test_presentations = [
    {
        "source": 12345,  # Invalid type, should be str
        "path": None,
    },
    {
        "source": "https://example.com/valid-source",
        "path": 67890,  # Invalid type, should be str or None
    },
    {
        # Missing 'source' field
        "path": "/presentations/missing-source",
    },
    {
        "source": "",
        # Missing 'path' field
    },
    {
        "source": "https://example.com/missing-path",
        "text": "Some text",  # Extra unexpected field
    },
]

many_test_presentations = [
    {
        "source": "https://example.com/fastapi-basics",
        "path": "/presentations/fastapi-basics",
    },
    {
        "source": "https://example.com/advanced-fastapi",
        "path": "/presentations/advanced-fastapi",
    },
    {
        "source": "https://example.com/database-integration",
        "path": "/presentations/database-integration",
    },
    {
        "source": "https://example.com/rest-api-design",
        "path": "/presentations/rest-api-design",
    },
]

presentation_update_data = {
    "source": "https://example.com/updated-presentation",
    "path": "/presentations/updated-path",
}
