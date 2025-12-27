import time
import csv
import multiprocessing
import os
import argparse
import numpy as np
import utils
import method_mp
import method_cf
import matplotlib.pyplot as plt
from collections import defaultdict

def run_multiple_benchmarks(IMAGE_COUNT, WORKER_COUNTS, RUNS_PER_CONFIG, tasks, methods, raw_results, avg_data):
    """
    Execute multiple benchmark runs and calculate averages with grouped output.
    """
    print(f"Running benchmark on {IMAGE_COUNT} images with {RUNS_PER_CONFIG} runs per configuration...")
    print("-" * 50)

    # --- Iterate over runs ---
    for run_idx in range(1, RUNS_PER_CONFIG + 1):
        print(f"\n>>> Iteration {run_idx}")
        # New Header Format
        print(f"{'Workers':<10} | {'Method':<12} | {'Time (s)':<10}")
        print("-" * 40)

        for workers in WORKER_COUNTS:
            worker_label = "Serial" if workers == 1 else str(workers)
            
            # --- EXECUTE ALL 3 METHODS (Buffer results) ---
            
            # 1. Multiprocessing
            start = time.time()
            method_mp.run_multiprocessing(tasks, workers)
            dur_mp = time.time() - start
            raw_results[workers]["MP"].append(dur_mp)
            
            # 2. CF Process
            start = time.time()
            method_cf.run(tasks, workers, mode='process')
            dur_proc = time.time() - start
            raw_results[workers]["CF_Proc"].append(dur_proc)
            
            # 3. CF Thread
            start = time.time()
            method_cf.run(tasks, workers, mode='thread')
            dur_thread = time.time() - start
            raw_results[workers]["CF_Thread"].append(dur_thread)

            # --- PRINT VISUAL BLOCK (Worker label on middle row) ---
            
            # Row 1: MP (Empty Worker col)
            print(f"{'':<10} | {'MP':<12} | {dur_mp:<10.4f}")
            
            # Row 2: CF_Proc (Worker Label here)
            print(f"{worker_label:<10} | {'CF_Proc':<12} | {dur_proc:<10.4f}")
            
            # Row 3: CF_Thread (Empty Worker col)
            print(f"{'':<10} | {'CF_Thread':<12} | {dur_thread:<10.4f}")
            
            # Divider between worker groups
            print("-" * 40)

    # --- Calculate averages (Silent) ---
    for workers, worker_methods in raw_results.items():
        for method, times in worker_methods.items():
            avg = sum(times) / len(times)
            avg_data[method][workers] = avg
    """
    Execute multiple benchmark runs and calculate averages.
    """

    # --- Calculate averages ---
    for workers, worker_methods in raw_results.items():
        for method, times in worker_methods.items():
            avg = sum(times) / len(times)
            avg_data[method][workers] = avg
            # print(f"Average time for {method} with {workers} worker(s): {avg:.4f}s")




def save_and_print_results(IMAGE_COUNT, WORKER_COUNTS, RUNS_PER_CONFIG, raw_results, avg_data, methods):
    """
    Save results to CSV and print detailed analysis tables.
    """
    # --- 1. SAVE CSV ---
    csv_path = "benchmark_results_averaged.csv"
    
    with open(csv_path, 'w', newline='') as f:
        header = ['Workers', 'Run'] + methods + ['Best_Method']
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        
        for workers in sorted(WORKER_COUNTS):
            for run in range(1, RUNS_PER_CONFIG + 1):
                row = {'Workers': workers, 'Run': f'Run{run}'}
                run_times = {}
                for method in methods:
                    times = raw_results[workers].get(method, [])
                    if run <= len(times):
                        time_val = times[run - 1]
                        row[method] = f"{time_val:.4f}"
                        run_times[method] = time_val
                    else:
                        row[method] = "N/A"
                        run_times[method] = float('inf')
                
                if run_times and min(run_times.values()) != float('inf'):
                    row['Best_Method'] = min(run_times, key=run_times.get)
                else:
                    row['Best_Method'] = "N/A"
                writer.writerow(row)
    
    print(f"Results saved to {csv_path}")

    # --- 2. PRINT DETAILED PERFORMANCE ANALYSIS ---
    print("="*100)
    print("DETAILED PERFORMANCE ANALYSIS: All Runs with Speedup & Efficiency")
    print("(Serial = 1 worker baseline for speedup/efficiency calculation)")
    print("="*100)

    for workers in sorted(WORKER_COUNTS):
        print(f"\n--- Worker Count: {workers} ---")
        print("-" * 96)
        # Header: First col Left Align (<10), others Center Align (^12)
        print(f"{'Run':<10} {'MP':^12} {'CF_Proc':^12} {'CF_Thread':^12} {'Best':^12} {'Speedup':^12} {'Efficiency':^12}")
        print("-" * 96)
        
        # Print individual runs
        for run in range(1, RUNS_PER_CONFIG + 1):
            run_times = {}
            # Row Label: Left Align 10
            row_str = f"{f'Run{run}':<10}"
            
            # Collect times per method
            for method in methods:
                times = raw_results[workers].get(method, [])
                if run <= len(times):
                    time_val = times[run - 1]
                    run_times[method] = time_val
                    # Data: Center Align 12
                    row_str += f" {time_val:^12.4f}"
                else:
                    run_times[method] = float('inf')
                    row_str += f" {'N/A':^12}"
            
            # Best Method
            if run_times and min(run_times.values()) != float('inf'):
                best_method = min(run_times, key=run_times.get)
            else:
                best_method = "N/A"
            row_str += f" {best_method:^12}"

            # Speedup & Efficiency
            speedup = 0.0
            efficiency = 0.0
            
            if workers == 1:
                speedup = 1.0
                efficiency = 100.0
            else:
                baseline_times = raw_results[1].get(best_method, [])
                if run <= len(baseline_times):
                    baseline = baseline_times[run - 1]
                    current_time = run_times.get(best_method, 0)
                    if current_time > 0:
                        speedup = baseline / current_time
                        efficiency = (speedup / workers) * 100
            
            # Format Speedup and Efficiency centered
            row_str += f" {speedup:^12.4f} {f'{efficiency:.2f} %':^12}"
            print(row_str)
        
        # --- Print Average Row ---
        print("-" * 96)
        
        # Average Label: Left Align 10 (Matches 'RunX')
        avg_str = f"{'Average':<10}"

        
        
        # Averages: Center Align 12 (Matches Data Columns)
        for method in methods:
            avg_val = avg_data[method].get(workers, 0.0)
            avg_str += f" {avg_val:^12.4f}"
            
        # Dashes: Center Align 12 (Matches Best/Speedup/Eff Columns)
        avg_str += f" {'-':^12} {'-':^12} {'-':^12}"
        
        print(avg_str)
        print("-" * 96)



def run_benchmark_suite(IMAGE_COUNT, WORKER_COUNTS, RUNS_PER_CONFIG, ENABLE_MULTI_RUN, GENERATE_PLOTS):
    print("--- Starting Benchmark Suite ---")
    
    # 1. SETUP
    INPUT_DIR = os.path.join("food-101", "food-101", "images")
    
    # Load Max Images once
    print(f"Loading {IMAGE_COUNT} images from {INPUT_DIR}...")
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=IMAGE_COUNT)
    
    if len(all_image_paths) < IMAGE_COUNT:
        print(f"Warning: Only found {len(all_image_paths)} images. Adjusting limit.")
        IMAGE_COUNT = len(all_image_paths)
    
    # Slice paths
    current_paths = all_image_paths[:IMAGE_COUNT]
    tasks = [(p, "outputs", False) for p in current_paths]
        
    print(f"Configuration:")
    print(f"  Images:       {IMAGE_COUNT}")
    print(f"  Worker Counts: {WORKER_COUNTS}")
    print(f"  Runs/Config:  {RUNS_PER_CONFIG if ENABLE_MULTI_RUN else 'Single Run'}")
    print(f"  Multi-Run:    {'Enabled' if ENABLE_MULTI_RUN else 'Disabled'}")
    print(f"  Plots:        {'Enabled' if GENERATE_PLOTS else 'Disabled'}")
    print("-" * 60)
    
    # Data collection
    raw_results = defaultdict(lambda: defaultdict(list))
    avg_data = defaultdict(dict)
    methods = ['MP', 'CF_Proc', 'CF_Thread']
    
    # Execute benchmarks
    if ENABLE_MULTI_RUN:
        run_multiple_benchmarks(IMAGE_COUNT, WORKER_COUNTS, RUNS_PER_CONFIG, tasks, methods, raw_results, avg_data)
    else:
        print(f"Running benchmark on {IMAGE_COUNT} images ({RUNS_PER_CONFIG} run per config)...")
        print(f"\n{'Method':<12} | {'Workers':<10} | {'Run':<4} | {'Time (s)':<10}")
        print("-" * 50)
        for workers in WORKER_COUNTS:
            worker_label = "Serial" if workers == 1 else str(workers)
            run_idx = 1
            
            # A. Multiprocessing
            start = time.time()
            method_mp.run_multiprocessing(tasks, workers)
            duration = time.time() - start
            raw_results[workers]["MP"].append(duration)
            print(f"{'MP':<12} | {worker_label:<10} | {run_idx:<4} | {duration:<10.4f}")
            
            # B. CF Process
            start = time.time()
            method_cf.run(tasks, workers, mode='process')
            duration = time.time() - start
            raw_results[workers]["CF_Proc"].append(duration)
            print(f"{'CF_Proc':<12} | {worker_label:<10} | {run_idx:<4} | {duration:<10.4f}")
            
            # C. CF Thread
            start = time.time()
            method_cf.run(tasks, workers, mode='thread')
            duration = time.time() - start
            raw_results[workers]["CF_Thread"].append(duration)
            print(f"{'CF_Thread':<12} | {worker_label:<10} | {run_idx:<4} | {duration:<10.4f}")
        
        print("-" * 50)
        print(" Done!\n")
        
        # Calculate averages for single run mode too
        for workers, worker_methods in raw_results.items():
            for method, times in worker_methods.items():
                avg = sum(times) / len(times)
                avg_data[method][workers] = avg
    
    # Always save and print results (works for both multi-run and single-run)
    save_and_print_results(IMAGE_COUNT, WORKER_COUNTS, RUNS_PER_CONFIG, raw_results, avg_data, methods)
    
    # Generate plots if enabled (works for both single-run and multi-run modes)
    if GENERATE_PLOTS:
        print("\nGenerating 3 Analysis Plots...")
        output_dir = "plots"
        os.makedirs(output_dir, exist_ok=True)
        
        colors = {
            'MP': 'blue',
            'CF_Proc': 'orange',
            'CF_Thread': 'green'
        }
        
        labels = {
            'MP': 'Multiprocessing',
            'CF_Proc': 'CF (Process)',
            'CF_Thread': 'CF (Thread)'
        }
    
        # PLOT 1: Execution Time vs Workers (BAR CHART)
        plt.figure(figsize=(12, 7))
        x = np.arange(len(WORKER_COUNTS))
        width = 0.25
        
        for idx, method in enumerate(['MP', 'CF_Proc', 'CF_Thread']):
            workers_list = sorted(avg_data[method].keys())
            times_list = [avg_data[method][w] for w in workers_list]
            plt.bar(x + idx*width, times_list, width, label=labels[method], color=colors[method], alpha=0.8)
        
        plt.title(f'Execution Time vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Workers', fontsize=12)
        plt.ylabel('Average Execution Time (s)', fontsize=12)
        plt.xticks(x + width, [f'Serial' if w == 1 else str(w) for w in WORKER_COUNTS])
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "plot_time_vs_workers.png"), dpi=300)
        print("  > Saved plots/plot_time_vs_workers.png")
        plt.close()

        # PLOT 2: Speedup vs Workers (LINE CHART - Enhanced)
        plt.figure(figsize=(12, 7))
        styles = {
            'MP': {'marker': 'o', 'linestyle': '-', 'markersize': 8},
            'CF_Proc': {'marker': '^', 'linestyle': '--', 'markersize': 8},
            'CF_Thread': {'marker': 's', 'linestyle': '-.', 'markersize': 8}
        }
        
        for method in ['MP', 'CF_Proc', 'CF_Thread']:
            workers_list = sorted(avg_data[method].keys())
            # T(1) is baseline
            t_1 = avg_data[method].get(1)
            if not t_1: 
                continue
            
            speedups = [t_1 / avg_data[method][w] for w in workers_list]
            st = styles[method]
            plt.plot(workers_list, speedups, marker=st['marker'], linestyle=st['linestyle'], 
                     label=labels[method], color=colors[method], linewidth=2.5, markersize=st['markersize'])

        # Ideal Line
        plt.plot([1, max(WORKER_COUNTS)], [1, max(WORKER_COUNTS)], 'k--', label='Ideal Linear', alpha=0.6, linewidth=2)
        
        plt.title(f'Speedup vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Workers', fontsize=12)
        plt.ylabel('Speedup Factor', fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xticks(WORKER_COUNTS)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "plot_speedup.png"), dpi=300)
        print("  > Saved plots/plot_speedup.png")
        plt.close()

        # PLOT 3: Efficiency vs Workers (BAR CHART)
        plt.figure(figsize=(12, 7))
        x = np.arange(len(WORKER_COUNTS))
        width = 0.25
        
        for idx, method in enumerate(['MP', 'CF_Proc', 'CF_Thread']):
            workers_list = sorted(avg_data[method].keys())
            t_1 = avg_data[method].get(1)
            if not t_1:
                continue
            
            efficiencies = []
            for w in workers_list:
                speedup = t_1 / avg_data[method][w]
                eff = (speedup / w) * 100
                efficiencies.append(eff)
            
            plt.bar(x + idx*width, efficiencies, width, label=labels[method], color=colors[method], alpha=0.8)

        plt.axhline(y=100, color='k', linestyle='--', label='Ideal (100%)', alpha=0.6, linewidth=2)
        
        plt.title(f'Efficiency vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Workers', fontsize=12)
        plt.ylabel('Efficiency (%)', fontsize=12)
        plt.xticks(x + width, [f'Serial' if w == 1 else str(w) for w in WORKER_COUNTS])
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.ylim(0, 120)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "plot_efficiency.png"), dpi=300)
        plt.savefig(os.path.join(output_dir, "plot_efficiency.png"))
        print("  > Saved plots/plot_efficiency.png")
        plt.close()

        print("\n✓ Benchmark Complete!")


def parse_arguments():
    """Parse command line arguments for benchmark configuration."""
    parser = argparse.ArgumentParser(
        description='Parallel Image Processing Benchmark',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic run with 100 images, 3 runs per config
  python benchmark.py --count 100 --runs 3 --multi-run

  # Single run benchmark with 50 images
  python benchmark.py --count 50

  # Test with custom worker counts
  python benchmark.py --count 200 --workers 1 2 4 8 16 --runs 3 --multi-run

  # Generate plots without multi-run
  python benchmark.py --count 100 --runs 1 --plots
        """
    )
    
    parser.add_argument(
        '--count', 
        type=int, 
        default=50,
        help='Number of images to process (default: 50)'
    )
    
    parser.add_argument(
        '--workers', 
        type=int, 
        nargs='+', 
        default=[1, 2, 4, 8],
        help='Worker counts to test (default: 1 2 4 8)'
    )
    
    parser.add_argument(
        '--runs', 
        type=int, 
        default=1,
        help='Number of runs per configuration (default: 1)'
    )
    
    parser.add_argument(
        '--multi-run', 
        action='store_true',
        default=False,
        help='Enable multiple runs and average calculation (default: False)'
    )
    
    parser.add_argument(
        '--plots', 
        action='store_true',
        default=True,
        help='Generate performance plots (default: True)'
    )
    
    parser.add_argument(
        '--no-plots', 
        action='store_true',
        default=False,
        help='Disable plot generation'
    )
    
    args = parser.parse_args()
    
    # Handle plot flag
    if args.no_plots:
        args.plots = False
    
    return args


if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Run benchmark with parsed arguments
    run_benchmark_suite(
        IMAGE_COUNT=args.count,
        WORKER_COUNTS=args.workers,
        RUNS_PER_CONFIG=args.runs,
        ENABLE_MULTI_RUN=args.multi_run,
        GENERATE_PLOTS=args.plots
    )
