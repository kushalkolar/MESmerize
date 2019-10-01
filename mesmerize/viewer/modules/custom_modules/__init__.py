import os
import glob
import importlib.util

dirname = os.path.dirname(__file__)
fname = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [os.path.basename(f)[:-3] for f in fname if os.path.isfile(f) and not f.endswith('__init__.py')]

for m in __all__:
    spec = importlib.util.spec_from_file_location(m, )

