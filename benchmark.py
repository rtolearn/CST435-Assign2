import time
import csv
import multiprocessing
import os
import utils
import method_mp
import method_cf
import matplotlib.pyplot as plt

def run_benchmark_suite():
    print("--- Starting Scalability Benchmark Suite ---")
    
    # 1. SETUP
    INPUT_DIR = os.path.join("food-101", "food-101", "images")
    
    # Dimensions to test
    # IMAGE_COUNTS = [50, 100, 500]
    IMAGE_COUNTS = [50]
    WORKER_COUNTS = [1, 2, 4, 8]
    
    # Load Max Images once
    MAX_IMAGES = max(IMAGE_COUNTS)
    print(f"Loading {MAX_IMAGES} images cache from {INPUT_DIR}...")
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=MAX_IMAGES)
    
    if len(all_image_paths) < MAX_IMAGES:
        print(f"Warning: Only found {len(all_image_paths)} images. Adjusting max test limit.")
        IMAGE_COUNTS = [c for c in IMAGE_COUNTS if c <= len(all_image_paths)]
        
    print(f"Testing Speed across Image Counts: {IMAGE_COUNTS}")
    print(f"For Worker Counts: {WORKER_COUNTS}")
    print("-" * 60)
    
    # Data collection
    csv_results = []
    plot_data = {w: {'MP': [], 'CF_Proc': [], 'CF_Thread': []} for w in WORKER_COUNTS}
    
    # 2. EXECUTION LOOP
    for img_count in IMAGE_COUNTS:
        print(f"\n[ Dataset Size: {img_count} Images ]")
        
        # Slice the paths for this iteration
        current_paths = all_image_paths[:img_count]
        tasks = [(p, "outputs", False) for p in current_paths]
        
        print(f"{'Workers':<8} | {'MP (s)':<10} | {'CF Proc (s)':<12} | {'CF Thrd (s)':<12} | {'Best':<10}")
        print("-" * 65)
        
        for workers in WORKER_COUNTS:
            # A. Multiprocessing
            start = time.time()
            method_mp.run_multiprocessing(tasks, workers)
            time_mp = time.time() - start
            
            # B. CF Process
            start = time.time()
            method_cf.run(tasks, workers, mode='process')
            time_cfp = time.time() - start
            
            # C. CF Threads
            start = time.time()
            method_cf.run(tasks, workers, mode='thread')
            time_cft = time.time() - start
            
            # Record Data
            plot_data[workers]['MP'].append((img_count, time_mp))
            plot_data[workers]['CF_Proc'].append((img_count, time_cfp))
            plot_data[workers]['CF_Thread'].append((img_count, time_cft))
            
            # Determine Winner
            times = {'MP': time_mp, 'CF_P': time_cfp, 'CF_T': time_cft}
            best = min(times, key=times.get)
            
            print(f"{workers:<8} | {time_mp:<10.4f} | {time_cfp:<12.4f} | {time_cft:<12.4f} | {best:<10}")
            
            # Append to CSV data
            csv_results.append({
                "Images": img_count,
                "Workers": workers,
                "Method": "Multiprocessing",
                "Time": time_mp
            })
            csv_results.append({
                "Images": img_count,
                "Workers": workers,
                "Method": "CF (Process)",
                "Time": time_cfp
            })
            csv_results.append({
                "Images": img_count,
                "Workers": workers,
                "Method": "CF (Thread)",
                "Time": time_cft
            })

    # 3. SAVE CSV (Overwrite)
    csv_path = "benchmark_results_scalability.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Images", "Workers", "Method", "Time"])
        writer.writeheader()
        writer.writerows(csv_results)
    print(f"\nResults saved to {csv_path}")

    # 4. GENERATE PLOTS
    print("\nGenerating plots...")
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    styles = {
        'MP': {'marker': 'o', 'linestyle': '-', 'label': 'Multiprocessing', 'color': 'blue'},
        'CF_Proc': {'marker': '^', 'linestyle': '--', 'label': 'CF (Process)', 'color': 'orange'},
        'CF_Thread': {'marker': 's', 'linestyle': '-', 'label': 'CF (Thread)', 'color': 'green'}
    }
    
    for w in WORKER_COUNTS:
        plt.figure(figsize=(10, 6))
        
        for method_key, points in plot_data[w].items():
            if not points:
                continue
            
            points.sort(key=lambda x: x[0])
            x_vals, y_vals = zip(*points)
            style = styles[method_key]
            
            plt.plot(x_vals, y_vals, 
                     marker=style['marker'], 
                     linestyle=style['linestyle'],
                     label=style['label'],
                     color=style['color'],
                     linewidth=2)
        
        plt.title(f'Execution Time: {w} Workers', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Images', fontsize=12)
        plt.ylabel('Execution Time (seconds)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xticks(IMAGE_COUNTS)
        
        filename = os.path.join(output_dir, f"time_vs_images_{w}worker.png")
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  > Saved {filename}")
        plt.close()
    
    print("\n✓ Benchmark complete!")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
