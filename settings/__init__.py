import importlib

from .common import *

mdl = importlib.import_module(f"settings.{ENV}")

if "__all__" in mdl.__dict__:
    names = mdl.__dict__["__all__"]
else:
    names = [x for x in mdl.__dict__ if not x.startswith("_")]

globals().update({k: getattr(mdl, k) for k in names})
