"""
Text Utilities
Provides normalization and formatting functions for text fields.

Key Principles:
- Storage: Always store subject/topic/subtopic in lowercase
- Query: Always query with lowercase
- Display: Format as Title Case for users
- Content: Question stems, options, and answers preserve original case
"""


def normalize_subject(subject: str) -> str:
    """
    Normalize subject for storage and queries.

    Args:
        subject: Subject name (e.g., "Math", "MATH", "math")

    Returns:
        Lowercase normalized subject (e.g., "math")
    """
    if not subject:
        return ""
    return subject.lower().strip()


def normalize_topic(topic: str) -> str:
    """
    Normalize topic for storage and queries.

    Args:
        topic: Topic name (e.g., "Multiplication", "MULTIPLICATION", "multiplication")

    Returns:
        Lowercase normalized topic (e.g., "multiplication")
    """
    if not topic:
        return ""
    return topic.lower().strip()


def normalize_subtopic(subtopic: str) -> str:
    """
    Normalize subtopic for storage and queries.

    Args:
        subtopic: Subtopic name (e.g., "Single-Digit Multiplication")

    Returns:
        Lowercase normalized subtopic (e.g., "single-digit multiplication")
    """
    if not subtopic:
        return ""
    return subtopic.lower().strip()


def to_display_case(text: str) -> str:
    """
    Format text for display to users (Title Case).

    Args:
        text: Normalized text (e.g., "single-digit multiplication")

    Returns:
        Title case text (e.g., "Single-Digit Multiplication")
    """
    if not text:
        return ""
    return text.strip().title()


def normalize_metadata(data: dict) -> dict:
    """
    Normalize all subject/topic/subtopic fields in a dictionary.
    Does NOT modify question content (stem, options, answers).

    Args:
        data: Dictionary with potential subject/topic/sub_topic/subtopic keys

    Returns:
        Dictionary with normalized metadata (modifies in place)
    """
    if "subject" in data:
        data["subject"] = normalize_subject(data["subject"])

    if "topic" in data:
        data["topic"] = normalize_topic(data["topic"])

    if "sub_topic" in data:
        data["sub_topic"] = normalize_subtopic(data["sub_topic"])

    if "subtopic" in data:
        data["subtopic"] = normalize_subtopic(data["subtopic"])

    return data
