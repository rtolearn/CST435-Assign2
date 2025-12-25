import time
import csv
import multiprocessing
import os
import utils
import method_mp
import method_cf

def run_benchmark_suite():
    print("--- Starting Benchmark Suite (3-Way Comparison) ---")
    # Setup
    INPUT_DIR = os.path.join("food-101", "food-101", "images")
    NUM_IMAGES = 50  # User requested 50 images
    
    print(f"Loading {NUM_IMAGES} images from {INPUT_DIR}...")
    image_paths = utils.get_image_paths(INPUT_DIR, limit=NUM_IMAGES)
    
    if len(image_paths) < NUM_IMAGES:
        print(f"Warning: Only found {len(image_paths)} images.")
    
    # Prepare tasks (Benchmark mode: save=False)
    tasks = [(p, "outputs", False) for p in image_paths]
    
    # Varied worker counts as requested
    worker_counts = [2, 4, 6, 8]
    print(f"Testing Worker Counts: {worker_counts}")
    print("-" * 60)
    
    # Data storage for pivoting: results[workers][method] = time
    benchmark_data = {w: {} for w in worker_counts}
    
    # Baseline (Single Core for reference, not part of comparison columns usually but good for speedup)
    # We use MP 1-core as the baseline speed
    print(f"Running Baseline (MP 1 Core) for speedup calc... ", end="", flush=True)
    start = time.time()
    method_mp.run_multiprocessing(tasks, 1)
    t_1 = time.time() - start
    print(f"Done in {t_1:.4f}s")
    
    # Plot data arrays
    plot_data = {'Multiprocessing': [], 'CF (Threads)': [], 'CF (Process)': []}

    print("\nRunning Tests...")
    
    for workers in worker_counts:
        print(f"\n--- Testing with {workers} Workers ---")
        
        # 1. Multiprocessing
        print(f"  > Multiprocessing... ", end="", flush=True)
        start = time.time()
        method_mp.run_multiprocessing(tasks, workers)
        dur = time.time() - start
        print(f"{dur:.4f}s")
        benchmark_data[workers]['MP'] = dur
        plot_data['Multiprocessing'].append((workers, dur))

        # 2. Concurrent Futures (Threads)
        print(f"  > CF (Threads)...    ", end="", flush=True)
        start = time.time()
        method_cf.run(tasks, workers, mode='thread')
        dur = time.time() - start
        print(f"{dur:.4f}s")
        benchmark_data[workers]['CF_Thread'] = dur
        plot_data['CF (Threads)'].append((workers, dur))

        # 3. Concurrent Futures (Process)
        print(f"  > CF (Process)...    ", end="", flush=True)
        start = time.time()
        method_cf.run(tasks, workers, mode='process')
        dur = time.time() - start
        print(f"{dur:.4f}s")
        benchmark_data[workers]['CF_Process'] = dur
        plot_data['CF (Process)'].append((workers, dur))

    # Print Side-by-Side Pivot Table
    print("\n" + "="*80)
    print(f"{'Workers':<8} | {'MP (s)':<10} | {'CF Proc (s)':<12} | {'CF Thrd (s)':<12} | {'Best Method':<15}")
    print("-" * 80)
    
    csv_rows = []
    for w in worker_counts:
        mp = benchmark_data[w].get('MP', 0)
        cfp = benchmark_data[w].get('CF_Process', 0)
        cft = benchmark_data[w].get('CF_Thread', 0)
        
        # Determine Winner
        times = {'Multiprocessing': mp, 'CF Process': cfp, 'CF Thread': cft}
        best_method = min(times, key=times.get)
        
        print(f"{w:<8} | {mp:<10.4f} | {cfp:<12.4f} | {cft:<12.4f} | {best_method:<15}")
        
        csv_rows.append({
            'Workers': w,
            'MP_Time': mp,
            'CF_Process_Time': cfp,
            'CF_Thread_Time': cft,
            'Winner': best_method
        })
    print("="*80)

    # Save details to CSV (Pivoted format)
    csv_path = "benchmark_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Workers", "MP_Time", "CF_Process_Time", "CF_Thread_Time", "Winner"])
        writer.writeheader()
        writer.writerows(csv_rows)
        
    print(f"\nResults saved to {csv_path}")
    
    # Generate Plot
    plot_results(plot_data)

def plot_results(data):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Skipping plot generation.")
        return

    print("Generating performance plot...")
    
    plt.figure(figsize=(10, 6))
    
    # Plot 3 Lines
    # Multiprocessing
    x_mp, y_mp = zip(*data['Multiprocessing'])
    plt.plot(x_mp, y_mp, marker='o', label='Multiprocessing (Pool)', linewidth=2)
    
    # CF Process
    x_cfp, y_cfp = zip(*data['CF (Process)'])
    plt.plot(x_cfp, y_cfp, marker='^', label='Concurrent Futures (Process)', linewidth=2, linestyle='--')

    # CF Threads
    x_cf, y_cf = zip(*data['CF (Threads)'])
    plt.plot(x_cf, y_cf, marker='s', label='Concurrent Futures (Threads)', linewidth=2)
    
    plt.title('Performance Comparison: MP vs CF(Process) vs CF(Thread)')
    plt.xlabel('Number of Workers')
    plt.ylabel('Time Taken (Seconds) [Lower is Better]')
    plt.grid(True)
    plt.legend()
    plt.xticks([2, 4, 6, 8])
    
    output_image = "benchmark_plot.png"
    plt.savefig(output_image)
    print(f"Plot saved to {output_image}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
