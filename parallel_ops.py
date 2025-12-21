import multiprocessing
import concurrent.futures
import filters
import data_loader
import os

def worker_task(task_args):
    """
    Top-level worker function to process a single image.
    This function is pickled and executed by worker processes.
    
    Args:
        task_args (tuple): (input_path, output_folder, save_flag)
        
    Returns:
        tuple: (success_bool, message)
    """
    input_path, output_folder, save_flag = task_args
    
    try:
        # 1. Load
        img = data_loader.load_image(input_path)
        if img is None:
            return False, f"Failed to load: {input_path}"
            
        # 2. Process
        processed_img = filters.process_pipeline(img)
        if processed_img is None:
            return False, f"Processing failed for: {input_path}"
            
        # 3. Save (if requested)
        if save_flag:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_folder, f"processed_{filename}")
            if not data_loader.save_image(processed_img, output_path):
                return False, f"Failed to save: {output_path}"
                
        return True, None
        
    except Exception as e:
        return False, f"Error processing {input_path}: {str(e)}"

def run_multiprocessing(tasks, num_cores):
    """
    Executes tasks using the multiprocessing module.
    
    Args:
        tasks (list): List of task_args tuples.
        num_cores (int): Number of worker processes.
    """
    with multiprocessing.Pool(processes=num_cores) as pool:
        # pool.map blocks until complete
        results = pool.map(worker_task, tasks)
    return results

def run_concurrent_futures(tasks, num_cores):
    """
    Executes tasks using the concurrent.futures module (ThreadPoolExecutor).
    NOTE: In Python, Threads are limited by the GIL. This is expected to be
    slower than Multiprocessing for CPU-bound tasks, but demonstrates the difference.
    
    Args:
        tasks (list): List of task_args tuples.
        num_cores (int): Number of worker threads.
    """
    results = []
    
    # Switch to ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        results = list(executor.map(worker_task, tasks))
        
    return results
