import warnings
from ants.exceptions import ScrapyDeprecationWarning
warnings.warn("Module `ants.contrib_exp.djangoitem` is deprecated, use `ants.contrib.djangoitem` instead",
    ScrapyDeprecationWarning, stacklevel=2)

from ants.contrib.djangoitem import DjangoItem
