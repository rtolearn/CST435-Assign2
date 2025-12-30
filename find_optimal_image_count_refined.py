"""
Dataset Size Optimizer (Refined)
Identifies the exact image count needed for stability.
Includes Cool-down and Memory Cleanup to prevent false drops.
"""

import time
import csv
import os
import multiprocessing
import gc  # <--- NEW: Garbage Collection
import matplotlib.pyplot as plt
import utils
import method_mp
import method_cf

# --- HELPER: ROBUST TIMER ---
def measure_time(func, *args, **kwargs):
    """
    Measures execution time with system stabilization.
    """
    # 1. Cool Down: Let CPU sleep to reset burst credits/heat
    time.sleep(2) 
    
    # 2. Cleanup: Force Python to clear old memory before starting
    gc.collect()
    
    # 3. Measure
    start = time.time()
    func(*args, **kwargs)
    end = time.time()
    
    return end - start

def test_image_count(image_count, workers):
    """
    Test a specific image count with all 3 parallel methods + Serial.
    """
    INPUT_DIR = "images"
    
    print(f"  Loading {image_count} paths...", end="", flush=True)
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=image_count)
    actual_count = len(all_image_paths)
    
    if actual_count < image_count:
        print(f" (Limited to {actual_count})")
    else:
        print(" Done.")

    # DISABLE SAVING (False) to test pure CPU Scalability
    tasks = [(p, "outputs_test", False) for p in all_image_paths[:actual_count]]
    
    results = {}
    
    print(f"    Running: ", end="", flush=True)
    
    # A. Sequential (Baseline)
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
    # We test up to 8000. 10,000 might take too long for Serial.
    TARGET_COUNTS = [100, 500, 1000, 2000, 4000, 6000, 8000, 10000]
    WORKERS = 8  
    
    print(f"Configuration:")
    print(f"  Targets: {TARGET_COUNTS}")
    print(f"  Workers: {WORKERS}")
    print("-" * 70)
    
    all_results = {}
    max_reached = False
    
    # --- TEST LOOP ---
    for target in TARGET_COUNTS:
        if max_reached: break
            
        print(f"\nTest Target: {target}")
        try:
            actual, times = test_image_count(target, WORKERS)
            all_results[actual] = times
            
            if actual < target:
                print(f"  ! Max dataset size reached ({actual}). Stopping.")
                max_reached = True
                
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    # --- SAVE DATA ---
    csv_path = "saturation_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Image_Count', 'Method', 'Time_Seconds'])
        for count, times in all_results.items():
            for method, t in times.items():
                writer.writerow([count, method, t])

    # --- PRINT SUMMARY ---
    print("\n" + "=" * 90)
    print(f"SUMMARY (Speedup based on MP vs Serial)")
    print("-" * 90)
    print(f"{'Images':<10} | {'Serial(s)':<10} | {'MP(s)':<10} | {'MP Speedup':<12} | {'Status':<15}")
    print("-" * 90)
    
    counts = sorted(all_results.keys())
    prev_speedup = 0
    
    # Logic to find the "Stability Point"
    optimal_candidate = None

    for count in counts:
        t_serial = all_results[count]['Sequential']
        t_mp = all_results[count]['MP']
        
        speedup = t_serial / t_mp if t_mp > 0 else 0
        diff = speedup - prev_speedup
        
        if count == counts[0]:
            status = "Baseline"
        elif abs(diff) < 0.2: # If change is less than 0.2x, it is stable
            status = "STABLE"
            if not optimal_candidate: optimal_candidate = count
        elif speedup > prev_speedup:
            status = "Rising"
        else:
            status = "Dropping"
            
        prev_speedup = speedup
        print(f"{count:<10} | {t_serial:<10.2f} | {t_mp:<10.2f} | {speedup:<12.2f}x | {status:<15}")
    
    print("-" * 90)
    if optimal_candidate:
        print(f"Recommendation: Use {optimal_candidate} images for future tests.")
    else:
        print(f"Recommendation: Use the highest number available ({counts[-1]}).")

    # --- PLOT ---
    generate_plot(all_results, WORKERS)

def generate_plot(all_results, workers):
    print("\nGenerating Plot...")
    plt.figure(figsize=(10, 6))
    
    methods = ['MP', 'CF_Proc', 'CF_Thread']
    colors = {'MP': 'blue', 'CF_Proc': 'orange', 'CF_Thread': 'green'}
    
    x_vals = sorted(all_results.keys())
    
    for method in methods:
        y_vals = []
        for count in x_vals:
            t_serial = all_results[count]['Sequential']
            t_parallel = all_results[count][method]
            speedup = t_serial / t_parallel if t_parallel > 0 else 0
            y_vals.append(speedup)
            
        plt.plot(x_vals, y_vals, marker='o', label=method, color=colors[method])

    plt.axhline(y=1, color='red', linestyle='--', label='Serial (1.0x)')
    plt.title(f'Speedup vs Dataset Size ({workers} Workers)')
    plt.xlabel('Dataset Size (Images)')
    plt.ylabel('Speedup Factor')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/plot_saturation_speedup.png")
    print("✓ Saved to plots/plot_saturation_speedup.png")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()