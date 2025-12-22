import os
import time
import argparse
import multiprocessing
import utils
import method_mp
import method_cf

def main():
    # --- COMMAND LINE ARGUMENT PARSING ---
    parser = argparse.ArgumentParser(description='Parallel Image Processing Benchmark')
    parser.add_argument('--count', type=int, default=None, 
                        help='Number of images to process (default: all)')
    parser.add_argument('--cores', type=int, default=multiprocessing.cpu_count(),
                        help='Number of cores/workers (default: CPU count)')
    parser.add_argument('--method', type=str, choices=['mp', 'cf'], default='mp',
                        help='Parallel method: mp (multiprocessing) or cf (concurrent.futures)')
    parser.add_argument('--save', action='store_true',
                        help='Enable saving of output images.')
    
    args = parser.parse_args()
    
    print(f"\n>>> CONFIGURATION")
    print(f"    Method:   {'Multiprocessing' if args.method == 'mp' else 'Concurrent Futures'}")
    print(f"    Cores:    {args.cores}")
    print(f"    Saving:   {'Enabled' if args.save else 'Disabled (Benchmark Mode)'}")
    
    # --- SETUP ---
    # Corrected path for nested directory structure
    INPUT_DIR = os.path.join("chicken_curry", "chicken_curry") 
    OUTPUT_DIR = "outputs"
    
    # Get image paths
    print(f"\nScanning {INPUT_DIR}...")
    image_paths = utils.get_image_paths(INPUT_DIR, limit=args.count)
    
    if not image_paths:
        print("ERROR: No images found. Please check 'chicken_curry/chicken_curry/' exists.")
        return

    print(f"    Found:    {len(image_paths)} images.")

    # Prepare tasks: (input_path, output_folder, save_flag)
    tasks = [(p, OUTPUT_DIR, args.save) for p in image_paths]
    
    # --- EXECUTION ---
    print(f"\n>>> STARTING PROCESSING...")
    start_time = time.time()
    
    if args.method == 'mp':
        results = method_mp.run_multiprocessing(tasks, args.cores)
    else:
        results = method_cf.run_concurrent_futures(tasks, args.cores)
        
    duration = time.time() - start_time
    
    # --- REPORT ---
    success_count = sum(1 for r in results if r[0])
    fail_count = len(results) - success_count
    
    print(f"\n>>> DONE!")
    print(f"    Time:     {duration:.4f} seconds")
    print(f"    Success:  {success_count}")
    print(f"    Failed:   {fail_count}")
    
    if fail_count > 0:
        print("\n    Failures:")
        for r in results:
            if not r[0]:
                print(f"    - {r[1]}")

if __name__ == "__main__":
    # Windows Multiprocessing support
    multiprocessing.freeze_support()
    main()
