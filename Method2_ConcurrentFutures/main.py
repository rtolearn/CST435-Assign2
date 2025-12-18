import os
import time
import concurrent.futures
import multiprocessing # Used only to count CPUs
import csv
import argparse
import filters # Imports your local filters.py

def run_test(num_workers, tasks):
    print(f"Testing with {num_workers} workers...", end=" ", flush=True)
    start_time = time.time()
    
    # METHOD 2 SPECIFIC: using ProcessPoolExecutor [cite: 40]
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks
        futures = [executor.submit(filters.process_single_image, task) for task in tasks]
        # Wait for all to complete
        concurrent.futures.wait(futures)
        
    duration = time.time() - start_time
    print(f"Done! ({duration:.4f}s)")
    return duration

def main():
    # --- COMMAND LINE ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(description='Concurrent Futures Benchmark')
    parser.add_argument('--save', type=str, default='false', 
                        help='Set to true for Video Demo (Save Images), false for Graph (Benchmark).')
    
    args = parser.parse_args()
    
    if args.save.lower() == 'true':
        SAVE_IMAGES = True
        print(">>> MODE: DEMO (Saving enabled).")
    else:
        SAVE_IMAGES = False
        print(">>> MODE: BENCHMARK (Saving disabled).")

    # --- SETUP ---
    INPUT_DIR = os.path.join("..", "input_images", "class_subset", "chicken_curry")
    OUTPUT_DIR = "outputs"
    
    if SAVE_IMAGES and not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(INPUT_DIR):
        print(f"ERROR: Input directory not found at: {INPUT_DIR}")
        return

    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.png'))]
    if not image_files:
        print("No images found!")
        return

    print(f"Found {len(image_files)} images.")
    
    # Prepare tasks
    tasks = [(os.path.join(INPUT_DIR, f), OUTPUT_DIR, SAVE_IMAGES) for f in image_files]
    
    # --- CORE COUNT CONFIGURATION ---
    max_cores = multiprocessing.cpu_count()
    core_counts = [1]
    while core_counts[-1] * 2 <= max_cores:
        core_counts.append(core_counts[-1] * 2)
    if max_cores not in core_counts:
        core_counts.append(max_cores)

    print(f"System has {max_cores} logical CPUs.")
    print(f"Running benchmarks for: {core_counts} workers.\n")

    # --- RUN BENCHMARKS ---
    results = []
    
    for workers in core_counts:
        duration = run_test(workers, tasks)
        results.append((workers, duration))

    # --- REPORT & CSV ---
    # Saving to 'benchmarks_concurrent.csv' to distinguish from Method 1
    csv_path = os.path.join("..", "Analysis", "benchmarks_concurrent.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    base_time = results[0][1]
    
    print("\n" + "="*45)
    print(f"{'Workers':<10} | {'Time (s)':<15} | {'Speedup':<10}")
    print("-" * 45)
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Workers", "Time", "Speedup"])
        
        for workers, duration in results:
            speedup = base_time / duration
            print(f"{workers:<10} | {duration:<15.4f} | {speedup:.2f}x")
            writer.writerow([workers, duration, speedup])
            
    print("="*45)
    print(f"\nResults saved to: {csv_path}")

if __name__ == "__main__":
    main()