from datetime import datetime
from pathlib import Path

import anndata as ad
import numpy as np
import toml


def _resolve_asset(data_root: Path, prefix: str) -> Path:
    """
    Resolve a data-asset mount directory by its prefix.

    Code Ocean appends a timestamp when a data asset is re-created
    (e.g. ``LCNE-...-from-R_2026-07-08_11-11-11``), so we match on the stable
    prefix rather than the full name. Prefers an exact match, otherwise picks
    the most recent (lexicographically last) prefix match.
    """
    exact = data_root / prefix
    if exact.exists():
        return exact
    matches = sorted(data_root.glob(f"{prefix}*"))
    if not matches:
        raise FileNotFoundError(
            f"No data asset matching '{prefix}*' found under {data_root}. "
            f"Check the prefix in config.toml and that the asset is attached "
            f"in .codeocean/datasets.json."
        )
    return matches[-1]


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

    # --- MERFISH data asset ---
    merfish_prefix = config.get("merfish_dataset", "Nardone_2024_merfish_processing")
    merfish_root = _resolve_asset(data_root, merfish_prefix)
    config["merfish_root"] = merfish_root
    config["merfish_metadata"] = merfish_root / "metadata"
    config["registered_output"] = merfish_root / "registered"
    config["registered_scratch"] = root_path / "scratch" / merfish_prefix / "registered"

    # --- transcriptomics data asset (snRNAseq + retroseq, exported from R) ---
    transcriptomics_prefix = config.get(
        "transcriptomics_dataset", "LCNE-transcriptomics-preprocessing-from-R"
    )
    transcriptomics_root = _resolve_asset(data_root, transcriptomics_prefix)
    config["transcriptomics_root"] = transcriptomics_root
    config["snRNAseq_h5ad"] = transcriptomics_root / "snRNAseq_LCNE.h5ad"
    config["retroseq_raw"] = transcriptomics_root / "retroseqdata_raw_from_R"

    config["result"] = root_path / "results" / "merfish"
    if verbose:
        print(config)
    return config
