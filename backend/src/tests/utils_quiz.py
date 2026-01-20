"""Test data for quiz-related resources (Question, Message, Numerical)."""

# Question test data
one_test_question = {
    "question": "What is the capital of France?",
    "language": "en",
}

many_test_questions = [
    {
        "question": "What is 2 + 2?",
        "language": "en",
    },
    {
        "question": "What is the largest planet in our solar system?",
        "language": "en",
    },
    {
        "question": "¿Cuál es la capital de España?",
        "language": "es",
    },
]

wrong_test_questions = [
    # Consider making mandatory, minimum length and contain '?' validations in the model
    # {
    #     "question": "",  # Empty question
    #     "language": "en",
    # },
    {
        "question": "What is the capital of France?",
        "language": "en-US",  # Invalid language code
    },
    {
        # Missing 'question' field
        "language": "en",
    },
    # Consider making mandatory - right now it has a default 'en'
    # {
    #     "question": "What is the capital of England?",
    #     # Missing 'language' field
    # },
    {
        "question": True,  # Invalid type, should be str
        "language": "en",
    },
    {
        "question": "What is the capital of Poland?",
        "language": 123,  # Invalid type
    },
]

question_update_data = {
    "question": "What is the capital of Germany?",
    "language": "de",
}

# Message (text answer) test data
one_test_message = {
    "content": "Paris",
    "language": "en",
}

many_test_messages = [
    {
        "content": "4",
        "language": "en",
    },
    {
        "content": "Jupiter",
        "language": "en",
    },
    {
        "content": "Madrid",
        "language": "es",
    },
]

message_update_data = {
    "content": "Berlin",
    "language": "de",
}

wrong_test_messages = [
    # {
    #     "content": "",  # Empty content
    #     "language": "en",
    # },
    {
        "content": "Paris",
        "language": "en-US",  # Invalid language code
    },
    {
        # Missing 'content' field
        "language": "en",
    },
]

# Numerical answer test data
one_test_numerical = {
    "value": 4.0,
    "tolerance": 0.1,
}

many_test_numericals = [
    {
        "value": 42.0,
        "tolerance": 0.5,
    },
    {
        "value": 3.14159,
        "tolerance": 0.001,
    },
    {
        "value": 100.0,
        "tolerance": None,  # Exact match required
    },
]

numerical_update_data = {
    "value": 5.0,
    "tolerance": 0.2,
}

wrong_test_numericals = [
    {
        "value": "not a number",  # Invalid type
        "tolerance": 0.1,
    },
    {
        "value": 4.0,
        "tolerance": "not a number",  # Invalid type
    },
    {
        # Missing 'value' field
        "tolerance": 0.1,
    },
]
