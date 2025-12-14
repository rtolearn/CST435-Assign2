import os
import time
import concurrent.futures
import multiprocessing # Just for counting CPUs
import filters  # Your local filters.py

def run_test(num_cores, tasks):
    """
    Runs the processing task with a specific number of workers.
    Returns the time taken.
    """
    print(f"Testing with {num_cores} workers...", end=" ", flush=True)
    
    start_time = time.time()
    
    # Use max_workers to control the "cores"
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(filters.process_single_image, task) for task in tasks]
        # Wait for all to complete
        concurrent.futures.wait(futures)
        
    end_time = time.time()
    duration = end_time - start_time
    print(f"Done! ({duration:.4f}s)")
    return duration

def main():
    # --- CONFIGURATION ---
    INPUT_DIR = os.path.join("..", "input_images", "class_subset",  "chicken_curry")
    OUTPUT_DIR = "outputs"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print("No images found!")
        return

    tasks = [(os.path.join(INPUT_DIR, f), OUTPUT_DIR) for f in image_files]
    
    # --- AUTOMATIC CORE DETECTION ---
    max_cores = multiprocessing.cpu_count()
    
    # Generate list: 1, 2, 4...
    core_counts = [1]
    while core_counts[-1] * 2 <= max_cores:
        core_counts.append(core_counts[-1] * 2)
    if max_cores not in core_counts:
        core_counts.append(max_cores)

    print(f"Detected {max_cores} logical CPUs.")
    print(f"Will run benchmarks for: {core_counts} workers.\n")

    # --- BENCHMARK LOOP ---
    results = []
    
    for cores in core_counts:
        duration = run_test(cores, tasks)
        results.append((cores, duration))

    # --- FINAL REPORT ---
    print("\n" + "="*40)
    print(f"{'Workers':<10} | {'Time (s)':<15} | {'Speedup':<10}")
    print("-" * 40)
    
    base_time = results[0][1] # Time taken by 1 worker
    
    for cores, duration in results:
        speedup = base_time / duration
        print(f"{cores:<10} | {duration:<15.4f} | {speedup:.2f}x")
    print("="*40)

if __name__ == "__main__":
    main()