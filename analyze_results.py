#!/usr/bin/env python3
"""
Analyze test results CSV and generate confusion matrices and charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report

# Configuration
CSV_FILE = "test_results_output/test_results_20251203_165455.csv"
OUTPUT_FOLDER = "test_results_output/analysis"

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def load_data(csv_file: str) -> pd.DataFrame:
    """Load CSV data."""
    df = pd.read_csv(csv_file)
    return df


def calculate_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    """Calculate classification metrics."""
    # Manually calculate confusion matrix to ensure 2x2 shape
    # This handles cases where all values are the same
    tn = ((y_true == False) & (y_pred == False)).sum()
    fp = ((y_true == False) & (y_pred == True)).sum()
    fn = ((y_true == True) & (y_pred == False)).sum()
    tp = ((y_true == True) & (y_pred == True)).sum()
    
    # Create 2x2 confusion matrix
    cm = np.array([[tn, fp], [fn, tp]])
    
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    return {
        "confusion_matrix": cm,
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "specificity": specificity,
    }


def plot_confusion_matrix(cm: np.ndarray, category: str, metrics: dict, ax=None):
    """Plot confusion matrix heatmap."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    labels = ["Negative", "Positive"]
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
        cbar_kws={"label": "Count"},
    )
    
    ax.set_xlabel("Predicted", fontsize=12, fontweight="bold")
    ax.set_ylabel("Actual", fontsize=12, fontweight="bold")
    ax.set_title(
        f"{category}\nAccuracy: {metrics['accuracy']:.2%} | "
        f"Precision: {metrics['precision']:.2%} | "
        f"Recall: {metrics['recall']:.2%} | "
        f"F1: {metrics['f1']:.2%}",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    
    # Add text annotations
    textstr = f"TP: {metrics['tp']} | TN: {metrics['tn']}\nFP: {metrics['fp']} | FN: {metrics['fn']}"
    ax.text(
        0.5,
        -0.15,
        textstr,
        transform=ax.transAxes,
        fontsize=10,
        ha="center",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )


def create_confusion_matrices(df: pd.DataFrame):
    """Create confusion matrices for all categories."""
    categories = {
        "Safe/Unsafe": ("Expected Safe", "Actual Safe"),
        "Emails": ("Expected Emails", "Actual Emails"),
        "Address": ("Expected Address", "Actual Address"),
        "Phone Numbers": ("Expected Phone Numbers", "Actual Phone Numbers"),
        "License Plates": ("Expected License Plates", "Actual License Plates"),
    }
    
    # Filter out rows with errors
    df_clean = df[df["Error"].isna()].copy()
    
    # Convert boolean columns
    for col in df_clean.columns:
        if "Expected" in col or "Actual" in col:
            df_clean[col] = df_clean[col].astype(bool)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    all_metrics = {}
    
    for idx, (category, (expected_col, actual_col)) in enumerate(categories.items()):
        y_true = df_clean[expected_col]
        y_pred = df_clean[actual_col]
        
        metrics = calculate_metrics(y_true, y_pred)
        all_metrics[category] = metrics
        
        plot_confusion_matrix(metrics["confusion_matrix"], category, metrics, ax=axes[idx])
    
    # Remove empty subplot
    fig.delaxes(axes[5])
    
    plt.tight_layout()
    output_path = Path(OUTPUT_FOLDER) / "confusion_matrices.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()
    
    return all_metrics


def create_metrics_comparison(all_metrics: dict):
    """Create comparison charts for all metrics."""
    categories = list(all_metrics.keys())
    
    # Extract metrics
    accuracy = [all_metrics[cat]["accuracy"] for cat in categories]
    precision = [all_metrics[cat]["precision"] for cat in categories]
    recall = [all_metrics[cat]["recall"] for cat in categories]
    f1 = [all_metrics[cat]["f1"] for cat in categories]
    specificity = [all_metrics[cat]["specificity"] for cat in categories]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(categories))
    width = 0.15
    
    ax.bar(x - 2 * width, accuracy, width, label="Accuracy", color="#3498db")
    ax.bar(x - width, precision, width, label="Precision", color="#2ecc71")
    ax.bar(x, recall, width, label="Recall", color="#e74c3c")
    ax.bar(x + width, f1, width, label="F1 Score", color="#f39c12")
    ax.bar(x + 2 * width, specificity, width, label="Specificity", color="#9b59b6")
    
    ax.set_xlabel("Category", fontsize=12, fontweight="bold")
    ax.set_ylabel("Score", fontsize=12, fontweight="bold")
    ax.set_title("Performance Metrics Comparison Across Categories", fontsize=16, fontweight="bold", pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=15, ha="right")
    ax.set_ylim([0, 1.1])
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    
    # Add value labels on bars
    for i, cat in enumerate(categories):
        for j, (values, offset) in enumerate([
            (accuracy, -2 * width),
            (precision, -width),
            (recall, 0),
            (f1, width),
            (specificity, 2 * width),
        ]):
            value = values[i]
            ax.text(i + offset, value + 0.01, f"{value:.2%}", ha="center", va="bottom", fontsize=8)
    
    plt.tight_layout()
    output_path = Path(OUTPUT_FOLDER) / "metrics_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def create_error_analysis(df: pd.DataFrame):
    """Create charts analyzing errors and incorrect predictions."""
    df_clean = df[df["Error"].isna()].copy()
    
    # Convert boolean columns
    for col in df_clean.columns:
        if "Expected" in col or "Actual" in col:
            df_clean[col] = df_clean[col].astype(bool)
    
    categories = ["Safe", "Emails", "Address", "Phone Numbers", "License Plates"]
    expected_cols = ["Expected Safe", "Expected Emails", "Expected Address", 
                     "Expected Phone Numbers", "Expected License Plates"]
    actual_cols = ["Actual Safe", "Actual Emails", "Actual Address",
                   "Actual Phone Numbers", "Actual License Plates"]
    correct_cols = ["Safe Correct", "Emails Correct", "Address Correct",
                    "Phone Numbers Correct", "License Plates Correct"]
    
    # Calculate error rates
    error_rates = []
    false_positive_rates = []
    false_negative_rates = []
    
    for expected_col, actual_col, correct_col in zip(expected_cols, actual_cols, correct_cols):
        correct = df_clean[correct_col].sum()
        total = len(df_clean)
        error_rate = 1 - (correct / total) if total > 0 else 0
        
        # False positives: predicted True but should be False
        fp = ((df_clean[expected_col] == False) & (df_clean[actual_col] == True)).sum()
        fp_rate = fp / len(df_clean[df_clean[expected_col] == False]) if len(df_clean[df_clean[expected_col] == False]) > 0 else 0
        
        # False negatives: predicted False but should be True
        fn = ((df_clean[expected_col] == True) & (df_clean[actual_col] == False)).sum()
        fn_rate = fn / len(df_clean[df_clean[expected_col] == True]) if len(df_clean[df_clean[expected_col] == True]) > 0 else 0
        
        error_rates.append(error_rate)
        false_positive_rates.append(fp_rate)
        false_negative_rates.append(fn_rate)
    
    # Create error analysis chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Error rates
    x = np.arange(len(categories))
    width = 0.25
    
    ax1.bar(x - width, error_rates, width, label="Overall Error Rate", color="#e74c3c", alpha=0.8)
    ax1.bar(x, false_positive_rates, width, label="False Positive Rate", color="#f39c12", alpha=0.8)
    ax1.bar(x + width, false_negative_rates, width, label="False Negative Rate", color="#9b59b6", alpha=0.8)
    
    ax1.set_xlabel("Category", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Rate", fontsize=12, fontweight="bold")
    ax1.set_title("Error Analysis by Category", fontsize=14, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=15, ha="right")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_ylim([0, max(max(error_rates), max(false_positive_rates), max(false_negative_rates)) * 1.2])
    
    # Add value labels
    for i, (er, fpr, fnr) in enumerate(zip(error_rates, false_positive_rates, false_negative_rates)):
        ax1.text(i - width, er + 0.01, f"{er:.2%}", ha="center", va="bottom", fontsize=8)
        ax1.text(i, fpr + 0.01, f"{fpr:.2%}", ha="center", va="bottom", fontsize=8)
        ax1.text(i + width, fnr + 0.01, f"{fnr:.2%}", ha="center", va="bottom", fontsize=8)
    
    # Correct vs Incorrect by category
    correct_counts = [df_clean[col].sum() for col in correct_cols]
    incorrect_counts = [len(df_clean) - count for count in correct_counts]
    
    x2 = np.arange(len(categories))
    ax2.bar(x2 - width/2, correct_counts, width, label="Correct", color="#2ecc71", alpha=0.8)
    ax2.bar(x2 + width/2, incorrect_counts, width, label="Incorrect", color="#e74c3c", alpha=0.8)
    
    ax2.set_xlabel("Category", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Count", fontsize=12, fontweight="bold")
    ax2.set_title("Correct vs Incorrect Predictions", fontsize=14, fontweight="bold")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(categories, rotation=15, ha="right")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)
    
    # Add value labels
    for i, (corr, incorr) in enumerate(zip(correct_counts, incorrect_counts)):
        ax2.text(i - width/2, corr + 1, str(corr), ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax2.text(i + width/2, incorr + 1, str(incorr), ha="center", va="bottom", fontsize=9, fontweight="bold")
    
    plt.tight_layout()
    output_path = Path(OUTPUT_FOLDER) / "error_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def create_category_performance_heatmap(all_metrics: dict):
    """Create a heatmap of all metrics across all categories."""
    categories = list(all_metrics.keys())
    metrics_names = ["Accuracy", "Precision", "Recall", "F1 Score", "Specificity"]
    
    data = []
    for cat in categories:
        data.append([
            all_metrics[cat]["accuracy"],
            all_metrics[cat]["precision"],
            all_metrics[cat]["recall"],
            all_metrics[cat]["f1"],
            all_metrics[cat]["specificity"],
        ])
    
    df_heatmap = pd.DataFrame(data, index=categories, columns=metrics_names)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        df_heatmap,
        annot=True,
        fmt=".2%",
        cmap="YlOrRd",
        vmin=0,
        vmax=1,
        ax=ax,
        cbar_kws={"label": "Score"},
        linewidths=0.5,
        linecolor="gray",
    )
    
    ax.set_title("Performance Metrics Heatmap", fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Metric", fontsize=12, fontweight="bold")
    ax.set_ylabel("Category", fontsize=12, fontweight="bold")
    
    plt.tight_layout()
    output_path = Path(OUTPUT_FOLDER) / "metrics_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def create_summary_table(all_metrics: dict):
    """Create a summary table of all metrics."""
    categories = list(all_metrics.keys())
    
    summary_data = {
        "Category": categories,
        "Accuracy": [f"{all_metrics[cat]['accuracy']:.2%}" for cat in categories],
        "Precision": [f"{all_metrics[cat]['precision']:.2%}" for cat in categories],
        "Recall": [f"{all_metrics[cat]['recall']:.2%}" for cat in categories],
        "F1 Score": [f"{all_metrics[cat]['f1']:.2%}" for cat in categories],
        "Specificity": [f"{all_metrics[cat]['specificity']:.2%}" for cat in categories],
        "TP": [all_metrics[cat]["tp"] for cat in categories],
        "TN": [all_metrics[cat]["tn"] for cat in categories],
        "FP": [all_metrics[cat]["fp"] for cat in categories],
        "FN": [all_metrics[cat]["fn"] for cat in categories],
    }
    
    df_summary = pd.DataFrame(summary_data)
    
    # Save to CSV
    output_path = Path(OUTPUT_FOLDER) / "summary_metrics.csv"
    df_summary.to_csv(output_path, index=False)
    print(f"Saved: {output_path}")
    
    # Create visual table
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis("tight")
    ax.axis("off")
    
    table = ax.table(
        cellText=df_summary.values,
        colLabels=df_summary.columns,
        cellLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(df_summary.columns)):
        table[(0, i)].set_facecolor("#3498db")
        table[(0, i)].set_text_props(weight="bold", color="white")
    
    # Alternate row colors
    for i in range(1, len(df_summary) + 1):
        if i % 2 == 0:
            for j in range(len(df_summary.columns)):
                table[(i, j)].set_facecolor("#ecf0f1")
    
    plt.title("Summary Metrics Table", fontsize=16, fontweight="bold", pad=20)
    plt.tight_layout()
    
    output_path = Path(OUTPUT_FOLDER) / "summary_table.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {output_path}")
    plt.close()


def main():
    """Main function to generate all analyses."""
    print("Loading data...")
    df = load_data(CSV_FILE)
    print(f"Loaded {len(df)} rows")
    
    # Create output folder
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(exist_ok=True)
    
    print("\nGenerating confusion matrices...")
    all_metrics = create_confusion_matrices(df)
    
    print("\nGenerating metrics comparison...")
    create_metrics_comparison(all_metrics)
    
    print("\nGenerating error analysis...")
    create_error_analysis(df)
    
    print("\nGenerating metrics heatmap...")
    create_category_performance_heatmap(all_metrics)
    
    print("\nGenerating summary table...")
    create_summary_table(all_metrics)
    
    print("\n" + "=" * 80)
    print("Analysis complete! All charts saved to:", OUTPUT_FOLDER)
    print("=" * 80)


if __name__ == "__main__":
    main()

