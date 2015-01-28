import warnings

from ants.utils.exceptions import ScrapyDeprecationWarning

warnings.warn("Module `ants.contrib_exp.djangoitem` is deprecated, use `ants.contrib.djangoitem` instead",
    ScrapyDeprecationWarning, stacklevel=2)

