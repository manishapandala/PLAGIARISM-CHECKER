#!/usr/bin/env python3
"""Run unsupervised build-variation analysis on battery tabular data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Perform EDA, dimensionality reduction, and clustering on battery cell tabular data."
        )
    )
    parser.add_argument("--input", required=True, help="Path to input CSV or Parquet file.")
    parser.add_argument(
        "--output-dir",
        default="battery_anomaly_detection/output",
        help="Directory to write plots and result tables.",
    )
    parser.add_argument(
        "--id-column",
        default=None,
        help="Optional explicit column for cell IDs. Inferred when omitted.",
    )
    parser.add_argument(
        "--lot-start-id",
        type=int,
        default=391,
        help="Cells with ID >= this value are tagged as the late-shipment lot.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Optional random sample size for quick EDA iterations.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed used by sampling, t-SNE, and GMM.",
    )
    parser.add_argument(
        "--min-clusters",
        type=int,
        default=2,
        help="Minimum number of GMM clusters to evaluate.",
    )
    parser.add_argument(
        "--max-clusters",
        type=int,
        default=4,
        help="Maximum number of GMM clusters to evaluate.",
    )
    parser.add_argument(
        "--pca-components",
        type=int,
        default=12,
        help="Max PCA dimensions retained before clustering.",
    )
    parser.add_argument(
        "--tsne-perplexity",
        type=float,
        default=30.0,
        help="Target t-SNE perplexity. Auto-adjusted to dataset size.",
    )
    parser.add_argument(
        "--exclude-columns",
        nargs="*",
        default=[],
        help="Optional list of columns to exclude from numeric feature matrix.",
    )
    parser.add_argument(
        "--missing-threshold",
        type=float,
        default=0.4,
        help="Drop numeric columns with missing fraction above this threshold.",
    )
    parser.add_argument(
        "--top-features",
        type=int,
        default=10,
        help="Top features to show in loadings and effect-size summaries.",
    )
    return parser.parse_args()


def load_dataframe(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(input_path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(input_path)
    raise ValueError("Unsupported input format. Use CSV or Parquet.")


def infer_id_column(df: pd.DataFrame, explicit: str | None) -> str:
    if explicit:
        if explicit not in df.columns:
            raise ValueError(f"ID column '{explicit}' was not found in the dataset.")
        return explicit

    normalized = {col.lower(): col for col in df.columns}
    preferred = ["cell_id", "cellid", "cell_number", "cell", "id", "serial"]
    for candidate in preferred:
        if candidate in normalized:
            return normalized[candidate]

    for col in df.columns:
        lowered = col.lower()
        if "cell" in lowered and "id" in lowered:
            return col

    generated = "__row_id__"
    df[generated] = np.arange(1, len(df) + 1, dtype=int)
    return generated


def to_numeric_id(series: pd.Series) -> pd.Series:
    numeric_direct = pd.to_numeric(series, errors="coerce")
    if numeric_direct.notna().mean() > 0.8:
        return numeric_direct

    extracted = (
        series.astype(str).str.extract(r"(\d+)", expand=False).pipe(pd.to_numeric, errors="coerce")
    )
    return extracted


def prepare_features(
    df: pd.DataFrame,
    id_column: str,
    exclude_columns: Iterable[str],
    missing_threshold: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric_df = df.select_dtypes(include=[np.number]).copy()
    drop_cols = set(exclude_columns)
    drop_cols.add(id_column)
    numeric_df = numeric_df.drop(columns=[c for c in drop_cols if c in numeric_df.columns], errors="ignore")
    if numeric_df.empty:
        raise ValueError("No numeric features are available after exclusions.")

    missing_fraction = numeric_df.isna().mean()
    cols_to_keep = missing_fraction[missing_fraction <= missing_threshold].index.tolist()
    numeric_df = numeric_df[cols_to_keep]
    if numeric_df.empty:
        raise ValueError(
            "No numeric features remain after dropping high-missingness columns. "
            "Increase --missing-threshold or check your dataset."
        )

    imputed = numeric_df.fillna(numeric_df.median(numeric_only=True))
    variance = imputed.var()
    non_constant_cols = variance[variance > 0].index.tolist()
    imputed = imputed[non_constant_cols]
    if imputed.empty:
        raise ValueError("All numeric features became constant after preprocessing.")

    feature_summary = pd.DataFrame(
        {
            "feature": imputed.columns,
            "missing_fraction": missing_fraction.reindex(imputed.columns).fillna(0.0).values,
            "mean": imputed.mean().values,
            "std": imputed.std().values,
            "variance": imputed.var().values,
        }
    ).sort_values(by="variance", ascending=False)
    return imputed, feature_summary


def choose_tsne_perplexity(n_samples: int, requested: float) -> float:
    if n_samples <= 2:
        return 1.0
    max_valid = max(1.0, (n_samples - 1) / 3)
    return float(min(requested, max_valid, n_samples - 1e-3))


def evaluate_gmm_range(
    data_for_clustering: np.ndarray,
    min_clusters: int,
    max_clusters: int,
    random_state: int,
) -> tuple[pd.DataFrame, int, np.ndarray]:
    if min_clusters > max_clusters:
        raise ValueError("--min-clusters must be <= --max-clusters.")

    metrics_rows: list[dict[str, float | int]] = []
    best_bic = float("inf")
    best_k = -1
    best_labels: np.ndarray | None = None

    for k in range(min_clusters, max_clusters + 1):
        if len(data_for_clustering) <= k:
            continue

        gmm = GaussianMixture(
            n_components=k,
            covariance_type="full",
            n_init=8,
            random_state=random_state,
        )
        labels = gmm.fit_predict(data_for_clustering)

        unique_labels = np.unique(labels)
        if len(unique_labels) < 2:
            silhouette = np.nan
            calinski = np.nan
            davies = np.nan
        else:
            silhouette = float(silhouette_score(data_for_clustering, labels))
            calinski = float(calinski_harabasz_score(data_for_clustering, labels))
            davies = float(davies_bouldin_score(data_for_clustering, labels))

        bic = float(gmm.bic(data_for_clustering))
        aic = float(gmm.aic(data_for_clustering))
        metrics_rows.append(
            {
                "k": k,
                "bic": bic,
                "aic": aic,
                "silhouette": silhouette,
                "calinski_harabasz": calinski,
                "davies_bouldin": davies,
            }
        )

        if bic < best_bic:
            best_bic = bic
            best_k = k
            best_labels = labels

    if best_labels is None or best_k < 0:
        raise ValueError(
            "Could not fit any GMM models. Make sure the dataset has enough rows and "
            "that --max-clusters is less than row count."
        )

    metrics_df = pd.DataFrame(metrics_rows).sort_values("k")
    return metrics_df, best_k, best_labels


def build_cluster_summary(
    labels: np.ndarray,
    id_numeric: pd.Series,
    lot_start_id: int,
) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    summary = pd.Series(labels).value_counts().sort_index().rename_axis("cluster").reset_index(name="count")
    summary["fraction"] = summary["count"] / summary["count"].sum()

    if id_numeric.notna().mean() < 0.8:
        return summary, None

    lot_mask = id_numeric.ge(lot_start_id)

    eval_df = pd.DataFrame({"cluster": labels, "is_lot_391_500": lot_mask.fillna(False)})
    contingency = pd.crosstab(eval_df["cluster"], eval_df["is_lot_391_500"])
    contingency.columns = [f"is_lot_{str(col).lower()}" for col in contingency.columns]

    if "is_lot_true" not in contingency.columns:
        contingency["is_lot_true"] = 0
    if "is_lot_false" not in contingency.columns:
        contingency["is_lot_false"] = 0

    contingency = contingency.reset_index()
    contingency["cluster_total"] = contingency["is_lot_true"] + contingency["is_lot_false"]
    contingency["lot_fraction_in_cluster"] = contingency["is_lot_true"] / contingency["cluster_total"].clip(lower=1)
    overall_lot_fraction = float(eval_df["is_lot_391_500"].mean())
    contingency["lot_enrichment_over_dataset"] = contingency["lot_fraction_in_cluster"] / max(
        overall_lot_fraction, 1e-9
    )
    contingency["lot_capture_fraction"] = contingency["is_lot_true"] / max(
        float(eval_df["is_lot_391_500"].sum()), 1.0
    )
    return summary, contingency.sort_values("cluster")


def top_pca_loadings(pca_model: PCA, feature_names: list[str], top_n: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    pcs_to_report = min(3, pca_model.components_.shape[0])
    for pc_idx in range(pcs_to_report):
        component = pca_model.components_[pc_idx]
        top_indices = np.argsort(np.abs(component))[::-1][:top_n]
        for rank, feat_idx in enumerate(top_indices, start=1):
            rows.append(
                {
                    "principal_component": f"PC{pc_idx + 1}",
                    "rank": rank,
                    "feature": feature_names[feat_idx],
                    "loading": float(component[feat_idx]),
                    "abs_loading": float(abs(component[feat_idx])),
                }
            )
    return pd.DataFrame(rows)


def top_cluster_shift_features(
    scaled_matrix: np.ndarray,
    labels: np.ndarray,
    feature_names: list[str],
    reference_cluster: int,
    top_n: int,
) -> pd.DataFrame:
    in_cluster = labels == reference_cluster
    out_cluster = ~in_cluster
    if in_cluster.sum() < 2 or out_cluster.sum() < 2:
        return pd.DataFrame(columns=["feature", "effect_size_z", "abs_effect_size_z"])

    mean_diff = scaled_matrix[in_cluster].mean(axis=0) - scaled_matrix[out_cluster].mean(axis=0)
    top_idx = np.argsort(np.abs(mean_diff))[::-1][:top_n]
    return pd.DataFrame(
        {
            "feature": [feature_names[i] for i in top_idx],
            "effect_size_z": mean_diff[top_idx],
            "abs_effect_size_z": np.abs(mean_diff[top_idx]),
        }
    )


def save_embedding_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    output_path: Path,
    title: str,
) -> None:
    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        data=df,
        x=x_col,
        y=y_col,
        hue="cluster",
        style="is_lot_391_500",
        alpha=0.85,
        palette="tab10",
        edgecolor="none",
    )
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()


def save_lot_composition_plot(crosstab_df: pd.DataFrame, output_path: Path) -> None:
    plot_df = crosstab_df[["cluster", "is_lot_false", "is_lot_true"]].copy()
    plot_df = plot_df.set_index("cluster")
    totals = plot_df.sum(axis=1).replace(0, np.nan)
    normed = plot_df.div(totals, axis=0).fillna(0.0)

    ax = normed.plot(kind="bar", stacked=True, figsize=(9, 6), color=["#4e79a7", "#f28e2b"])
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Fraction within cluster")
    ax.set_title("Late-shipment lot composition by cluster")
    ax.legend(["Cells 1-390", "Cells 391-500"], loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()


def save_effect_plot(effect_df: pd.DataFrame, output_path: Path, reference_cluster: int) -> None:
    if effect_df.empty:
        return
    ordered = effect_df.sort_values("effect_size_z")
    plt.figure(figsize=(10, 7))
    plt.barh(ordered["feature"], ordered["effect_size_z"], color="#59a14f")
    plt.xlabel("Standardized mean difference (cluster - rest)")
    plt.title(f"Top separating features for cluster {reference_cluster}")
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()


def write_markdown_report(
    output_path: Path,
    input_path: Path,
    row_count: int,
    feature_count: int,
    id_column: str,
    best_k: int,
    metrics_df: pd.DataFrame,
    pca_var_ratio: np.ndarray,
    cluster_summary: pd.DataFrame,
    lot_enrichment: pd.DataFrame | None,
    loadings_df: pd.DataFrame,
    effect_df: pd.DataFrame,
) -> None:
    pc1 = float(pca_var_ratio[0]) if len(pca_var_ratio) >= 1 else 0.0
    pc1_2 = float(pca_var_ratio[:2].sum()) if len(pca_var_ratio) >= 2 else pc1
    pc1_3 = float(pca_var_ratio[:3].sum()) if len(pca_var_ratio) >= 3 else float(pca_var_ratio.sum())

    lines = [
        "# Battery Cell Unsupervised Analysis Report",
        "",
        "## Data snapshot",
        f"- Input file: `{input_path}`",
        f"- Rows analyzed: **{row_count}**",
        f"- Numeric features analyzed: **{feature_count}**",
        f"- Cell ID column used: `{id_column}`",
        "",
        "## Model selection",
        f"- Best GMM cluster count by BIC: **k = {best_k}**",
        "",
        metrics_df.to_markdown(index=False),
        "",
        "## PCA explained variance",
        (
            "- Cumulative explained variance by first 3 PCs: "
            f"PC1={pc1:.3f}, "
            f"PC1-2={pc1_2:.3f}, "
            f"PC1-3={pc1_3:.3f}"
        ),
        "",
        "## Cluster distribution",
        cluster_summary.to_markdown(index=False),
        "",
    ]

    if lot_enrichment is not None:
        lines.extend(
            [
                "## Late-shipment lot enrichment (cells >= 391)",
                lot_enrichment.to_markdown(index=False),
                "",
            ]
        )

    lines.extend(
        [
            "## Top PCA loadings",
            loadings_df.to_markdown(index=False),
            "",
        ]
    )

    if not effect_df.empty:
        lines.extend(
            [
                "## Top cluster-separating features",
                effect_df.to_markdown(index=False),
                "",
            ]
        )

    lines.extend(
        [
            "## Notes",
            "- This is an unsupervised analysis and does not imply defects by itself.",
            "- Validate cluster meaning with electrochemical and process metadata before actioning.",
            "- If clusters are unstable across runs, increase sample size or revisit feature engineering.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    sns.set_theme(style="whitegrid")

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataframe(input_path)
    if args.sample_size is not None and args.sample_size > 0 and args.sample_size < len(df):
        df = df.sample(n=args.sample_size, random_state=args.random_state).sort_index()
    if len(df) < max(args.max_clusters + 1, 10):
        raise ValueError(
            "Dataset is too small for stable clustering and t-SNE. "
            "Use at least 10 rows and more than --max-clusters."
        )

    id_column = infer_id_column(df, args.id_column)
    id_numeric = to_numeric_id(df[id_column])

    features_df, feature_summary = prepare_features(
        df=df,
        id_column=id_column,
        exclude_columns=args.exclude_columns,
        missing_threshold=args.missing_threshold,
    )
    feature_summary.to_csv(output_dir / "feature_summary.csv", index=False)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features_df.values)

    n_components = min(args.pca_components, scaled.shape[1], scaled.shape[0] - 1)
    if n_components < 1:
        raise ValueError("PCA could not run because too few rows/features are available.")

    pca_model = PCA(n_components=n_components, random_state=args.random_state)
    pca_embedding = pca_model.fit_transform(scaled)
    if pca_embedding.shape[1] >= 2:
        pca2 = pca_embedding[:, :2]
    else:
        pca2 = np.column_stack([pca_embedding[:, 0], np.zeros(len(df))])

    clustering_matrix = pca_embedding[:, : min(8, pca_embedding.shape[1])]
    gmm_metrics_df, best_k, labels = evaluate_gmm_range(
        data_for_clustering=clustering_matrix,
        min_clusters=args.min_clusters,
        max_clusters=args.max_clusters,
        random_state=args.random_state,
    )
    gmm_metrics_df.to_csv(output_dir / "gmm_metrics.csv", index=False)

    perplexity = choose_tsne_perplexity(len(df), args.tsne_perplexity)
    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        random_state=args.random_state,
        init="pca",
        learning_rate="auto",
    )
    tsne_embedding = tsne.fit_transform(clustering_matrix)

    cluster_summary, lot_enrichment = build_cluster_summary(
        labels=labels,
        id_numeric=id_numeric,
        lot_start_id=args.lot_start_id,
    )
    cluster_summary.to_csv(output_dir / "cluster_summary.csv", index=False)
    if lot_enrichment is not None:
        lot_enrichment.to_csv(output_dir / "lot_enrichment.csv", index=False)

    loadings_df = top_pca_loadings(
        pca_model=pca_model,
        feature_names=features_df.columns.tolist(),
        top_n=args.top_features,
    )
    loadings_df.to_csv(output_dir / "pca_top_loadings.csv", index=False)

    if lot_enrichment is not None and not lot_enrichment.empty:
        reference_cluster = int(
            lot_enrichment.sort_values(
                ["lot_enrichment_over_dataset", "lot_capture_fraction"],
                ascending=False,
            )["cluster"].iloc[0]
        )
    else:
        reference_cluster = int(cluster_summary.sort_values("count", ascending=False)["cluster"].iloc[0])

    effect_df = top_cluster_shift_features(
        scaled_matrix=scaled,
        labels=labels,
        feature_names=features_df.columns.tolist(),
        reference_cluster=reference_cluster,
        top_n=args.top_features,
    )
    effect_df.to_csv(output_dir / "cluster_shift_features.csv", index=False)

    result_df = df.copy()
    result_df["cluster"] = labels
    result_df["pca_1"] = pca2[:, 0]
    result_df["pca_2"] = pca2[:, 1]
    result_df["tsne_1"] = tsne_embedding[:, 0]
    result_df["tsne_2"] = tsne_embedding[:, 1]
    result_df["is_lot_391_500"] = id_numeric.ge(args.lot_start_id).fillna(False)
    result_df.to_csv(output_dir / "cells_with_embeddings.csv", index=False)

    save_embedding_plot(
        df=result_df,
        x_col="pca_1",
        y_col="pca_2",
        output_path=output_dir / "pca_clusters.png",
        title=f"PCA view of battery cells (GMM k={best_k})",
    )
    save_embedding_plot(
        df=result_df,
        x_col="tsne_1",
        y_col="tsne_2",
        output_path=output_dir / "tsne_clusters.png",
        title=f"t-SNE view of battery cells (GMM k={best_k})",
    )
    if lot_enrichment is not None:
        save_lot_composition_plot(lot_enrichment, output_dir / "cluster_lot_composition.png")
    save_effect_plot(effect_df, output_dir / "top_cluster_shift_features.png", reference_cluster)

    run_summary = {
        "input_file": str(input_path),
        "rows_analyzed": int(len(df)),
        "feature_count": int(features_df.shape[1]),
        "id_column": id_column,
        "best_cluster_count": int(best_k),
        "tsne_perplexity_used": float(perplexity),
        "output_dir": str(output_dir),
        "reference_cluster_for_feature_shift": int(reference_cluster),
    }
    (output_dir / "run_summary.json").write_text(
        json.dumps(run_summary, indent=2),
        encoding="utf-8",
    )

    write_markdown_report(
        output_path=output_dir / "analysis_report.md",
        input_path=input_path,
        row_count=len(df),
        feature_count=features_df.shape[1],
        id_column=id_column,
        best_k=best_k,
        metrics_df=gmm_metrics_df,
        pca_var_ratio=pca_model.explained_variance_ratio_,
        cluster_summary=cluster_summary,
        lot_enrichment=lot_enrichment,
        loadings_df=loadings_df,
        effect_df=effect_df,
    )

    print("Analysis complete.")
    print(f"Results written to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
