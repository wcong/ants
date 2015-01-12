from ants.project import crawler
stats = crawler.stats

import warnings
from ants.exceptions import ScrapyDeprecationWarning
warnings.warn("Module `ants.stats` is deprecated, use `crawler.stats` attribute instead",
    ScrapyDeprecationWarning, stacklevel=2)
