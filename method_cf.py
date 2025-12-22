import concurrent.futures
import utils

def run_concurrent_futures(task_list, num_cores):
    """
    Executes tasks using the concurrent.futures module (ThreadPoolExecutor).
    NOTE: In Python, Threads are limited by the GIL. This is expected to be
    slower than Multiprocessing for CPU-bound tasks, but demonstrates the difference.
    
    Args:
        task_list (list): List of task_args tuples.
        num_cores (int): Number of worker threads.
    """
    results = []
    
    # Switch to ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        results = list(executor.map(utils.worker_task, task_list))
        
    return results
