from datetime import datetime
from pathlib import Path

import anndata as ad
import numpy as np
import toml


def get_paths(verbose: bool = False) -> dict:
    """
    Get custom paths from config.toml that is in the root directory.
    """

    # get path of this file
    root_path = Path(__file__).parent.parent
    data_root = root_path / "data"

    config_path = root_path / "config.toml"
    if config_path.exists():
        config = toml.load(config_path)
    else:
        config = {}

    config["package_root"] = root_path
    config["data_root"] = data_root
    config["merfish_metadata"] = data_root / "Nardone_2024_merfish_processing" / "metadata"   # /data/Nardone_2024_merfish_processing
    config["registered_output"] = data_root / "Nardone_2024_merfish_processing" / "registered"
    config["registered_scratch"] = root_path / "scratch" / "Nardone_2024_merfish_processing" / "registered"
    config["result"] = root_path / "results" / "merfish"
    if verbose:
        print(config)
    return config
