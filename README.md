# LC-NE Transcriptomics Preprocessing

Preprocessing pipelines for the transcriptomic and spatial profiling of locus coeruleus
norepinephrine (LC-NE) neurons. This capsule takes the raw sequencing and imaging outputs
for three complementary modalities and produces the harmonized, quality-controlled
datasets used in the downstream analyses of the associated study.

Developed at the Allen Institute for Neural Dynamics.
This is the Github link: https://github.com/AllenNeuralDynamics/LCNE_transcriptomics_preprocess

## Overview

Runs for about 25-30min. The pipeline processes three data modalities and integrates them on a shared gene space:

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

**`01_remove_chromosomal_XY.ipynb`** — queries the MyGene API to annotate each gene's chromosome; marks X/Y genes for removal in the next step.

**`02_snRNA_batchcorrection.ipynb`** — drops X/Y genes, selects highly variable genes, and integrates across sex batches with scVI. Run twice via the `INCLUDE_MER` flag: once without and once with the MERFISH gene panel, producing the two gene spaces used by downstream modalities.

### 2. MERFISH

**`MERFISH_preprocess.ipynb`** — registers each section image to the Allen CCF, assembles per-section cell coordinates and counts into an AnnData, runs scVI batch correction across imaging sessions, then filters to LC-NE clusters (high `Dbh`/`Th`/`Slc6a2`).

### 3. Retro-seq

**`create_adata_from_raw.ipynb`** — builds AnnData from raw MTX/TSV inputs, applies donor whitelist, QC filters (gene count, mitochondrial fraction, ribosomal fraction), low-resolution clustering to isolate the LC-NE neuronal population, and exports the filtered dataset.

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

### Inputs

| Mount / path | Format | Origin |
|---|---|---|
| `snRNAseq_LCNE` | `.h5ad` | Output of the upstream snRNA-seq processing pipeline |
| `retroseq` (under `data/`) | `.tsv`/`.csv`/`.mtx` count matrix + `.h5ad` | Output of the same upstream pipeline |
| `Nardone_2024_merfish_processing` | mixed | See note below |

**`Nardone_2024_merfish_processing` — important:**
- Contains **two distinct components**:
  1. **Original MERFISH data** from Nardone et al. (2024) — raw/unregistered, not aligned to CCF.
  2. **CCF registration results** produced by this lab — spatial coordinates mapped to the Allen Common Coordinate Framework.
- Source publication: Nardone et al. (2024), *Nature Communications* — https://www.nature.com/articles/s41467-024-45907-7
- **AIND metadata:** [`code/add_metadata.py`](code/add_metadata.py) assembles the full asset (data + `data_description.json` + `processing.json`, recording the external source and the lab-added CCF registration) into its own subfolder `results/Nardone_2024_merfish_processing/`, kept out of the top level of `results/` so it doesn't mix with pipeline outputs. Create the new Code Ocean data asset from that subfolder, then transfer it to `aind-open-data` before publication.

### Outputs

| File | Description |
|---|---|
| `snRNAseq_LCNE_with_chrom.h5ad` | Intermediate: snRNA with per-gene chromosome annotation (notebook 01 → input to 02) |
| `results/snRNAseq/snRNAseq_LCNE_BN_d4_1-5k.h5ad` | Batch-corrected snRNA — standard gene set |
| `results/snRNAseq/snRNAseq_LCNE_BN_d4_merbar_1-5k.h5ad` | Batch-corrected snRNA — MERFISH panel genes included |
| `registered_{slice}.csv` (per section) | Intermediate: CCF-registered cell coordinates for each MERFISH section |
| `results/adata_mer_subset_2_2k.h5ad` | Filtered MERFISH AnnData (LC-NE clusters only) |
| `results/retroseq/retroseq_updated_filtered.h5ad` | Filtered retroseq AnnData (LC-NE neurons only) |
| `results/figures/` | QC plots for each modality |

## Reproducing the results

The capsule is self-contained and reproducible. To run the full pipeline:

```bash
code/run
```

This executes each notebook in place with a per-notebook timeout and writes all outputs to
`results/`. Notebooks can also be opened and run individually; when doing so, run the
snRNA-seq stage first, as it produces the gene lists used by the other stages.

## Citation

If you use this pipeline or the derived datasets, please cite the associated preprint
and the Allen Institute for Neural Dynamics.

> Su, Z., Kosillo, P., Jung, K., Chen, S., ..., Siegle, J., & Cohen, J. Y. (2026).
> *Topographic structure and function of locus coeruleus norepinephrine neurons.*
> bioRxiv. https://doi.org/10.64898/2026.04.10.717727

```bibtex
@article{su2026topographic,
  title     = {Topographic structure and function of locus coeruleus norepinephrine neurons},
  author    = {Su, Z. and Kosillo, P. and Jung, K. and Chen, S. and Summers, M. T. and Piet, A. and Hou, H. and Hagihara, K. M. and Friedmann, D. and Ho-Shing, O. and Becker, M. I. and Chartrand, T. and Grotz, P. and Hilton-VanOsdall, E. and Lee, M. and Javeri, R. and Tuggle, S. L. and Ouellette, N. and Myers, H. and Laiton, C. and Wulf, K. and Rohde, J. and Buccino, A. P. and Arshadi, C. and Wang, D. and Seshamani, S. and Vasquez, S. and Eng, C. M. and Ollerenshaw, D. R. and Dee, N. and Casper, T. and Ho, W. and Jungert, M. and Jordan, A. and Phillips, E. and Chakka, A. B. and Nasirova, K. and Blake, K. and McCutcheon, A. and Koch, M. and Vergara, M. C. and Smith, K. A. and Jarsky, T. and Lusk, N. and Rue, M. C. P. and Chen, X. and Siegle, J. and Cohen, J. Y.},
  journal   = {bioRxiv},
  year      = {2026},
  doi       = {10.64898/2026.04.10.717727},
  url       = {https://www.biorxiv.org/content/10.64898/2026.04.10.717727v1},
  publisher = {Cold Spring Harbor Laboratory}
}
```



## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
Copyright (c) Allen Institute for Neural Dynamics.
