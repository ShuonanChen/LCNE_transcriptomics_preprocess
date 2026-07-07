# LC-NE Transcriptomics Preprocessing

Preprocessing pipelines for the transcriptomic and spatial profiling of locus coeruleus
norepinephrine (LC-NE) neurons. This capsule takes the raw sequencing and imaging outputs
for three complementary modalities and produces the harmonized, quality-controlled
datasets used in the downstream analyses of the associated study.

Developed at the Allen Institute for Neural Dynamics.

## Overview

The pipeline processes three data modalities and integrates them on a shared gene space:

1. **snRNA-seq** — single-nucleus RNA sequencing of LC-NE neurons.
2. **MERFISH** — spatially resolved transcriptomics.
3. **Retro-seq** — sequencing of retrogradely labeled, projection-defined neurons.

For each modality the pipeline performs quality control, normalization, and batch
correction, and writes analysis-ready [AnnData](https://anndata.readthedocs.io) (`.h5ad`)
objects together with summary figures.

## Pipeline

The stages run in a fixed order because the single-nucleus stage defines the gene lists
consumed by the spatial and retro-seq stages.

### 1. snRNA-seq
- Remove sex-chromosome (X/Y) genes while retaining mitochondrial genes.
- Quality-control filtering of all cells.
- Highly variable gene selection and clustering.
- Batch correction and denoised, batch-averaged normalized expression via
  [scVI](https://scvi-tools.org). The batch-correction step is run both with and without
  the MERFISH gene panel to produce the two gene spaces used downstream.

### 2. MERFISH
- Apply inverse registration from the pre-existing conversion matrix to align cells to the
  reference coordinate framework.
- Batch processing across imaging runs, doublet removal, and batch correction.
- Filter to the target neuronal populations.

### 3. Retro-seq
- Donor whitelist and per-donor injection-target / sequencing-run annotation.
- Pre-QC count floors on genes and cells, followed by QC filtering on gene counts,
  mitochondrial fraction, and ribosomal fraction.
- Low-resolution clustering to retain the LC-NE / neuronal population.
- Batch normalization and export of the filtered dataset.

## Repository structure

```
code/
  run                         Entry point; executes all notebooks in order
  notebooks/
    snRNAseq/                 Single-nucleus QC, XY-gene removal, batch correction
    merfish/                  MERFISH registration, filtering, batch correction
    retroseq/                 Retro-seq end-to-end preprocessing
  utils.py, *_util.py         Shared helper functions
data/                         Input datasets (see below)
results/                      Generated outputs (AnnData files and figures)
```

## Data

Inputs are provided as attached datasets and files under `data/`:

- **snRNA-seq** counts and metadata (`snRNAseq_LCNE`).
- **MERFISH** processing inputs (`Nardone_2024_merfish_processing`).
- **Retro-seq** raw count matrix and BARseq counts (`data/`).

Outputs are written to `results/`, including the batch-corrected `.h5ad` objects for each
modality and QC figures under `results/figures/`.

## Reproducing the results

The capsule is self-contained and reproducible. To run the full pipeline:

```bash
code/run
```

This executes each notebook in place with a per-notebook timeout and writes all outputs to
`results/`. Notebooks can also be opened and run individually; when doing so, run the
snRNA-seq stage first, as it produces the gene lists used by the other stages.

## Citation

If you use this pipeline or the derived datasets, please cite the associated publication
and the Allen Institute for Neural Dynamics.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
Copyright (c) Allen Institute for Neural Dynamics.
