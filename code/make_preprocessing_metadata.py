#!/usr/bin/env python
"""Generate AIND-standard metadata for the LCNE-transcriptomics-preprocessing data asset.

The data asset ``LCNE-transcriptomics-preprocessing_2026-07-08_16-23-00`` (attached to
this capsule under ``/data``) is *scientist-derived data*: the output of a prior
preprocessing step (raw -> preprocessed), not raw experimental data. It bundles the
preprocessed inputs for the three modalities the manuscript analysis consumes --
``snRNAseq/`` (batch-corrected single-nucleus matrices, with and without the MERFISH gene
panel), ``merfish/`` (spatial matrix), and ``retroseq/`` (filtered retro-seq matrix). Per
AIND publication standards, derived data that contributes to published results must carry
``data_description`` and ``processing`` metadata before transfer to the open-data bucket.

Provenance / classification
    The preprocessing pipeline pools cells across many donor mice and across modalities,
    so this is an *aggregation across subjects*: no subject/procedures metadata is
    inherited, and the new metadata consists of ``data_description`` + ``processing`` only
    (no full ``Metadata`` wrapper, no DocDB lookup). This mirrors ``make_mmidas_metadata.py``.

    The preprocessing itself was run in the companion repo/capsule
    ``LCNE_transcriptomics_preprocessing`` (see README), not in this analysis capsule; the
    preprocessing notebooks are not present here, only their outputs are stored in the asset.
    The raw snRNAseq/MERFISH/retro-seq inputs are NOT mounted here either -- that is
    expected, since source_data/input_data record lineage rather than runtime mounts.

Metadata only (no data staging)
    This script writes ONLY the two metadata JSON files; it does NOT copy the ~1.3 GB of
    data files. When creating the shareable/publishable asset, combine these JSON files
    with the existing preprocessing data (data + metadata together) into one new asset.

Running
    python scratch/make_preprocessing_metadata.py
    -> writes data_description.json and processing.json to /results/<asset_name>/ (on Code
       Ocean) or to <repo>/metadata/<asset_name>/ (locally).

    Both files validate on write; a clean run means the metadata is well-formed.

Provenance for this asset was read from the Code Ocean computation record (capsule
"LCNE_transcriptomics_preprocessing", computation id e2681863-2d11-47b3-a16c-a871f768324f,
Code Version bb6b538, run script code/run, input data listed below), so PREPROC_COMMIT_HASH
and SOURCE_RAW_ASSET_IDS are filled in from it.

Already valid as written. RUN_START / RUN_END default to the asset creation time -- a single
approximate run date, which the AIND guide accepts (start_date_time is the only schema-
required date; end_date_time is optional). Set exact run times only if you have them.

TODO before the aind-open-data transfer / publication:
    * FUNDING grant_number  -- grant number(s) to cite.
"""

import os
from datetime import datetime, timezone

import aind_data_schema.core.data_description as ds
import aind_data_schema.core.processing as ps
from aind_data_schema_models.modalities import Modality

# ============================ EDIT THESE ============================
ASSET_LABEL = "LCNE-transcriptomics-preprocessing"
# creation_time = the asset's generation time, taken from its dated folder suffix
# (LCNE-transcriptomics-preprocessing_2026-07-08_16-23-00). tz-aware datetime required.
CREATION_TIME = datetime(2026, 7, 8, 16, 23, 0, tzinfo=timezone.utc)

# start_date_time is the only schema-required date (end_date_time is optional); the guide
# accepts a single approximate run date when exact times aren't known. Both default to
# CREATION_TIME here -- valid as-is; set exact times only if you have them.
RUN_START = CREATION_TIME  # optional: set exact preprocessing start time if known
RUN_END = CREATION_TIME    # optional: set exact end time if known (schema-optional field)

INVESTIGATOR = "Shuonan Chen"
# project_name pattern forbids underscores, so the capsule's "LCNE_transcriptomics"
# is recorded here with a dash.
PROJECT_NAME = "LCNE-transcriptomics"

# The preprocessing pipeline is the Code Ocean capsule "LCNE_transcriptomics_preprocessing",
# confirmed as the source of this asset from its computation provenance (computation id
# e2681863-2d11-47b3-a16c-a871f768324f, run script code/run). The capsule id below is from
# the earlier 07-10 asset's buildLog for the same-named capsule; a release-capsule url is
# accepted by the AIND guide in place of a GitHub url.
PREPROC_URL = "https://codeocean.allenneuraldynamics.org/capsule/fcaf3e8d-32be-4cc6-8b76-b5480d269fb5"
# Code Version from the computation provenance (git commit of the preprocessing capsule).
PREPROC_VERSION = None            # using commit_hash below instead
PREPROC_COMMIT_HASH = "bb6b538"   # Code Version from the computation provenance

# Input data assets attached to the preprocessing run, from the computation provenance.
# Listed by name (preferred by the AIND guide). The two upstream inputs are:
#   * Nardone_2024_merfish_processing_v2 -- external MERFISH processing (Nardone 2024)
#   * LCNE-transcriptomics-preprocessing-from-R_2026-07-08_11-11-11 -- upstream R-based
#     preprocessing output (Code Ocean asset id 915f30e7-324d-4ed5-a520-5509a6e54f87)
SOURCE_RAW_ASSET_IDS = [
    "Nardone_2024_merfish_processing_v2",
    "LCNE-transcriptomics-preprocessing-from-R_2026-07-08_11-11-11",
]

# Funding is required by the schema (>=1 entry). Grant number omitted for now;
# add the grant number(s) before the aind-open-data transfer.
FUNDING = [ds.Funding(funder=ds.Organization.AIND, grant_number=None)]  # TODO: grant_number
# ===========================================================================


def _on_code_ocean():
    return os.path.exists("/code") and os.path.exists("/data") and os.path.exists("/results")


def _base_output_dir():
    """/results on Code Ocean, else <repo>/metadata."""
    if _on_code_ocean():
        return "/results"
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(repo_root, "metadata")


def build_processing():
    """Processing metadata: one combined PROCESSING DataProcess for the whole run."""
    code = ps.Code(
        name="LCNE_transcriptomics_preprocessing",
        url=PREPROC_URL,
        version=PREPROC_VERSION,
        commit_hash=PREPROC_COMMIT_HASH,
        input_data=[ps.DataAsset(name=a) for a in SOURCE_RAW_ASSET_IDS],
    )
    data_process = ps.DataProcess(
        # No "preprocessing"/"batch-correction" operation exists in ProcessName -> OTHER
        # + explicit name (the schema requires an explicit name for OTHER/ANALYSIS).
        process_type=ps.ProcessName.OTHER,
        name="transcriptomics_preprocessing",
        stage=ps.ProcessStage.PROCESSING,
        experimenters=[INVESTIGATOR],
        start_date_time=RUN_START,
        end_date_time=RUN_END,
        code=code,
        notes=(
            "Raw-to-preprocessed LC-NE transcriptomics pipeline covering three modalities. "
            "snRNAseq: remove sex-chromosome (X/Y) genes, then scVI (scvi-tools 1.3.3) batch "
            "correction run twice -- excluding the MERFISH gene panel (INCLUDE_MER=False -> "
            "snRNAseq_LCNE_BN_d4_1-5k.h5ad) and including it (INCLUDE_MER=True -> "
            "snRNAseq_LCNE_BN_d4_merbar_1-5k.h5ad). MERFISH: spatial transcriptomics "
            "preprocessing (-> adata_mer_subset_2_2k.h5ad). retro-seq: build filtered AnnData "
            "from raw (-> retroseq_updated_filtered.h5ad). Run in the Code Ocean capsule "
            "LCNE_transcriptomics_preprocessing (run script code/run); its notebooks are not "
            "in this analysis capsule, only its outputs are stored in the asset."
        ),
    )
    return ps.Processing(data_processes=[data_process])


def build_data_description():
    """Data description for the derived asset (aggregation across subjects & modalities)."""
    return ds.DataDescription(
        name=ds.build_data_name(ASSET_LABEL, CREATION_TIME),
        source_data=list(SOURCE_RAW_ASSET_IDS),
        creation_time=CREATION_TIME,
        institution=ds.Organization.AIND,
        data_level=ds.DataLevel.DERIVED,
        investigators=[ds.Person(name=INVESTIGATOR)],
        project_name=PROJECT_NAME,
        # snRNAseq + retro-seq are sequencing -> SCRNASEQ; MERFISH is spatial transcriptomics.
        modalities=[Modality.SCRNASEQ, Modality.MERFISH],
        license=ds.License.CC_BY_40,
        funding_source=FUNDING,
        data_summary=(
            "Preprocessed LC-NE transcriptomics data across three modalities: "
            "batch-corrected single-nucleus RNA-seq matrices (with and without the MERFISH "
            "gene panel), a MERFISH spatial transcriptomics matrix, and a filtered retro-seq "
            "matrix, produced by the raw-to-preprocessed pipeline and consumed by the LC-NE "
            "manuscript analysis."
        ),
    )


def main():
    processing = build_processing()
    data_description = build_data_description()
    # Isolate the asset in its own subfolder (named after the asset) so it holds ONLY the
    # metadata -- /results is shared with the figure pipeline on Code Ocean.
    out = os.path.join(_base_output_dir(), data_description.name)
    os.makedirs(out, exist_ok=True)
    # Write the two core files directly (an aggregation-across-subjects asset needs no
    # subject/procedures, so we skip the full Metadata wrapper).
    data_description.write_standard_file(output_directory=out)
    processing.write_standard_file(output_directory=out)
    print(f"\nMetadata written to: {out}")
    print(f"  contents: {sorted(os.listdir(out))}")
    print("Metadata JSON only -- the ~1.3 GB of data files were NOT copied. Create ONE data "
          "asset that combines these JSON files with the existing preprocessing data (data + "
          "metadata together), then file the aind-open-data transfer issue.")


if __name__ == "__main__":
    main()
