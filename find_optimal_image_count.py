"""
Image Count Saturation Tester
Tests different image counts (up to 10,000) with 8 Workers.
Generates a "Speedup vs Dataset Size" graph to identify the saturation point.
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

def measure_time(func, *args, **kwargs):
    """Helper to measure execution time of a function."""
    start = time.time()
    func(*args, **kwargs)
    return time.time() - start

def test_image_count(image_count, workers):
    """
    Test a specific image count with all 3 parallel methods + Serial.
    """
    INPUT_DIR = "images"
    
    # 1. Load images
    print(f"  Loading {image_count} images...", end="", flush=True)
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=image_count)
    actual_count = len(all_image_paths)
    
    if actual_count < image_count:
        print(f" (Limited to {actual_count})")
    else:
        print(" Done!")

    # 2. Prepare Tasks
    # We use a dummy output folder and DISABLE saving (False) to measure pure CPU performance
    current_paths = all_image_paths[:actual_count]
    tasks = [(p, "outputs_test", False) for p in current_paths]
    
    results = {}
    
    # 3. Run Benchmarks
    print(f"Running: ", end="", flush=True)
    
    # A. Sequential (1 Worker) - The Baseline
    print("Serial...", end="", flush=True)
    results['Sequential'] = measure_time(method_mp.run_multiprocessing, tasks, 1)
    
    # B. Multiprocessing
    print(f" MP({workers})...", end="", flush=True)
    results['MP'] = measure_time(method_mp.run_multiprocessing, tasks, workers)
    
    # C. CF Process
    print(f" CF_Proc({workers})...", end="", flush=True)
    results['CF_Proc'] = measure_time(method_cf.run, tasks, workers, mode='process')
    
    # D. CF Thread
    print(f" CF_Thread({workers})...", end="", flush=True)
    results['CF_Thread'] = measure_time(method_cf.run, tasks, workers, mode='thread')
    
    print(" Done.")
    return actual_count, results

def main():
    print("=" * 70)
    print("SATURATION TEST: Finding the Optimal Dataset Size")
    print("=" * 70)
    
    # --- CONFIGURATION ---
    TARGET_COUNTS = [100, 500, 1000, 2000, 4000, 6000, 8000, 10000]
    WORKERS = 8  
    
    print(f"Configuration:")
    print(f"  Targets: {TARGET_COUNTS}")
    print(f"  Workers: {WORKERS}")
    print("-" * 70)
    
    all_results = {}
    max_images_reached = False
    
    # --- TEST LOOP ---
    for target in TARGET_COUNTS:
        if max_images_reached:
            break
            
        print(f"\nTest Target: {target}")
        try:
            actual, times = test_image_count(target, WORKERS)
            all_results[actual] = times
            
            if actual < target:
                print(f"  ! Max dataset size reached ({actual}). Stopping further tests.")
                max_images_reached = True
                
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    # --- SAVE RAW DATA TO CSV ---
    csv_path = "saturation_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Image_Count', 'Method', 'Time_Seconds'])
        for count, times in all_results.items():
            for method, t in times.items():
                writer.writerow([count, method, t])
    print(f"\nSaved raw data to {csv_path}")

    # --- PRINT SUMMARY TABLE ---
    print("\n" + "=" * 90)
    print(f"SUMMARY (Speedup based on MP vs Serial)")
    print("-" * 90)
    print(f"{'Images':<10} | {'Serial (s)':<12} | {'MP (s)':<12} | {'MP Speedup':<12} | {'Status':<15}")
    print("-" * 90)
    
    counts = sorted(all_results.keys())
    previous_speedup = 0
    
    for count in counts:
        t_serial = all_results[count]['Sequential']
        t_mp = all_results[count]['MP']
        
        # Calculate Speedup Formula: Serial / Parallel
        speedup = t_serial / t_mp if t_mp > 0 else 0
        
        diff = abs(speedup - previous_speedup)
        
        if count == counts[0]:
            status = "Baseline"
        elif diff < 0.05:
            status = "SATURATED (Flat)"
        elif speedup > previous_speedup:
            status = "Improving"
        else:
            status = "Regression"
            
        previous_speedup = speedup
        print(f"{count:<10} | {t_serial:<12.4f} | {t_mp:<12.4f} | {speedup:<12.2f}x | {status:<15}")
    
    print("-" * 90)

    # --- GENERATE SPEEDUP PLOT ---
    print("\nGenerating Speedup Plot...")
    plt.figure(figsize=(12, 7))
    
    # We only plot the parallel methods (Speedup relative to Serial)
    parallel_methods = ['MP', 'CF_Proc', 'CF_Thread']
    colors = {'MP': 'blue', 'CF_Proc': 'orange', 'CF_Thread': 'green'}
    markers = {'MP': '^', 'CF_Proc': 's', 'CF_Thread': 'D'}
    
    x_vals = sorted(all_results.keys())
    
    for method in parallel_methods:
        # Calculate Speedup list for this method
        # Speedup = Serial_Time / Method_Time
        y_speedups = []
        for count in x_vals:
            t_serial = all_results[count]['Sequential']
            t_parallel = all_results[count][method]
            val = t_serial / t_parallel if t_parallel > 0 else 0
            y_speedups.append(val)
            
        plt.plot(x_vals, y_speedups, marker=markers[method], label=method, color=colors[method], linewidth=2.5)

    # Plot Ideal Line (y = Workers)? No, usually too high.
    # Let's plot the "Serial Baseline" at y=1 for reference
    plt.axhline(y=1, color='red', linestyle='--', label='Serial Baseline (1.0x)', alpha=0.7)

    plt.title(f'Speedup Ratio vs Dataset Size ({WORKERS} Workers)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Images (Dataset Size)', fontsize=12)
    plt.ylabel('Speedup Factor (Higher is Better)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save
    os.makedirs("plots", exist_ok=True)
    plot_path = "plots/plot_saturation_speedup.png"
    plt.savefig(plot_path, dpi=300)
    print(f"✓ Speedup Graph saved to {plot_path}")
    print("=" * 90)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()