#!/usr/bin/env python3
"""
Test script for SafePost analyze endpoint with metrics and confusion matrix.
"""

import requests
import json
import csv
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration
API_URL = "http://localhost:3000/api/analyze"
TEST_IMAGES_FOLDER = "test_images"
OUTPUT_FOLDER = "test_results_output"

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# Map folder names to expected PII categories
FOLDER_TO_CATEGORY = {
    "Address": "address",
    "Email ": "emails",  # Note: folder has trailing space
    "Email": "emails",   # Handle both with and without space
    "License Plate": "licensePlates",
    "Phone Numbers": "phoneNumbers",
}


def analyze_image(image_path: Path) -> dict:
    """Send image to analyze endpoint and return result."""
    try:
        with open(image_path, "rb") as f:
            # Detect MIME type from extension
            mime_type = "image/jpeg"
            if image_path.suffix.lower() in [".png"]:
                mime_type = "image/png"
            elif image_path.suffix.lower() in [".gif"]:
                mime_type = "image/gif"
            elif image_path.suffix.lower() in [".webp"]:
                mime_type = "image/webp"
            
            files = {"image": (image_path.name, f, mime_type)}
            response = requests.post(API_URL, files=files, timeout=30)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_expected_values(folder_name: str) -> Dict[str, bool]:
    """Get expected PII values based on folder name. All images should be unsafe."""
    category = FOLDER_TO_CATEGORY.get(folder_name.strip())
    if not category:
        return {}
    
    # Verify: All images should be marked as NOT safe to post
    expected = {
        "safe": False,  # All images should be unsafe - this is always False
        "emails": category == "emails",
        "address": category == "address",
        "phoneNumbers": category == "phoneNumbers",
        "licensePlates": category == "licensePlates",
    }
    
    # Double-check: ensure safe is always False
    assert expected["safe"] == False, f"Expected safe should always be False, got {expected['safe']}"
    
    return expected


def calculate_metrics(results: List[Tuple[dict, dict, str, Path]]) -> dict:
    """Calculate accuracy, confusion matrix, and other metrics."""
    metrics = {
        "total": len(results),
        "safe_accuracy": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
        "emails": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
        "address": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
        "phoneNumbers": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
        "licensePlates": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
    }
    
    for expected, actual, _, _ in results:
        if "error" in actual:
            continue
        
        # Safe/Unsafe confusion matrix
        expected_safe = expected.get("safe", False)
        actual_safe = actual.get("safe", True)
        
        if not expected_safe and not actual_safe:
            metrics["safe_accuracy"]["tp"] += 1  # True Positive: correctly flagged unsafe
        elif expected_safe and actual_safe:
            metrics["safe_accuracy"]["tn"] += 1  # True Negative: correctly flagged safe
        elif expected_safe and not actual_safe:
            metrics["safe_accuracy"]["fp"] += 1  # False Positive: flagged unsafe when should be safe
        elif not expected_safe and actual_safe:
            metrics["safe_accuracy"]["fn"] += 1  # False Negative: flagged safe when should be unsafe
        
        # Category-specific confusion matrices
        for category in ["emails", "address", "phoneNumbers", "licensePlates"]:
            expected_val = expected.get(category, False)
            actual_val = actual.get(category, False)
            
            if expected_val and actual_val:
                metrics[category]["tp"] += 1
            elif not expected_val and not actual_val:
                metrics[category]["tn"] += 1
            elif not expected_val and actual_val:
                metrics[category]["fp"] += 1
            elif expected_val and not actual_val:
                metrics[category]["fn"] += 1
    
    return metrics


def calculate_precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    """Calculate precision, recall, and F1 score."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def print_report(metrics: dict):
    """Print comprehensive metrics report."""
    print("\n" + "=" * 80)
    print("EVALUATION REPORT")
    print("=" * 80)
    
    total = metrics["total"]
    print(f"\nTotal Images Tested: {total}\n")
    
    # Overall Safe/Unsafe Accuracy
    safe = metrics["safe_accuracy"]
    safe_accuracy = (safe["tp"] + safe["tn"]) / total if total > 0 else 0.0
    print("OVERALL SAFE/UNSAFE DETECTION")
    print("-" * 80)
    print(f"Accuracy: {safe_accuracy:.2%}")
    print(f"True Positives (correctly flagged unsafe): {safe['tp']}")
    print(f"True Negatives (correctly flagged safe): {safe['tn']}")
    print(f"False Positives (flagged unsafe when safe): {safe['fp']}")
    print(f"False Negatives (flagged safe when unsafe): {safe['fn']}")
    
    precision, recall, f1 = calculate_precision_recall_f1(safe["tp"], safe["fp"], safe["fn"])
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1 Score: {f1:.2%}")
    
    # Category-specific metrics
    print("\n" + "=" * 80)
    print("CATEGORY-SPECIFIC METRICS")
    print("=" * 80)
    
    category_names = {
        "emails": "Email Addresses",
        "address": "Addresses",
        "phoneNumbers": "Phone Numbers",
        "licensePlates": "License Plates",
    }
    
    for category, display_name in category_names.items():
        cat_metrics = metrics[category]
        tp, tn, fp, fn = cat_metrics["tp"], cat_metrics["tn"], cat_metrics["fp"], cat_metrics["fn"]
        
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision, recall, f1 = calculate_precision_recall_f1(tp, fp, fn)
        
        print(f"\n{display_name.upper()}")
        print("-" * 80)
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Precision: {precision:.2%}")
        print(f"Recall: {recall:.2%}")
        print(f"F1 Score: {f1:.2%}")
        print(f"\nConfusion Matrix:")
        print(f"  True Positives:  {tp:4d}  |  False Negatives: {fn:4d}")
        print(f"  False Positives: {fp:4d}  |  True Negatives:   {tn:4d}")
    
    # Confusion Matrix Summary
    print("\n" + "=" * 80)
    print("CONFUSION MATRIX SUMMARY")
    print("=" * 80)
    print(f"{'Category':<20} {'TP':<8} {'TN':<8} {'FP':<8} {'FN':<8} {'Accuracy':<10}")
    print("-" * 80)
    print(f"{'Safe/Unsafe':<20} {safe['tp']:<8} {safe['tn']:<8} {safe['fp']:<8} {safe['fn']:<8} {safe_accuracy:<10.2%}")
    
    for category, display_name in category_names.items():
        cat_metrics = metrics[category]
        tp, tn, fp, fn = cat_metrics["tp"], cat_metrics["tn"], cat_metrics["fp"], cat_metrics["fn"]
        accuracy = (tp + tn) / total if total > 0 else 0.0
        print(f"{display_name:<20} {tp:<8} {tn:<8} {fp:<8} {fn:<8} {accuracy:<10.2%}")
    
    print("\n" + "=" * 80)


def save_images_locally(results: List[Tuple[dict, dict, str, Path]]):
    """Copy all test images to output folder."""
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(exist_ok=True)
    
    images_folder = output_path / "images"
    images_folder.mkdir(exist_ok=True)
    
    copied_count = 0
    for expected, actual, category, image_path in results:
        # Create category subfolder
        category_folder = images_folder / category
        category_folder.mkdir(exist_ok=True)
        
        # Copy image
        dest_path = category_folder / image_path.name
        try:
            shutil.copy2(image_path, dest_path)
            copied_count += 1
        except Exception as e:
            print(f"Warning: Could not copy {image_path}: {e}")
    
    print(f"Copied {copied_count} image(s) to {images_folder}")


def save_results_csv(results: List[Tuple[dict, dict, str, Path]], csv_file: str = None):
    """Save results to CSV file."""
    if csv_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"{OUTPUT_FOLDER}/test_results_{timestamp}.csv"
    
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(exist_ok=True)
    csv_path = output_path / Path(csv_file).name
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "Image Path",
            "Category",
            "Expected Safe",
            "Actual Safe",
            "Safe Correct",
            "Expected Emails",
            "Actual Emails",
            "Emails Correct",
            "Expected Address",
            "Actual Address",
            "Address Correct",
            "Expected Phone Numbers",
            "Actual Phone Numbers",
            "Phone Numbers Correct",
            "Expected License Plates",
            "Actual License Plates",
            "License Plates Correct",
            "Message",
            "Reasoning",
            "Redaction Suggestions",
            "Error",
        ])
        
        # Data rows
        for expected, actual, category, image_path in results:
            # Verify expected safe is always False
            expected_safe = expected.get("safe", False)
            if expected_safe != False:
                print(f"WARNING: Expected safe is {expected_safe} for {image_path}, should be False")
            
            redaction_suggestions = actual.get("redactionSuggestions", [])
            redaction_str = "; ".join(redaction_suggestions) if redaction_suggestions else ""
            
            writer.writerow([
                str(image_path),
                category,
                expected_safe,
                actual.get("safe", None) if "error" not in actual else None,
                expected_safe == actual.get("safe", True) if "error" not in actual else None,
                expected.get("emails", False),
                actual.get("emails", None) if "error" not in actual else None,
                expected.get("emails", False) == actual.get("emails", False) if "error" not in actual else None,
                expected.get("address", False),
                actual.get("address", None) if "error" not in actual else None,
                expected.get("address", False) == actual.get("address", False) if "error" not in actual else None,
                expected.get("phoneNumbers", False),
                actual.get("phoneNumbers", None) if "error" not in actual else None,
                expected.get("phoneNumbers", False) == actual.get("phoneNumbers", False) if "error" not in actual else None,
                expected.get("licensePlates", False),
                actual.get("licensePlates", None) if "error" not in actual else None,
                expected.get("licensePlates", False) == actual.get("licensePlates", False) if "error" not in actual else None,
                actual.get("message", "") if "error" not in actual else "",
                actual.get("reasoning", "") if "error" not in actual else "",
                redaction_str,
                actual.get("error", "") if "error" in actual else "",
            ])
    
    print(f"Results saved to CSV: {csv_path}")


def save_detailed_results(results: List[Tuple[dict, dict, str, Path]], output_file: str = None):
    """Save detailed results including reasoning to a JSON file."""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{OUTPUT_FOLDER}/test_results_{timestamp}.json"
    
    output_path = Path(OUTPUT_FOLDER)
    output_path.mkdir(exist_ok=True)
    json_path = output_path / Path(output_file).name
    
    detailed_results = []
    
    for expected, actual, category, image_path in results:
        # Verify expected safe is always False
        expected_safe = expected.get("safe", False)
        if expected_safe != False:
            print(f"WARNING: Expected safe is {expected_safe} for {image_path}, should be False")
        
        result_entry = {
            "image": str(image_path),
            "category": category,
            "expected": expected,
            "actual": {
                "safe": actual.get("safe", None),
                "emails": actual.get("emails", None),
                "address": actual.get("address", None),
                "phoneNumbers": actual.get("phoneNumbers", None),
                "licensePlates": actual.get("licensePlates", None),
                "message": actual.get("message", None),
                "reasoning": actual.get("reasoning", None),
                "redactionSuggestions": actual.get("redactionSuggestions", []),
            },
            "correct": {
                "safe": expected_safe == actual.get("safe", True) if "error" not in actual else None,
                "emails": expected.get("emails", False) == actual.get("emails", False) if "error" not in actual else None,
                "address": expected.get("address", False) == actual.get("address", False) if "error" not in actual else None,
                "phoneNumbers": expected.get("phoneNumbers", False) == actual.get("phoneNumbers", False) if "error" not in actual else None,
                "licensePlates": expected.get("licensePlates", False) == actual.get("licensePlates", False) if "error" not in actual else None,
            },
            "error": actual.get("error", None),
        }
        detailed_results.append(result_entry)
    
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "results": detailed_results,
    }
    
    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Detailed results saved to JSON: {json_path}")


def print_reasoning_summary(results: List[Tuple[dict, dict, str, Path]]):
    """Print a summary of all reasonings."""
    print("\n" + "=" * 80)
    print("REASONING SUMMARY")
    print("=" * 80)
    
    for i, (expected, actual, category, image_path) in enumerate(results, 1):
        if "error" in actual:
            continue
        
        reasoning = actual.get("reasoning", "N/A")
        safe = actual.get("safe", True)
        expected_safe = expected.get("safe", False)
        status = "✅" if safe == expected_safe else "❌"
        
        print(f"\n[{i}] {category}/{image_path.name} {status}")
        print(f"    Reasoning: {reasoning}")
        
        # Show detected categories
        detected = []
        if actual.get("emails"):
            detected.append("emails")
        if actual.get("address"):
            detected.append("address")
        if actual.get("phoneNumbers"):
            detected.append("phoneNumbers")
        if actual.get("licensePlates"):
            detected.append("licensePlates")
        
        if detected:
            print(f"    Detected: {', '.join(detected)}")
        else:
            print(f"    Detected: none")
    
    print("\n" + "=" * 80)


def main():
    """Iterate over test images and generate evaluation report."""
    folder = Path(TEST_IMAGES_FOLDER)
    
    if not folder.exists():
        print(f"Error: Folder '{TEST_IMAGES_FOLDER}' not found.")
        print(f"Create a folder named '{TEST_IMAGES_FOLDER}' with subfolders for each PII category.")
        return
    
    # Collect all images from subfolders
    test_cases = []
    subfolders = [d for d in folder.iterdir() if d.is_dir()]
    
    if not subfolders:
        print(f"No subfolders found in '{TEST_IMAGES_FOLDER}'.")
        return
    
    print("Collecting test images...")
    for subfolder in subfolders:
        folder_name = subfolder.name
        expected = get_expected_values(folder_name)
        
        if not expected:
            print(f"Warning: Unknown folder '{folder_name}', skipping...")
            continue
        
        image_files = [
            f for f in subfolder.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]
        
        for image_path in image_files:
            test_cases.append((image_path, expected, folder_name))
    
    if not test_cases:
        print("No image files found in subfolders.")
        return
    
    print(f"Found {len(test_cases)} test image(s) across {len(subfolders)} category(ies)\n")
    print("Analyzing images...")
    print("=" * 80)
    
    results = []
    for i, (image_path, expected, category) in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] {category}/{image_path.name}...", end=" ", flush=True)
        result = analyze_image(image_path)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            actual_safe = result.get("safe", True)
            expected_safe = expected.get("safe", False)
            status = "✅" if actual_safe == expected_safe else "❌"
            print(f"{status} Safe: {actual_safe} (expected: {expected_safe})")
            reasoning = result.get("reasoning", "N/A")
            if reasoning and reasoning != "N/A":
                print(f"    💭 {reasoning}")
        
        # Store: (expected, actual, category, image_path)
        results.append((expected, result, category, image_path))
    
    # Verify all expected values have safe=False
    print("\nVerifying expected values...")
    all_safe_false = all(exp.get("safe", True) == False for exp, _, _, _ in results)
    if not all_safe_false:
        print("WARNING: Some expected values have safe=True. All should be False.")
        for i, (exp, _, cat, img) in enumerate(results, 1):
            if exp.get("safe", True) != False:
                print(f"  [{i}] {cat}/{img.name}: expected safe = {exp.get('safe')}")
    else:
        print(f"✓ All {len(results)} test cases have expected safe=False")
    
    # Calculate and print metrics
    metrics = calculate_metrics(results)
    print_report(metrics)
    
    # Print reasoning summary
    print_reasoning_summary(results)
    
    # Save all outputs
    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    save_images_locally(results)
    save_results_csv(results)
    save_detailed_results(results)


if __name__ == "__main__":
    main()
