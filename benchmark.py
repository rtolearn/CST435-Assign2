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
    IMAGE_COUNTS = [5, 10, 50, 100, 500]
    WORKER_COUNTS = [1, 2, 4, 6, 8]
    
    # Load Max Images once (to avoid reloading for every test)
    MAX_IMAGES = max(IMAGE_COUNTS)
    print(f"Loading {MAX_IMAGES} images cache from {INPUT_DIR}...")
    all_image_paths = utils.get_image_paths(INPUT_DIR, limit=MAX_IMAGES)
    
    if len(all_image_paths) < MAX_IMAGES:
        print(f"Warning: Only found {len(all_image_paths)} images. Adjusting max test limit.")
        IMAGE_COUNTS = [c for c in IMAGE_COUNTS if c <= len(all_image_paths)]
        
    print(f"Testing Speed across Image Counts: {IMAGE_COUNTS}")
    print(f"For Worker Counts: {WORKER_COUNTS}")
    print("-" * 60)
    
    # Data Structure: results[worker_count][image_count][method] = time
    # Flattened list for CSV
    csv_results = []
    
    # Nested Dictionary for Plotting: plot_data[worker_count] = { 'MP': [(img, time), ...], 'CF_Th': ... }
    plot_data = {w: {'MP': [], 'CF_Proc': [], 'CF_Thread': []} for w in WORKER_COUNTS}

    # 2. EXECUTION LOOP
    # We loop by Image Count first to minimize list slicing, or by Worker?
    # Actually, looping by Image Count first is better for progress visibility.
    
    for img_count in IMAGE_COUNTS:
        print(f"\n[ Dataset Size: {img_count} Images ]")
        
        # Slice the paths for this iteration
        current_paths = all_image_paths[:img_count]
        # Create tasks (No Save)
        tasks = [(p, "outputs", False) for p in current_paths]
        
        print(f"{'Workers':<8} | {'MP (s)':<10} | {'CF Proc (s)':<12} | {'CF Thrd (s)':<12} | {'Best':<10}")
        print("-" * 65)
        
        for workers in WORKER_COUNTS:
            # A. Multiprocessing
            start = time.time()
            method_mp.run_multiprocessing(tasks, workers)
            time_mp = time.time() - start
            
            # B. CF Threads
            start = time.time()
            method_cf.run(tasks, workers, mode='thread')
            time_cft = time.time() - start
            
            # C. CF Process
            start = time.time()
            method_cf.run(tasks, workers, mode='process')
            time_cfp = time.time() - start
            
            # Record Data
            plot_data[workers]['MP'].append((img_count, time_mp))
            plot_data[workers]['CF_Thread'].append((img_count, time_cft))
            plot_data[workers]['CF_Proc'].append((img_count, time_cfp))
            
            # Determine Winner
            times = {'MP': time_mp, 'CF_P': time_cfp, 'CF_T': time_cft}
            best = min(times, key=times.get)
            
            print(f"{workers:<8} | {time_mp:<10.4f} | {time_cfp:<12.4f} | {time_cft:<12.4f} | {best:<10}")
            
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

    # 3. SAVE CSV
    csv_path = "benchmark_results_scalability.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Images", "Workers", "Method", "Time"])
        writer.writeheader()
        writer.writerows(csv_results)
    print(f"\nDetailed results saved to {csv_path}")

    # 4. GENERATE PLOTS (5 Graphs)
    print("\nGenerating 5 Scalability Plots...")
    
    for w in WORKER_COUNTS:
        plt.figure(figsize=(10, 6))
        
        # Extract X, Y for each method
        # MP
        x_mp, y_mp = zip(*plot_data[w]['MP'])
        plt.plot(x_mp, y_mp, marker='o', label='Multiprocessing', linewidth=2)
        
        # CF Process
        x_cfp, y_cfp = zip(*plot_data[w]['CF_Proc'])
        plt.plot(x_cfp, y_cfp, marker='^', linestyle='--', label='CF (Process)', linewidth=2)
        
        # CF Thread
        x_cft, y_cft = zip(*plot_data[w]['CF_Thread'])
        plt.plot(x_cft, y_cft, marker='s', label='CF (Thread)', linewidth=2)
        
        plt.title(f'Scalability Analysis: {w} Workers')
        plt.xlabel('Number of Images')
        plt.ylabel('Execution Time (seconds)')
        plt.legend()
        plt.grid(True)
        
        # Save
        output_dir = "plots"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"benchmark_plot_{w}worker.png")
        plt.savefig(filename)
        print(f"  > Saved {filename}")
        plt.close() # Close memory

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
