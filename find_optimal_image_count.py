"""
Image Count Optimizer
Tests different image counts (50 to 3000) to find the optimal dataset size
for the CST435 assignment. Compares all 4 execution modes:
- Sequential (1 worker baseline)
- Multiprocessing (MP)
- Concurrent Futures Process (CF_Proc)
- Concurrent Futures Thread (CF_Thread)
"""

import time
import csv
import os
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import utils
import method_mp
import method_cf


def test_image_count(image_count, workers=4):
    """
    Test a specific image count with all 4 execution methods.
    
    Args:
        image_count: Number of images to test
        workers: Number of workers to use (default: 4)
    
    Returns:
        dict: Results {method: execution_time}
    """
    INPUT_DIR = "images"
    
    # Load images
    print(f"  Loading {image_count} images...", end="", flush=True)
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=image_count)
    
    if len(all_image_paths) < image_count:
        actual_count = len(all_image_paths)
        print(f" (only {actual_count} available)")
        image_count = actual_count
    else:
        print(" Done!")
    
    # Slice paths and create tasks
    current_paths = all_image_paths[:image_count]
    tasks = [(p, "outputs", False) for p in current_paths]
    
    results = {}
    
    # Test Sequential (1 worker)
    print(f"    Testing Sequential (1 worker)...", end="", flush=True)
    start = time.time()
    method_mp.run_multiprocessing(tasks, 1)
    results['Sequential'] = time.time() - start
    print(f" {results['Sequential']:.4f}s")
    
    # Test Multiprocessing
    print(f"    Testing Multiprocessing ({workers} workers)...", end="", flush=True)
    start = time.time()
    method_mp.run_multiprocessing(tasks, workers)
    results['MP'] = time.time() - start
    print(f" {results['MP']:.4f}s")
    
    # Test CF Process
    print(f"    Testing CF_Proc ({workers} workers)...", end="", flush=True)
    start = time.time()
    method_cf.run(tasks, workers, mode='process')
    results['CF_Proc'] = time.time() - start
    print(f" {results['CF_Proc']:.4f}s")
    
    # Test CF Thread
    print(f"    Testing CF_Thread ({workers} workers)...", end="", flush=True)
    start = time.time()
    method_cf.run(tasks, workers, mode='thread')
    results['CF_Thread'] = time.time() - start
    print(f" {results['CF_Thread']:.4f}s")
    
    return image_count, results


def main():
    """Main execution: Test different image counts and generate analysis."""
    
    print("=" * 70)
    print("IMAGE COUNT OPTIMIZER - Finding Optimal Dataset Size")
    print("=" * 70)
    
    # Configuration
    IMAGE_COUNTS = [1, 5, 10, 25, 50, 100, 500, 1000, 1500, 2000, 3000]
    WORKERS = 4  # Use 4 workers for fair comparison
    
    print(f"\nConfiguration:")
    print(f"  Image Counts: {IMAGE_COUNTS}")
    print(f"  Workers: {WORKERS}")
    print(f"  Methods: Sequential, MP, CF_Proc, CF_Thread")
    print("\n" + "=" * 70)
    
    # Collect results
    all_results = defaultdict(lambda: defaultdict(float))
    csv_rows = []
    
    # Test each image count
    for img_count in IMAGE_COUNTS:
        print(f"\nTesting with {img_count} images:")
        
        try:
            actual_count, results = test_image_count(img_count, WORKERS)
            
            # Store results
            for method, exec_time in results.items():
                all_results[actual_count][method] = exec_time
                csv_rows.append({
                    'Image_Count': actual_count,
                    'Method': method,
                    'Time_Seconds': exec_time
                })
            
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    # Save to CSV
    csv_path = "image_count_analysis.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Image_Count', 'Method', 'Time_Seconds'])
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"\n{'=' * 70}")
    print(f"Results saved to {csv_path}")
    print(f"{'=' * 70}\n")
    
    # Generate summary table
    print("SUMMARY: Execution Time (seconds)")
    print("-" * 80)
    print(f"{'Images':<12} {'Sequential':<15} {'MP':<15} {'CF_Proc':<15} {'CF_Thread':<15}")
    print("-" * 80)
    
    for img_count in sorted(all_results.keys()):
        row = f"{img_count:<12}"
        for method in ['Sequential', 'MP', 'CF_Proc', 'CF_Thread']:
            time_val = all_results[img_count].get(method, 0)
            row += f"{time_val:<15.4f}"
        print(row)
    
    print("-" * 80)
    
    # Identify best and worst cases
    print("\nANALYSIS:")
    print("-" * 80)
    
    for img_count in sorted(all_results.keys()):
        methods_times = all_results[img_count]
        if methods_times:
            best_method = min(methods_times, key=methods_times.get)
            best_time = methods_times[best_method]
            print(f"  {img_count} images: Best = {best_method} ({best_time:.4f}s)")
    
    print("\n" + "=" * 70)
    print("GENERATING PLOT...")
    print("=" * 70)
    
    # Generate plot
    plt.figure(figsize=(14, 8))
    
    colors = {
        'Sequential': 'red',
        'MP': 'blue',
        'CF_Proc': 'orange',
        'CF_Thread': 'green'
    }
    
    markers = {
        'Sequential': 'o',
        'MP': '^',
        'CF_Proc': 's',
        'CF_Thread': 'D'
    }
    
    # Plot each method
    for method in ['Sequential', 'MP', 'CF_Proc', 'CF_Thread']:
        image_counts = sorted(all_results.keys())
        times = [all_results[img][method] for img in image_counts]
        
        plt.plot(image_counts, times, 
                color=colors[method], 
                label=method, 
                linewidth=2.5)
    
    plt.title('Execution Time vs Image Count (4 Workers)', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Images', fontsize=13)
    plt.ylabel('Execution Time (seconds)', fontsize=13)
    plt.legend(fontsize=12, loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "image_count_analysis.png")
    plt.savefig(plot_path, dpi=300)
    print(f"✓ Plot saved to {plot_path}")
    plt.close()
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR ASSIGNMENT:")
    print("=" * 70)
    print("""
    Choose an image count that:
    1. Shows clear speedup differences between methods
    2. Runs in reasonable time (<2 minutes per test)
    3. Uses enough images to be statistically meaningful (>500)
    
    Suggested options:
    - Quick testing: 500 images (fast feedback)
    - Balanced: 1000 images (good analysis + reasonable time)
    - Thorough: 2000+ images (comprehensive metrics)
    """)
    print("=" * 70)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
