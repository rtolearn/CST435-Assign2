import time
import csv
import multiprocessing
import os
import utils
import method_mp
import method_cf
import matplotlib.pyplot as plt
from collections import defaultdict

def run_benchmark_suite():
    print("--- Starting Averaged Benchmark Suite (3 Runs) ---")
    
    # 1. SETUP
    INPUT_DIR = os.path.join("food-101", "food-101", "images")
    
    # CONFIGURATION
    IMAGE_COUNT = 500  # Fixed number as requested
    WORKER_COUNTS = [1, 2, 4, 8]
    RUNS_PER_CONFIG = 3 # Number of times to repeat each test
    
    # Load Max Images once
    print(f"Loading {IMAGE_COUNT} images cache from {INPUT_DIR}...")
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=IMAGE_COUNT)
    
    if len(all_image_paths) < IMAGE_COUNT:
        print(f"Warning: Only found {len(all_image_paths)} images. Adjusting limit.")
        IMAGE_COUNT = len(all_image_paths)
    
    # Slice paths
    current_paths = all_image_paths[:IMAGE_COUNT]
    tasks = [(p, "outputs", False) for p in current_paths]
        
    print(f"Testing Speed for {IMAGE_COUNT} Images")
    print(f"Worker Counts: {WORKER_COUNTS}")
    print(f"Runs per Config: {RUNS_PER_CONFIG}")
    print("-" * 60)
    
    # Data collection
    # raw_results stores list of times: raw_results[workers][method] = [t1, t2, t3]
    raw_results = defaultdict(lambda: defaultdict(list))
    csv_rows = []
    
    # 2. EXECUTION LOOP
    print(f"{'Method':<12} | {'Workers':<8} | {'Run':<4} | {'Time (s)':<10}")
    print("-" * 50)

    for workers in WORKER_COUNTS:
        for run_idx in range(1, RUNS_PER_CONFIG + 1):
            
            # Function to execute and record
            def execute_method(name, func):
                start = time.time()
                func()
                duration = time.time() - start
                
                raw_results[workers][name].append(duration)
                print(f"{name:<12} | {workers:<8} | {run_idx:<4} | {duration:<10.4f}")
                
                csv_rows.append({
                    "Images": IMAGE_COUNT,
                    "Workers": workers,
                    "Method": name,
                    "Run": run_idx,
                    "Time": duration
                })

            # A. Multiprocessing
            execute_method("MP", lambda: method_mp.run_multiprocessing(tasks, workers))
            
            # B. CF Process
            execute_method("CF_Proc", lambda: method_cf.run(tasks, workers, mode='process'))
            
            # C. CF Thread
            execute_method("CF_Thread", lambda: method_cf.run(tasks, workers, mode='thread'))

    # 3. SAVE CSV (Raw Data)
    csv_path = "benchmark_results_averaged.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Images", "Workers", "Method", "Run", "Time"])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nRaw results saved to {csv_path}")

    # 4. CALCULATE AVERAGES
    # avg_data[method][workers] = avg_time
    avg_data = defaultdict(dict)
    
    for workers, methods in raw_results.items():
        for method, times in methods.items():
            avg = sum(times) / len(times)
            avg_data[method][workers] = avg

    # 5. GENERATE 3 SPECIFIC PLOTS
    print("\nGenerating 3 Analysis Plots...")
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    styles = {
        'MP': {'marker': 'o', 'linestyle': '-', 'label': 'Multiprocessing', 'color': 'blue'},
        'CF_Proc': {'marker': '^', 'linestyle': '--', 'label': 'CF (Process)', 'color': 'orange'},
        'CF_Thread': {'marker': 's', 'linestyle': '-', 'label': 'CF (Thread)', 'color': 'green'}
    }
    
    # PLOT 1: Execution Time vs Workers
    plt.figure(figsize=(10, 6))
    for method in styles.keys():
        workers_list = sorted(avg_data[method].keys())
        times_list = [avg_data[method][w] for w in workers_list]
        st = styles[method]
        plt.plot(workers_list, times_list, marker=st['marker'], linestyle=st['linestyle'], 
                 label=st['label'], color=st['color'], linewidth=2)
                 
    plt.title(f'Execution Time vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Workers', fontsize=12)
    plt.ylabel('Average Execution Time (s)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(WORKER_COUNTS)
    plt.savefig(os.path.join(output_dir, "plot_time_vs_workers.png"))
    print("  > Saved plots/plot_time_vs_workers.png")
    plt.close()

    # PLOT 2: Speedup vs Workers
    plt.figure(figsize=(10, 6))
    for method in styles.keys():
        workers_list = sorted(avg_data[method].keys())
        # T(1) is baseline
        t_1 = avg_data[method].get(1)
        if not t_1: continue
        
        speedups = [t_1 / avg_data[method][w] for w in workers_list]
        st = styles[method]
        plt.plot(workers_list, speedups, marker=st['marker'], linestyle=st['linestyle'], 
                 label=st['label'], color=st['color'], linewidth=2)

    # Ideal Line
    plt.plot([1, 8], [1, 8], 'k--', label='Ideal Linear', alpha=0.5)
    
    plt.title(f'Speedup vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Workers', fontsize=12)
    plt.ylabel('Speedup Factor', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(WORKER_COUNTS)
    plt.savefig(os.path.join(output_dir, "plot_speedup.png"))
    print("  > Saved plots/plot_speedup.png")
    plt.close()

    # PLOT 3: Efficiency vs Workers
    plt.figure(figsize=(10, 6))
    for method in styles.keys():
        workers_list = sorted(avg_data[method].keys())
        t_1 = avg_data[method].get(1)
        if not t_1: continue
        
        efficiencies = []
        for w in workers_list:
            speedup = t_1 / avg_data[method][w]
            eff = (speedup / w) * 100
            efficiencies.append(eff)
            
        st = styles[method]
        plt.plot(workers_list, efficiencies, marker=st['marker'], linestyle=st['linestyle'], 
                 label=st['label'], color=st['color'], linewidth=2)

    plt.axhline(y=100, color='k', linestyle='--', label='Ideal (100%)', alpha=0.5)
    
    plt.title(f'Efficiency vs Workers ({IMAGE_COUNT} Images)', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Workers', fontsize=12)
    plt.ylabel('Efficiency (%)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(WORKER_COUNTS)
    plt.ylim(0, 110)
    plt.savefig(os.path.join(output_dir, "plot_efficiency.png"))
    print("  > Saved plots/plot_efficiency.png")
    plt.close()

    print("\n✓ Averaged Benchmark Complete!")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
