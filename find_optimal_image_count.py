"""
Dataset Size Optimizer (Clean Headers)
Identifies the exact image count needed for stability.
Saves all reports and plots to the 'outputs/' folder.
"""

import time
import csv
import os
import multiprocessing
import gc
import matplotlib.pyplot as plt
import utils
import method_mp
import method_cf

# --- CONFIGURATION: OUTPUT DIRECTORY ---
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- HELPER: ROBUST TIMER ---
def measure_time(func, *args, **kwargs):
    """
    Measures execution time with system stabilization.
    """
    time.sleep(1) # Short cool down
    gc.collect()  # Force cleanup
    
    start = time.time()
    func(*args, **kwargs)
    end = time.time()
    
    return end - start

def test_image_count(image_count, workers):
    """
    Test a specific image count with all 3 parallel methods + Serial.
    """
    INPUT_DIR = "images"
    # Update: Put generated images in outputs folder (even if saving is False)
    IMG_OUT_DIR = os.path.join(OUTPUT_DIR, "test_images")
    
    # 1. Load Data
    print(f"\n[ Dataset: {image_count} Images ] Loading...", end="", flush=True)
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=image_count)
    actual_count = len(all_image_paths)
    print(f" Loaded {actual_count}.")

    # Tasks (Saving Disabled for pure CPU testing)
    tasks = [(p, IMG_OUT_DIR, False) for p in all_image_paths[:actual_count]]
    results = {}
    
    # 2. Run Tests
    print(f"  Running: Serial...", end="", flush=True)
    results['Serial'] = measure_time(method_mp.run_multiprocessing, tasks, 1)
    
    print(f" | MP...", end="", flush=True)
    results['MP'] = measure_time(method_mp.run_multiprocessing, tasks, workers)
    
    print(f" | CF_Proc...", end="", flush=True)
    results['CF_Proc'] = measure_time(method_cf.run, tasks, workers, mode='process')
    
    print(f" | CF_Thread...", end="", flush=True)
    results['CF_Thread'] = measure_time(method_cf.run, tasks, workers, mode='thread')
    
    print(" Done.")
    return actual_count, results

def print_batch_analysis(count, results, workers):
    """
    Prints a detailed table for the specific batch just run.
    """
    t_serial = results['Serial']
    
    print("-" * 65)
    print(f"{'Method':<15} | {'Time (s)':<10} | {'Speedup':<10} | {'Efficiency':<10}")
    print("-" * 65)
    
    # Print Serial First
    print(f"{'Serial (1 Core)':<15} | {t_serial:<10.4f} | {'1.00x':<10} | {'100%':<10}")
    
    # Print Parallel Methods
    for method in ['MP', 'CF_Proc', 'CF_Thread']:
        t_curr = results[method]
        
        # Calculate Speedup (Serial / Parallel)
        speedup = t_serial / t_curr if t_curr > 0 else 0
        
        # Calculate Efficiency (Speedup / Workers)
        efficiency = (speedup / workers) * 100
        
        print(f"{method:<15} | {t_curr:<10.4f} | {speedup:<9.2f}x | {efficiency:<9.1f}%")
    print("-" * 65)

def main():
    # --- CONFIGURATION ---
    TARGET_COUNTS = [100, 500, 1000, 2000, 4000, 6000, 8000, 10000]
    WORKERS = 8  
    
    print("=" * 70)
    print(f"SATURATION TEST: Optimizing for {WORKERS} Cores")
    print(f"Output Directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 70)
    
    all_results = {}
    max_reached = False
    
    # --- TEST LOOP ---
    for target in TARGET_COUNTS:
        if max_reached: break
            
        try:
            # 1. Run Test
            actual, times = test_image_count(target, WORKERS)
            all_results[actual] = times
            
            # 2. Print Immediate Detailed Analysis
            print_batch_analysis(actual, times, WORKERS)
            
            if actual < target:
                print(f"  ! Max dataset size reached ({actual}). Stopping loop.")
                max_reached = True
                
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    # --- SAVE CSV ---
    csv_path = os.path.join(OUTPUT_DIR, "saturation_results.csv")
    try:
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Image_Count', 'Method', 'Time', 'Speedup', 'Efficiency'])
            for count, times in all_results.items():
                t_serial = times['Serial']
                for method, t in times.items():
                    speedup = t_serial / t if t > 0 else 0
                    eff = (speedup / WORKERS) if method != 'Serial' else 1.0
                    writer.writerow([count, method, t, speedup, eff])
        print(f"\n[Saved] Data saved to {csv_path}")
    except Exception as e:
        print(f"Could not save CSV: {e}")

    # --- FINAL EXECUTIVE SUMMARY ---
    print("\n" + "=" * 85)
    print(f"EXECUTIVE SUMMARY: Speedup Matrix")
    print("-" * 85)
    
    # UPDATED HEADER: Removed (s) and (x)
    print(f"{'Images':<8} | {'Serial':<10} || {'MP':<10} | {'CF_P':<10} | {'CF_T':<10} || {'Winner':<10}")
    print("-" * 85)
    
    for count in sorted(all_results.keys()):
        res = all_results[count]
        t_serial = res['Serial']
        
        # Calculate Speedups
        s_mp = t_serial / res['MP'] if res['MP'] > 0 else 0
        s_cf_p = t_serial / res['CF_Proc'] if res['CF_Proc'] > 0 else 0
        s_cf_t = t_serial / res['CF_Thread'] if res['CF_Thread'] > 0 else 0
        
        # Find Winner
        best_val = max(s_mp, s_cf_p, s_cf_t)
        if best_val == s_mp: winner = "MP"
        elif best_val == s_cf_p: winner = "CF_Proc"
        else: winner = "CF_Thread"
        
        print(f"{count:<8} | {t_serial:<10.2f} || {s_mp:<10.2f} | {s_cf_p:<10.2f} | {s_cf_t:<10.2f} || {winner:<10}")
    
    print("-" * 85)
    generate_plot(all_results, WORKERS)

def generate_plot(all_results, workers):
    print("Generating Plot...")
    plt.figure(figsize=(10, 6))
    
    methods = ['MP', 'CF_Proc', 'CF_Thread']
    colors = {'MP': 'blue', 'CF_Proc': 'orange', 'CF_Thread': 'green'}
    
    x_vals = sorted(all_results.keys())
    
    for method in methods:
        y_vals = []
        for count in x_vals:
            t_serial = all_results[count]['Sequential'] if 'Sequential' in all_results[count] else all_results[count]['Serial']
            t_parallel = all_results[count][method]
            speedup = t_serial / t_parallel if t_parallel > 0 else 0
            y_vals.append(speedup)
            
        plt.plot(x_vals, y_vals, marker='o', label=method, color=colors[method])

    plt.axhline(y=1, color='red', linestyle='--', label='Serial (1.0x)')
    plt.axhline(y=workers, color='gray', linestyle=':', label=f'Ideal ({workers}x)')
    
    plt.title(f'Method Comparison: Speedup vs Dataset Size ({workers} Workers)')
    plt.xlabel('Dataset Size (Images)')
    plt.ylabel('Speedup Factor')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save to Outputs folder
    save_path = os.path.join(OUTPUT_DIR, "saturation_summary.png")
    plt.savefig(save_path)
    print(f"✓ Plot saved to {save_path}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()