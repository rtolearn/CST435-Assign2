import os
import time
import multiprocessing
import filters  # Your local filters.py

def run_test(num_cores, tasks):
    """
    Runs the processing task with a specific number of cores.
    Returns the time taken.
    """
    print(f"Testing with {num_cores} cores...", end=" ", flush=True)
    
    start_time = time.time()
    
    # Create Pool with specific number of processes
    with multiprocessing.Pool(processes=num_cores) as pool:
        # We don't need the results variable for benchmarking, just wait for completion
        pool.map(filters.process_single_image, tasks)
        
    end_time = time.time()
    duration = end_time - start_time
    print(f"Done! ({duration:.4f}s)")
    return duration

def main():
    # --- CONFIGURATION ---
    INPUT_DIR = os.path.join("..", "input_images", "class_subset", "chicken_curry")
    OUTPUT_DIR = "outputs"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Get list of images
    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print("No images found!")
        return

    # Prepare tasks
    tasks = [(os.path.join(INPUT_DIR, f), OUTPUT_DIR) for f in image_files]
    
    # --- AUTOMATIC CORE DETECTION ---
    max_cores = multiprocessing.cpu_count()
    
    # Create a list of core counts to test: 1, 2, 4, 8... up to max_cores
    core_counts = [1]
    while core_counts[-1] * 2 <= max_cores:
        core_counts.append(core_counts[-1] * 2)
    
    # If max_cores is not a power of 2 (e.g., 6 or 12), add it to the end
    if max_cores not in core_counts:
        core_counts.append(max_cores)

    print(f"Detected {max_cores} logical CPUs.")
    print(f"Will run benchmarks for: {core_counts} cores.\n")

    # --- BENCHMARK LOOP ---
    results = []
    
    for cores in core_counts:
        duration = run_test(cores, tasks)
        results.append((cores, duration))

    # --- FINAL REPORT ---
    print("\n" + "="*40)
    print(f"{'Cores':<10} | {'Time (s)':<15} | {'Speedup':<10}")
    print("-" * 40)
    
    base_time = results[0][1] # Time taken by 1 core
    
    for cores, duration in results:
        speedup = base_time / duration
        print(f"{cores:<10} | {duration:<15.4f} | {speedup:.2f}x")
    print("="*40)

if __name__ == "__main__":
    main()