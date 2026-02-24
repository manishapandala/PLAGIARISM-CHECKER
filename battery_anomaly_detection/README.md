# Battery Cell Build-Variation & Anomaly Exploration

This folder adds an unsupervised workflow for exploring subtle cell-to-cell build variation from tabular outputs.

## What this does

`analyze_cells.py` runs:

1. Basic EDA-oriented preprocessing:
   - numeric feature selection
   - missing-value handling (median imputation)
   - standardization
2. Dimensionality reduction:
   - PCA (for variance-aware feature insight)
   - t-SNE (for nonlinear structure visualization)
3. Unsupervised clustering:
   - Gaussian Mixture Models over `k=2..4` by default
   - model comparison with BIC/AIC + cluster quality metrics
4. Late-lot enrichment check:
   - checks whether any cluster is enriched for `cell_id >= 391`
5. Interpretability outputs:
   - top PCA loading features
   - top cluster-separating features (effect-size style)

This is aligned with the study goal of identifying lot/build variation without hard-coding feature-specific CV rules.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r battery_anomaly_detection/requirements.txt
```

## Run on your dataset

```bash
python battery_anomaly_detection/analyze_cells.py \
  --input path/to/samsung_50e_tabular.csv \
  --id-column cell_id \
  --min-clusters 2 \
  --max-clusters 4 \
  --lot-start-id 391 \
  --output-dir battery_anomaly_detection/output/samsung_50e
```

### Useful flags

- `--sample-size 200`: quick exploratory run on subset
- `--exclude-columns colA colB`: remove confounding numeric columns
- `--pca-components 12`: tune latent dimensionality before clustering
- `--tsne-perplexity 30`: tune manifold view granularity

## Output files

Each run writes:

- `cells_with_embeddings.csv` - original rows + cluster label + PCA/t-SNE coordinates
- `gmm_metrics.csv` - BIC/AIC/Silhouette/Calinski-Harabasz/Davies-Bouldin by `k`
- `cluster_summary.csv` - cluster counts and fractions
- `lot_enrichment.csv` - enrichment stats for cells `>= lot_start_id` (if ID can be parsed)
- `pca_top_loadings.csv` - strongest feature contributions per principal component
- `cluster_shift_features.csv` - biggest standardized shifts for enriched cluster vs rest
- `feature_summary.csv` - per-feature missingness and variance
- `analysis_report.md` - one-page markdown summary
- plots:
  - `pca_clusters.png`
  - `tsne_clusters.png`
  - `cluster_lot_composition.png` (if lot labels are available)
  - `top_cluster_shift_features.png`

## Synthetic smoke test

Generate demo data:

```bash
python battery_anomaly_detection/generate_synthetic_cells.py
```

Then run:

```bash
python battery_anomaly_detection/analyze_cells.py \
  --input battery_anomaly_detection/data/synthetic_cells.csv \
  --id-column cell_id \
  --output-dir battery_anomaly_detection/output/synthetic_demo
```

## Notes

- This is unsupervised anomaly/build-variation detection; a cluster is not automatically a defect class.
- For image-first workflows, the same clustering logic can be reused once image embeddings are generated.
