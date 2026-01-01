import time
import multiprocessing
import os
import argparse
import numpy as np
import utils
import method_mp
import method_cf
import matplotlib.pyplot as plt
from collections import defaultdict

def run_benchmark_suite(IMAGE_COUNT, WORKER_COUNTS, RUNS_PER_CONFIG, GENERATE_PLOTS, SAVE_IMAGES):
    print("--- Starting Benchmark Suite ---")
    
    # 1. SETUP & DIRECTORIES
    INPUT_DIR = os.path.join("images")
    
    # Define Output Directories based on --save flag
    if SAVE_IMAGES:
        BASE_OUT = "output"
        MP_OUT = os.path.join(BASE_OUT, "mp", "images")
        CF_PROC_OUT = os.path.join(BASE_OUT, "cf_proc", "images")   # <--- Separate
        CF_THREAD_OUT = os.path.join(BASE_OUT, "cf_thread", "images")
        BENCH_OUT = os.path.join(BASE_OUT, "benchmark")
        
        # Create directories
        for folder in [MP_OUT, CF_PROC_OUT, CF_THREAD_OUT, BENCH_OUT]:
            os.makedirs(folder, exist_ok=True)
            
        print(f"Saving Enabled: Outputting to '{BASE_OUT}/'")
        plot_output_dir = BENCH_OUT  # Plots go to output/benchmark
    else:
        # Default behavior (No saving)
        MP_OUT = "outputs" 
        CF_PROC_OUT = "outputs"   # <--- Dummy path
        CF_THREAD_OUT = "outputs"
        plot_output_dir = "plots" # Default plot folder
        if GENERATE_PLOTS:
            os.makedirs(plot_output_dir, exist_ok=True)

    # 2. LOAD IMAGES
    print(f"Loading {IMAGE_COUNT} images from {INPUT_DIR}...")
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=IMAGE_COUNT)
    
    if len(all_image_paths) < IMAGE_COUNT:
        print(f"Warning: Only found {len(all_image_paths)} images. Adjusting limit.")
        IMAGE_COUNT = len(all_image_paths)
    
    # Slice paths
    current_paths = all_image_paths[:IMAGE_COUNT]

    # --- CREATE SEPARATE TASK LISTS ---
    mp_tasks = [(p, MP_OUT, SAVE_IMAGES) for p in current_paths]
    cf_proc_tasks = [(p, CF_PROC_OUT, SAVE_IMAGES) for p in current_paths]     # <--- New List
    cf_thread_tasks = [(p, CF_THREAD_OUT, SAVE_IMAGES) for p in current_paths] # <--- New List

    print(f"Configuration:")
    print(f"  Images:       {IMAGE_COUNT}")
    print(f"  Worker Counts: {WORKER_COUNTS}")
    print(f"  Runs/Config:  {RUNS_PER_CONFIG}")
    print(f"  Save Images:  {'Yes' if SAVE_IMAGES else 'No'}")
    print(f"  Plots:        {'Yes' if GENERATE_PLOTS else 'No'}")
    print("-" * 60)

    # 3. EXECUTION LOOP
    raw_results = defaultdict(lambda: defaultdict(list))
    avg_data = defaultdict(dict)
    methods = ['MP', 'CF_Proc', 'CF_Thread']

    # --- Iterate over runs ---
    for run_idx in range(1, RUNS_PER_CONFIG + 1):
        print(f"\n>>> Iteration {run_idx}")
        # Header Format
        print(f"{'Workers':<10} | {'Method':<12} | {'Time (s)':<10}")
        print("-" * 40)

        for workers in WORKER_COUNTS:
            worker_label = "Serial" if workers == 1 else str(workers)
            
            # --- EXECUTE ALL 3 METHODS ---
            
            # 1. Multiprocessing
            start = time.time()
            method_mp.run_multiprocessing(mp_tasks, workers)  # Correct
            dur_mp = time.time() - start
            raw_results[workers]["MP"].append(dur_mp)
            
            # 2. CF Process
            start = time.time()
            # CHANGE: Use 'cf_proc_tasks'
            method_cf.run(cf_proc_tasks, workers, mode='process') 
            dur_proc = time.time() - start
            raw_results[workers]["CF_Proc"].append(dur_proc)
            
            # 3. CF Thread
            start = time.time()
            # CHANGE: Use 'cf_thread_tasks'
            method_cf.run(cf_thread_tasks, workers, mode='thread')
            dur_thread = time.time() - start
            raw_results[workers]["CF_Thread"].append(dur_thread)
            
            # --- PRINT VISUAL BLOCK ---
            print(f"{'':<10} | {'MP':<12} | {dur_mp:<10.4f}")
            print(f"{worker_label:<10} | {'CF_Proc':<12} | {dur_proc:<10.4f}")
            print(f"{'':<10} | {'CF_Thread':<12} | {dur_thread:<10.4f}")
            print("-" * 40)

    # 4. CALCULATE AVERAGES
    for workers, worker_methods in raw_results.items():
        for method, times in worker_methods.items():
            avg = sum(times) / len(times)
            avg_data[method][workers] = avg

    # 5. PRINT SUMMARY & SAVE PLOTS
    save_and_print_results(WORKER_COUNTS, RUNS_PER_CONFIG, raw_results, avg_data, methods)
    
    if GENERATE_PLOTS:
        generate_plots(IMAGE_COUNT, WORKER_COUNTS, avg_data, plot_output_dir)

def save_and_print_results(WORKER_COUNTS, RUNS_PER_CONFIG, raw_results, avg_data, methods):
    COL_WIDTH = 12
    print("\n" + "=" * 65)
    print("DETAILED PERFORMANCE ANALYSIS (Per Worker, Per Paradigm)")
    print("=" * 65)

    for workers in sorted(WORKER_COUNTS):
        worker_label = "Serial" if workers == 1 else str(workers)
        print(f"\n--- Worker Count: {worker_label} ---")
        print("-" * 50)

        # Header
        header = f"{'Run':<8}"
        for method in methods:
            header += f"{method:<{COL_WIDTH}}"
        print(header)
        print("-" * 50)

        # Runs
        for run_idx in range(RUNS_PER_CONFIG):
            row = f"{'Run' + str(run_idx + 1):<8}"
            for method in methods:
                time_val = raw_results[workers][method][run_idx]
                row += f"{time_val:<{COL_WIDTH}.4f}"
            print(row)

        print("-" * 50)
        # Average
        avg_row = f"{'Average':<8}"
        for method in methods:
            avg_time = avg_data[method][workers]
            avg_row += f"{avg_time:<{COL_WIDTH}.4f}"
        print(avg_row)
        
        # Speedup
        speedup_row = f"{'Speedup':<8}"
        for method in methods:
            t1 = avg_data[method][1]
            tn = avg_data[method][workers]
            speedup = (t1 / tn) if workers != 1 else 1.0
            speedup_row += f"{speedup:<{COL_WIDTH}.4f}"
        print(speedup_row)

        # Efficiency
        eff_row = f"{'Eff(%)':<8}"
        for method in methods:
            t1 = avg_data[method][1]
            tn = avg_data[method][workers]
            speedup = (t1 / tn) if workers != 1 else 1.0
            efficiency = (speedup / workers) * 100 if workers != 1 else 100.0
            eff_row += f"{efficiency:<{COL_WIDTH}.2f}"
        print(eff_row)
        
        print("-" * 50)
        
        # --- DETERMINE BEST METHOD ---
        # Logic: Find the method with the minimum average time for this worker count
        candidates = [(m, avg_data[m][workers]) for m in methods]
        best_method, best_time = min(candidates, key=lambda x: x[1])
        
        print(f"{'Best:':<8}{best_method}")
        print("-" * 50)

def generate_plots(IMAGE_COUNT, WORKER_COUNTS, avg_data, output_dir):
    print(f"\nGenerating 3 Analysis Plots in '{output_dir}/'...")
    
    colors = {'MP': 'blue', 'CF_Proc': 'orange', 'CF_Thread': 'green'}
    labels = {'MP': 'Multiprocessing', 'CF_Proc': 'CF (Process)', 'CF_Thread': 'CF (Thread)'}

    # PLOT 1: Execution Time
    plt.figure(figsize=(10, 6))
    for method in ['MP', 'CF_Proc', 'CF_Thread']:
        workers_list = sorted(avg_data[method].keys())
        times_list = [avg_data[method][w] for w in workers_list]
        plt.plot(workers_list, times_list, marker='o', label=labels[method], color=colors[method], linewidth=2)
    
    plt.title(f'Execution Time vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Workers', fontsize=12)
    plt.ylabel('Time (s)', fontsize=12)
    plt.xticks(WORKER_COUNTS)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(output_dir, "plot_time_vs_workers.png"), dpi=300)
    plt.close()

    # PLOT 2: Speedup
    plt.figure(figsize=(10, 6))
    for method in ['MP', 'CF_Proc', 'CF_Thread']:
        workers_list = sorted(avg_data[method].keys())
        t_1 = avg_data[method][1]
        speedups = [t_1 / avg_data[method][w] for w in workers_list]
        plt.plot(workers_list, speedups, marker='o', label=labels[method], color=colors[method], linewidth=2)
    
    plt.plot([1, max(WORKER_COUNTS)], [1, max(WORKER_COUNTS)], 'k--', label='Ideal Linear', alpha=0.6)
    plt.title(f'Speedup vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Workers', fontsize=12)
    plt.ylabel('Speedup Factor', fontsize=12)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.xticks(WORKER_COUNTS)
    plt.savefig(os.path.join(output_dir, "plot_speedup.png"), dpi=300)
    plt.close()

    # PLOT 3: Efficiency
    plt.figure(figsize=(10, 6))
    for method in ['MP', 'CF_Proc', 'CF_Thread']:
        workers_list = sorted(avg_data[method].keys())
        t_1 = avg_data[method][1]
        effs = []
        for w in workers_list:
            speedup = t_1 / avg_data[method][w]
            val = (speedup/w)*100 if w!=1 else 100.0
            effs.append(val)
        plt.plot(workers_list, effs, marker='o', label=labels[method], color=colors[method], linewidth=2)

    plt.axhline(y=100, color='k', linestyle='--', label='Ideal', alpha=0.6)
    plt.title(f'Efficiency vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Workers', fontsize=12)
    plt.ylabel('Efficiency (%)', fontsize=12)
    plt.xticks(WORKER_COUNTS)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.ylim(0, 120)
    plt.savefig(os.path.join(output_dir, "plot_efficiency.png"), dpi=300)
    plt.close()
    
    print("Plots saved successfully.")

def parse_arguments():
    """
    Command-Line Interface: Configures runtime parameters.
    
    Responsibilities:
    1. Parameterization: Allows customization of image count, worker counts, and run iterations.
    2. Feature Toggles: Handles flags for saving output images and generating visual reports.
    """
    parser = argparse.ArgumentParser(description='Parallel Image Processing Benchmark')
    
    parser.add_argument('--count', type=int, default=50, help='Number of images')
    parser.add_argument('--workers', type=int, nargs='+', default=[1, 2, 4, 8], help='Worker counts')
    parser.add_argument('--runs', type=int, default=1, help='Runs per configuration')
    parser.add_argument('--multi-run', action='store_true', help='Deprecated: Multirun is now automatic if runs > 1')
    parser.add_argument('--plots', action='store_true', default=True, help='Generate plots')
    parser.add_argument('--no-plots', action='store_true', help='Disable plots')
    
    # NEW ARGUMENT
    parser.add_argument('--save', action='store_true', default=False, help='Save processed images to /output folder')
    
    args = parser.parse_args()
    if args.no_plots: args.plots = False
    return args

if __name__ == "__main__":
    multiprocessing.freeze_support()
    args = parse_arguments()
    
    run_benchmark_suite(
        IMAGE_COUNT=args.count,
        WORKER_COUNTS=args.workers,
        RUNS_PER_CONFIG=args.runs,
        GENERATE_PLOTS=args.plots,
        SAVE_IMAGES=args.save
    )