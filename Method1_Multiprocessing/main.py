import os
import time
import multiprocessing
import csv
import argparse  # Library for command line arguments
import filters   # Imports your local filters.py

def run_test(num_cores, tasks):
    print(f"Testing with {num_cores} cores...", end=" ", flush=True)
    start_time = time.time()
    
    # Multiprocessing Pool
    with multiprocessing.Pool(processes=num_cores) as pool:
        pool.map(filters.process_single_image, tasks)
        
    duration = time.time() - start_time
    print(f"Done! ({duration:.4f}s)")
    return duration

def main():
    # --- COMMAND LINE ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(description='Parallel Image Processing Benchmark')
    parser.add_argument('--save', type=str, default='false', 
                        help='Set to true to save images (Video Demo), false for Benchmark (Graph).')
    
    args = parser.parse_args()
    
    # Convert string argument to boolean
    if args.save.lower() == 'true':
        SAVE_IMAGES = True
        print(">>> MODE: DEMO (Saving images enabled. Speedup will be lower due to Disk I/O).")
    else:
        SAVE_IMAGES = False
        print(">>> MODE: BENCHMARK (Saving disabled. Measuring pure CPU Speedup).")

    # --- SETUP ---
    INPUT_DIR = os.path.join("..", "input_images", "class_subset", "chicken_curry")
    OUTPUT_DIR = "outputs"
    
    # Create output dir only if we are actually saving
    if SAVE_IMAGES and not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(INPUT_DIR):
        print(f"ERROR: Input directory not found at: {INPUT_DIR}")
        print("Please create the folder and add images.")
        return

    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print("No images found!")
        return

    print(f"Found {len(image_files)} images to process.")

    # Pass the configuration flag to every worker task
    tasks = [(os.path.join(INPUT_DIR, f), OUTPUT_DIR, SAVE_IMAGES) for f in image_files]
    
    # --- CORE COUNT CONFIGURATION ---
    max_cores = multiprocessing.cpu_count()
    core_counts = [1]
    while core_counts[-1] * 2 <= max_cores:
        core_counts.append(core_counts[-1] * 2)
    if max_cores not in core_counts:
        core_counts.append(max_cores)

    print(f"System has {max_cores} logical CPUs.")
    print(f"Running benchmarks for: {core_counts} cores.\n")

    # --- RUN BENCHMARKS ---
    results = []
    
    for cores in core_counts:
        duration = run_test(cores, tasks)
        results.append((cores, duration))

    # --- REPORT & CSV ---
    csv_path = os.path.join("..", "Analysis", "benchmarks_multiprocessing.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    base_time = results[0][1] # Baseline (1 core)
    
    print("\n" + "="*45)
    print(f"{'Cores':<10} | {'Time (s)':<15} | {'Speedup':<10}")
    print("-" * 45)
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Cores", "Time", "Speedup"])
        
        for cores, duration in results:
            speedup = base_time / duration
            print(f"{cores:<10} | {duration:<15.4f} | {speedup:.2f}x")
            writer.writerow([cores, duration, speedup])
            
    print("="*45)
    print(f"\nResults saved to: {csv_path}")

if __name__ == "__main__":
    main()