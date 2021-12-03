#!/usr/bin/env python3
"""
Decorator Design Pattern Repeater
"""
import functools
from contextlib import ContextDecorator


def verbose(function):
    """Verbose function"""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        print("before function call")
        outcome = function(*args, **kwargs)
        print("after function call")
        return outcome
    return wrapper


def repeater(repeat=1):
    """Repeater function"""
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            for _ in range(repeat):
                val = function(*args, **kwargs)
            return val
        return wrapper
    return decorator


class verbose_context(ContextDecorator):
    """Verbose context class"""
    def __enter__(self):
        print('class: before function call')
        return self

    def __exit__(self, *exc):
        print('class: after function call')
        return False
