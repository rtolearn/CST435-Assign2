import concurrent.futures
import utils

def run(task_list, num_cores, mode='thread'):
    """
    Executes tasks using the concurrent.futures module.
    
    Args:
        task_list (list): List of task_args tuples.
        num_cores (int): Number of workers.
        mode (str): 'thread' for ThreadPoolExecutor, 'process' for ProcessPoolExecutor.
    """
    results = []
    
    if mode == 'process':
        Executor = concurrent.futures.ProcessPoolExecutor
    else:
        Executor = concurrent.futures.ThreadPoolExecutor
    
    # Run with selected executor
    with Executor(max_workers=num_cores) as executor:
        results = list(executor.map(utils.worker_task, task_list))
        
    return results