one_test_presentation = {
    "source": "https://example.com/presentation",
    "path": "/presentation/intro-to-fastapi",
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
        "source": "https://example.com/valid-source",
        "path": "presentation/missing-leading-slash",  # no leading slash → not a valid path
    },
    {
        "source": "https://example.com/valid-source",
        "path": "https://example.com/presentation/intro",  # absolute URL, not a relative path
    },
    {
        # Missing 'source' field
        "path": "/presentations/missing-source",
    },
    # { # That's ok: path is optional!
    #     "source": "",
    #     # Missing 'path' field
    # },
    # { # That's ok: extra field get's ignored, and path is optional!
    #     "source": "https://example.com/missing-path",
    #     "text": "Some text",  # Extra unexpected field
    # },
]

many_test_presentations = [
    {
        "source": "https://example.com/fastapi-basics",
        "path": "/presentation/fullstack-basics",
    },
    {
        "source": "https://example.com/advanced-fastapi",
        "path": "/presentation/advanced-fullstack",
    },
    {
        "source": "https://example.com/database-integration",
        "path": "/presentation/database-integration",
    },
    {
        "source": "https://example.com/rest-api-design",
        "path": "/presentation/rest-api-design",
    },
]

presentation_update_data = {
    "source": "https://example.com/updated-presentation",
    "path": "/presentation/updated-path",
}
