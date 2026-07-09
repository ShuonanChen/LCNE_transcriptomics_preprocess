"""
Add AIND metadata for the ``Nardone_2024_merfish_processing`` data asset.

This asset is scientist-derived data with two provenance layers:

1. External source data -- MERFISH atlas of the murine dorsal pons from
   Nardone et al., Nat Commun 15:1966 (2024), doi:10.1038/s41467-024-45907-7
   (Beth Israel Deaconess Medical Center / Harvard Medical School), downloaded
   from the BIDMC datashare.
2. Lab-added CCF registration -- QuickNII/VisuAlign transformation matrices
   (``quicknii_rez/``, ``visualign_rez/``) and the resulting CCF-mapped cell
   coordinates (``registered/``) produced at AIND.

Because the base data is non-AIND and aggregates many external subjects, no AIND
base metadata is inherited: we build a ``DataDescription`` (non-AIND external
path) plus a ``Processing`` object documenting the lab's CCF-registration step.

Run inside the capsule::

    python code/add_metadata.py [output_dir]        # copies data + writes metadata
    python code/add_metadata.py [output_dir] --no-copy   # metadata JSONs only

By default this assembles the *complete new data asset* in its own subfolder,
``/results/Nardone_2024_merfish_processing`` -- kept out of the top level of
``/results`` so it doesn't mix with the pipeline's generated outputs. It copies
the existing asset contents there and writes ``data_description.json`` and
``processing.json`` at that subfolder's root. Create the new Code Ocean data
asset from this subfolder and attach that asset (data + metadata) going forward.
Pass ``--no-copy`` to (re)write only the metadata JSONs.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import aind_data_schema.core.data_description as ds
import aind_data_schema.core.processing as ps
from aind_data_schema.core.metadata import Metadata

REPO_URL = "https://github.com/AllenNeuralDynamics/LCNE_transcriptomics_preprocess"
ASSET_NAME = "Nardone_2024_merfish_processing"
BIDMC_URL = (
    "https://research.bidmc.harvard.edu/datashare/"
    "DataShareInfo.ASP?Submit=Display&ID=7"
)
DATA_ROOT = Path(__file__).resolve().parent.parent / "data"


def build_processing() -> ps.Processing:
    """Document the lab-added QuickNII/VisuAlign -> CCF registration step."""
    code_details = ps.Code(
        name="LCNE_transcriptomics_preprocess",
        url=REPO_URL,
        version="1.0",
        input_data=[ps.DataAsset(name=ASSET_NAME)],
    )
    return ps.Processing(
        data_processes=[
            ps.DataProcess(
                process_type=ps.ProcessName.IMAGE_ATLAS_ALIGNMENT,
                name="ccf_registration",
                stage=ps.ProcessStage.ANALYSIS,
                experimenters=["Shuonan Chen"],
                start_date_time="2024-03-04T00:00",
                end_date_time="2024-03-04T00:00",
                code=code_details,
                notes=(
                    "Manual per-section alignment of Nardone 2024 MERFISH images to "
                    "the Allen CCFv3 using QuickNII (affine, quicknii_rez/) and "
                    "VisuAlign (nonlinear markers, visualign_rez/); the transforms "
                    "are applied to map cell coordinates into CCF space "
                    "(registered/*.csv)."
                ),
            ),
        ],
    )


def build_data_description() -> ds.DataDescription:
    """Non-AIND external-source data description for the Nardone 2024 MERFISH data."""
    creation_time = datetime(2024, 3, 4)
    name = ds.build_data_name(ASSET_NAME, creation_time)
    return ds.DataDescription(
        name=name,
        creation_time=creation_time,
        institution=ds.Organization.OTHER,  # BIDMC / Harvard Medical School (not in registry)
        data_level=ds.DataLevel.DERIVED,
        investigators=[ds.Person(name="Stefano Nardone")],
        project_name="external data",
        modalities=[ds.Modality.MERFISH],
        license=ds.License.CC_BY_40,
        # The schema requires >=1 funding_source. Grant numbers are intentionally
        # omitted (per project decision); AIND is recorded as the funder of the
        # lab-added CCF-registration work.
        funding_source=[ds.Funding(funder=ds.Organization.AIND)],
        data_summary=(
            "MERFISH atlas of the murine dorsal pons (including the locus coeruleus), "
            "Nardone et al., Nat Commun 15:1966 (2024), doi:10.1038/s41467-024-45907-7, "
            "from Beth Israel Deaconess Medical Center / Harvard Medical School. "
            f"Downloaded from {BIDMC_URL} on 2024-03-04. "
            "Lab-added CCF registration: QuickNII/VisuAlign transformation matrices "
            "(quicknii_rez/, visualign_rez/) and the resulting CCF-mapped cell "
            "coordinates (registered/)."
        ),
    )


def resolve_source(data_root: Path = DATA_ROOT) -> Path:
    """Locate the mounted source asset, matching the timestamped-prefix convention."""
    exact = data_root / ASSET_NAME
    if exact.exists():
        return exact
    matches = sorted(data_root.glob(f"{ASSET_NAME}*"))
    if not matches:
        raise FileNotFoundError(
            f"No data asset matching '{ASSET_NAME}*' found under {data_root}."
        )
    return matches[-1]


def copy_source_data(output_path: str) -> None:
    """Copy the existing asset's contents into ``output_path`` (asset root)."""
    src = resolve_source()
    Path(output_path).mkdir(parents=True, exist_ok=True)
    print(f"Copying {src} -> {output_path} (~6 GB, may take a few minutes) ...")
    # cp -a preserves the subfolder structure and is far faster than shutil for
    # the large per-subject metadata/ tree; copies contents of src into output_path.
    subprocess.run(["cp", "-a", f"{src}/.", output_path], check=True)
    print("Copy complete.")


DEFAULT_OUTPUT = f"/results/{ASSET_NAME}"


def main(output_path: str = DEFAULT_OUTPUT, copy_data: bool = True) -> None:
    if copy_data:
        copy_source_data(output_path)
    metadata = Metadata(
        name=ASSET_NAME,
        location=f"s3://aind-open-data/{ASSET_NAME}",
        data_description=build_data_description(),
        processing=build_processing(),
    )
    metadata.data_description.write_standard_file(output_path)
    metadata.processing.write_standard_file(output_path)
    print(f"Wrote data_description.json and processing.json to {output_path}")


if __name__ == "__main__":
    argv = sys.argv[1:]
    copy_data = "--no-copy" not in argv
    positional = [a for a in argv if not a.startswith("-")]
    out = positional[0] if positional else DEFAULT_OUTPUT
    main(out, copy_data=copy_data)
