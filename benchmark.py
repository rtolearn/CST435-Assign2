import time
import csv
import multiprocessing
import os
import utils
import method_mp
import method_cf

def run_benchmark_suite():
    print("--- Starting Benchmark Suite ---")
    # Setup
    INPUT_DIR = os.path.join("food-101", "food-101", "images")
    # Use a reasonable number of images for benchmarking (e.g., 20)
    # The user mentioned "Food-101 dataset (I will use a manageable subset)"
    # We will use 20 images to keep the benchmark fast but representative for this demo.
    NUM_IMAGES = 500
    
    print(f"Loading {NUM_IMAGES} images from {INPUT_DIR}...")
    image_paths = utils.get_image_paths(INPUT_DIR, limit=NUM_IMAGES)
    
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
    
    results = []
    
    # Baseline (1 Core Multiprocessing)
    print(f"Running Baseline (MP 1 Core)... ", end="", flush=True)
    start = time.time()
    method_mp.run_multiprocessing(tasks, 1)
    t_1 = time.time() - start
    print(f"Done in {t_1:.4f}s")
    
    results.append({
        "Method": "Baseline (MP)",
        "Cores": 1,
        "Time": t_1,
        "Speedup": 1.0,
        "Efficiency": 1.0
    })

    # Run all tests first
    mp_results = {} # Map cores -> stats
    cf_results = {} # Map cores -> stats
    
    print("\nRunning Tests...")
    for cores in valid_cores:
        # Multiprocessing
        if cores == 1:
            stats = {"Time": t_1, "Speedup": 1.0, "Efficiency": 1.0}
        else:
            print(f"  > Multiprocessing ({cores} cores)... ", end="", flush=True)
            start = time.time()
            method_mp.run_multiprocessing(tasks, cores)
            dur = time.time() - start
            stats = {"Time": dur, "Speedup": t_1/dur, "Efficiency": (t_1/dur)/cores}
            print(f"{dur:.4f}s")
            
        mp_results[cores] = stats
        results.append({**stats, "Method": "Multiprocessing", "Cores": cores})
        
        # Concurrent Futures (Threads)
        print(f"  > Concurrent Futures (Threads) ({cores} cores)... ", end="", flush=True)
        start = time.time()
        method_cf.run_concurrent_futures(tasks, cores)
        dur = time.time() - start
        stats = {"Time": dur, "Speedup": t_1/dur, "Efficiency": (t_1/dur)/cores}
        print(f"{dur:.4f}s")
        
        cf_results[cores] = stats
        results.append({**stats, "Method": "Concurrent Futures (Threads)", "Cores": cores})

    # Print Side-by-Side Table
    print("\n" + "="*85)
    print(f"{'Cores':<6} | {'MP Time':<9} {'MP Spd':<8} | {'CF Time':<9} {'CF Spd':<8} | {'Winner':<10}")
    print("-" * 85)
    
    for cores in valid_cores:
        mp = mp_results[cores]
        cf = cf_results[cores]
        
        winner = "MP" if mp["Time"] < cf["Time"] else "CF"
        if abs(mp["Time"] - cf["Time"]) < 0.01: winner = "Tie"
        
        print(f"{cores:<6} | {mp['Time']:<9.4f} {mp['Speedup']:<8.2f} | {cf['Time']:<9.4f} {cf['Speedup']:<8.2f} | {winner:<10}")
        
    print("="*85)

    # Save details to CSV
    csv_path = "benchmark_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Method", "Cores", "Time", "Speedup", "Efficiency"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nResults saved to {csv_path}")
    
    # Generate Plot
    plot_results(results)

def plot_results(results):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed. Skipping plot generation.")
        return

    print("Generating performance plot...")
    
    # Separate data by method
    mp_data = [r for r in results if "Multiprocessing" in r["Method"] or "Baseline" in r["Method"]]
    cf_data = [r for r in results if "Concurrent Futures" in r["Method"]]
    
    # Sort by cores to ensure line connects correctly
    mp_data.sort(key=lambda x: x["Cores"])
    cf_data.sort(key=lambda x: x["Cores"])
    
    # Extract X (Cores) and Y (Speedup)
    mp_cores = [d["Cores"] for d in mp_data]
    mp_speedup = [d["Speedup"] for d in mp_data]
    
    cf_cores = [d["Cores"] for d in cf_data]
    cf_speedup = [d["Speedup"] for d in cf_data]
    
    plt.figure(figsize=(10, 6))
    
    # Plot Lines
    plt.plot(mp_cores, mp_speedup, marker='o', label='Multiprocessing', linewidth=2)
    plt.plot(cf_cores, cf_speedup, marker='s', label='Concurrent Futures', linewidth=2, linestyle='--')
    
    # Ideal Speedup Line (y=x)
    max_cores = max(max(mp_cores), max(cf_cores))
    plt.plot([1, max_cores], [1, max_cores], 'k:', label='Ideal Linear Speedup', alpha=0.5)
    
    plt.title('Speedup Comparison: Multiprocessing vs Concurrent Futures')
    plt.xlabel('Number of Cores')
    plt.ylabel('Speedup Factor (Higher is Better)')
    plt.grid(True)
    plt.legend()
    plt.xticks(mp_cores) # Show only tested core counts on X-axis
    
    output_image = "benchmark_plot.png"
    plt.savefig(output_image)
    print(f"Plot saved to {output_image}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_benchmark_suite()
