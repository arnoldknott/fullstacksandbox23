one_test_presentation = {
    "source": "https://example.com/presentation",
    "path": "/presentation/intro-to-fastapi",
}

one_test_presentation_multi_segment_path = {
    "source": "https://example.com/presentation-multi-segment",
    "path": "/presentation/chapter-1/section-a/slide-3",
}

one_test_presentation_uuid_like_path = {
    "source": "https://example.com/presentation-uuid-like-path",
    "path": "/presentation/550e8400-e29b-41d4-a716-446655440000",
}

one_test_presentation_without_path = {
    "source": "https://example.com/presentation-without-path",
    "path": None,
}

wrong_test_presentations = [
    {
        "source": 12345,  # Invalid type, should be str
        "path": None,
    },
    # {
    #     "source": "https://example.com/valid-source",
    #     "path": 67890,  # Invalid type, should be str or None
    # },
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
    {
        "source": "https://example.com/first-no-path",
        "path": None,
    },
    {
        "source": "https://example.com/second-no-path",
        "path": None,
    },
    {
        "source": "https://example.com/empty-string",
        "path": "",
    },
    {
        "source": "https://example.com/second-empty-string",
        "path": "",
    },
]

presentation_update_data = {
    "source": "https://example.com/updated-presentation",
    "path": "/presentation/updated-path",
}
