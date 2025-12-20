import time
import csv
import multiprocessing
import os
import data_loader
import parallel_ops

def run_benchmark_suite():
    print("--- Starting Benchmark Suite ---")
    
    # Setup
    INPUT_DIR = os.path.join("chicken_curry", "chicken_curry")
    # Use a reasonable number of images for benchmarking (e.g., 20)
    # The user mentioned "Food-101 dataset (I will use a manageable subset)"
    # We will use 20 images to keep the benchmark fast but representative for this demo.
    NUM_IMAGES = 20 
    
    print(f"Loading {NUM_IMAGES} images from {INPUT_DIR}...")
    image_paths = data_loader.get_image_paths(INPUT_DIR, limit=NUM_IMAGES)
    
    if len(image_paths) < NUM_IMAGES:
        print(f"Warning: Only found {len(image_paths)} images.")
    
    # Prepare tasks (Benchmark mode: save=False)
    tasks = [(p, "outputs", False) for p in image_paths]
    
    # Core counts to test
    max_cores = multiprocessing.cpu_count()
    core_counts = [1, 2, 4, 8]
    # Filter core counts that exceed available cores (optional, but good for stability)
    # We'll allow up to 8 even if physical is less, just to show the trend, 
    # but concurrent.futures might cap it or multiprocessing might context switch heavily.
    # Let's clean it to available cores + maybe one step higher if low.
    valid_cores = [c for c in core_counts if c <= max_cores]
    if len(valid_cores) == 0: valid_cores = [1]
    
    # Ensure we test at least sequential (1 core) for baseline
    if 1 not in valid_cores: valid_cores.insert(0, 1)

    print(f"Testing Cores: {valid_cores}")
    print("-" * 60)
    print(f"{'Method':<20} | {'Cores':<5} | {'Time (s)':<10} | {'Speedup':<8} | {'Efficiency':<8}")
    print("-" * 60)
    
    results = []
    
    # Baseline (1 Core Multiprocessing)
    # We use this as T_1 for speedup calculations = T_1 / T_p
    print(f"{'Baseline (MP)':<20} | {1:<5} | ", end="", flush=True)
    start = time.time()
    parallel_ops.run_multiprocessing(tasks, 1)
    t_1 = time.time() - start
    print(f"{t_1:<10.4f} | {'1.00':<8} | {'1.00':<8}")
    
    results.append({
        "Method": "Baseline (MP)",
        "Cores": 1,
        "Time": t_1,
        "Speedup": 1.0,
        "Efficiency": 1.0
    })

    methods = [
        ("Multiprocessing", parallel_ops.run_multiprocessing),
        ("Concurrent Futures", parallel_ops.run_concurrent_futures)
    ]
    
    for name, func in methods:
        for cores in valid_cores:
            if name == "Multiprocessing" and cores == 1:
                continue # Already done baseline
                
            print(f"{name:<20} | {cores:<5} | ", end="", flush=True)
            
            start = time.time()
            func(tasks, cores)
            duration = time.time() - start
            
            speedup = t_1 / duration
            efficiency = speedup / cores
            
            print(f"{duration:<10.4f} | {speedup:<8.2f} | {efficiency:<8.2f}")
            
            results.append({
                "Method": name,
                "Cores": cores,
                "Time": duration,
                "Speedup": speedup,
                "Efficiency": efficiency
            })

    # Save details to CSV
    csv_path = "benchmark_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Method", "Cores", "Time", "Speedup", "Efficiency"])
        writer.writeheader()
        writer.writerows(results)
        
    print("-" * 60)
    print(f"Results saved to {csv_path}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
