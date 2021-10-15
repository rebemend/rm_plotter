import json
import os
import sys

import logging
log = logging.getLogger(__name__)

""" Class for handling of configs

Currently only loading.

TODO: Saving? Overwrite?
"""

pkgPath = os.path.dirname(sys.modules["plotter"].__file__)+"/"


def load_config(path):
    log.debug(f"Loading config file {path}")
    with open(path, "r") as f:
        config = json.load(f)
        return config
