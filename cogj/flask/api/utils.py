from flask import request
import os


def get_request_arg_casei(find):
    for k in request.args:
        if k.lower() == find.lower():
            return request.args.get(k)
    return None


def get_env(k, d=None):
    if k not in os.environ:
        return d
    v = os.environ[k]
    return v


def is_dev():
    return get_env("ENVIRONMENT") == "development"


def merge_dicts(x, y, z=None):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    # https://stackoverflow.com/a/26853961

    a = x.copy()
    a.update(y)
    if z is not None:
        a.update(z)
    return a
