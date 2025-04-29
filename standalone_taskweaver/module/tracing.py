import functools
import inspect
from typing import Any, Callable, Dict, Optional

import tiktoken


def get_tracer():
    """
    Get the tracer.
    :return: The tracer.
    """
    return None


def tracing_decorator(func):
    """
    Tracing decorator.
    :param func: The function.
    :return: The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def tracing_decorator_non_class(func):
    """
    Tracing decorator for non-class functions.
    :param func: The function.
    :return: The decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


class Tracing:
    """
    Tracing is used to trace the execution of the code.
    """

    def __init__(self) -> None:
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def set_span_attribute(self, key: str, value: Any) -> None:
        """
        Set a span attribute.
        :param key: The key.
        :param value: The value.
        """
        pass

    def set_span_status(self, status: str, description: str) -> None:
        """
        Set the span status.
        :param status: The status.
        :param description: The description.
        """
        pass

    def set_span_exception(self, exception: Exception) -> None:
        """
        Set the span exception.
        :param exception: The exception.
        """
        pass

    def count_tokens(self, text: str) -> int:
        """
        Count the tokens in the text.
        :param text: The text.
        :return: The number of tokens.
        """
        return len(self.encoding.encode(text))

    def add_prompt_size(
        self,
        size: int,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Add the prompt size.
        :param size: The size.
        :param labels: The labels.
        """
        pass

