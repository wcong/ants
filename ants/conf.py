# This module is kept for backwards compatibility, so users can import
# ants.conf.settings and get the settings they expect

import sys

if 'ants.cmdline' not in sys.modules:
    from ants.utils.project import get_project_settings
    settings = get_project_settings()

import warnings
from ants.exceptions import ScrapyDeprecationWarning
warnings.warn("Module `ants.conf` is deprecated, use `crawler.settings` attribute instead",
    ScrapyDeprecationWarning, stacklevel=2)
