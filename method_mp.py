import multiprocessing
import utils

def run_multiprocessing(task_list, num_cores):
    """
    Executes tasks using the multiprocessing module (Process Pool).
    
    Args:
        task_list (list): List of task_args tuples.
        num_cores (int): Number of worker processes.
    """
    results = []
    
    # Create a Pool of workers
    with multiprocessing.Pool(processes=num_cores) as pool:
        # Map the tasks to the workers
        results = pool.map(utils.worker_task, task_list)
        
    return results