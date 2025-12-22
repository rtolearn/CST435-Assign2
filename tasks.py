import os
import filters
import data_loader
import time

def worker_task(task_args):
    """
    Top-level function for processing a single image.
    This must be picklable.
    
    Args:
        task_args (tuple): (input_path, output_folder, save_flag)
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        input_path, output_folder, save_flag = task_args
        
        # 1. Load
        image = data_loader.load_image(input_path)
        if image is None:
            return False
            
        # 2. Process
        processed_image = filters.process_pipeline(image)
        
        # 3. Save (Optional)
        if save_flag:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_folder, filename)
            data_loader.save_image(processed_image, output_path)
            
        return True
        
    except Exception as e:
        print(f"Error processing {task_args[0]}: {e}")
        return False
