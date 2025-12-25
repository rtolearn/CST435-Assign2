import time
import csv
import multiprocessing
import os
import utils
import method_mp
import method_cf

def run_benchmark_suite():
    print("--- Starting Scalability Benchmark Suite (Data Collection) ---")
    
    # 1. SETUP
    INPUT_DIR = os.path.join("food-101", "food-101", "images")
    
    # Dimensions to test
    IMAGE_COUNTS = [10000]
    WORKER_COUNTS = [1, 2, 4, 6, 8]
    
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
    
    # 2. LOAD EXISTING DATA
    csv_path = "benchmark_results_scalability.csv"
    existing_tests = set() # Stores tuples: (ImageCount, WorkerCount, MethodName)
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    existing_tests.add((int(row['Images']), int(row['Workers']), row['Method']))
                except ValueError:
                    continue
        print(f"Loaded {len(existing_tests)} existing test records from {csv_path}")
    else:
        # Create file with header if it doesn't exist
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Images", "Workers", "Method", "Time"])
            writer.writeheader()
    
    # 3. EXECUTION LOOP
    
    for img_count in IMAGE_COUNTS:
        print(f"\n[ Dataset Size: {img_count} Images ]")
        
        # Slice the paths for this iteration
        current_paths = all_image_paths[:img_count]
        # Create tasks (No Save)
        tasks = [(p, "outputs", False) for p in current_paths]
        
        print(f"{'Workers':<8} | {'MP (s)':<10} | {'CF Proc (s)':<12} | {'CF Thrd (s)':<12} | {'Status':<10}")
        print("-" * 65)
        
        for workers in WORKER_COUNTS:
            # Helper to check run and save
            def run_and_save(method_name, runner_func):
                if (img_count, workers, method_name) in existing_tests:
                    return None # Signal that we skipped
                    
                start = time.time()
                runner_func()
                duration = time.time() - start
                
                # Append to CSV immediately
                with open(csv_path, 'a', newline='') as f:
                     writer = csv.DictWriter(f, fieldnames=["Images", "Workers", "Method", "Time"])
                     writer.writerow({
                        "Images": img_count,
                        "Workers": workers,
                        "Method": method_name,
                        "Time": duration
                     })
                existing_tests.add((img_count, workers, method_name))
                return duration

            # A. Multiprocessing
            t_mp = run_and_save("Multiprocessing", lambda: method_mp.run_multiprocessing(tasks, workers))
            
            # B. CF Process
            t_cfp = run_and_save("CF (Process)", lambda: method_cf.run(tasks, workers, mode='process'))
            
            # C. CF Threads
            t_cft = run_and_save("CF (Thread)", lambda: method_cf.run(tasks, workers, mode='thread'))
            
            # Print Status row
            def fmt(val): return f"{val:.4f}" if isinstance(val, float) else "-"
            
            # Determine status
            status = "Done"
            if t_mp is None and t_cfp is None and t_cft is None:
                status = "Skipped"
                
            print(f"{workers:<8} | {fmt(t_mp):<10} | {fmt(t_cfp):<12} | {fmt(t_cft):<12} | {status:<10}")

    print(f"\nBenchmark run complete. Data saved to {csv_path}")
    print("Run 'python plot_benchmark.py' to generate graphs.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
