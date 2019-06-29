# VSCode still doesn't support namespace packages
# or am I doing something wrong?

from importlib_metadata import version

__version__ = version(__package__)
