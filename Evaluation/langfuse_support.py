"""Shared Langfuse setup for Agent experiments."""

import os

from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler


def initialize_langfuse() -> Langfuse:
    """Validate environment variables and obtain the shared client."""
    required_variables = (
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_BASE_URL",
    )

    missing = [
        name
        for name in required_variables
        if not os.getenv(name, "").strip()
    ]

    if missing:
        raise ValueError(
            "Missing Langfuse environment variables: "
            + ", ".join(missing)
        )

    return get_client()


def create_langfuse_callback() -> CallbackHandler:
    """Create a callback for one Agent run."""
    return CallbackHandler()