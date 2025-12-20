import cv2
import os

def get_image_paths(source_dir, limit=None):
    """
    Retrieves image file paths from the source directory.
    
    Args:
        source_dir (str): Directory containing images.
        limit (int, optional): Maximum number of images to return.
        
    Returns:
        list: List of full file paths.
    """
    valid_extensions = ('.jpg', '.jpeg', '.png')
    image_paths = []
    
    if not os.path.exists(source_dir):
        print(f"Warning: Source directory '{source_dir}' does not exist.")
        return []

    count = 0
    for entry in os.scandir(source_dir):
        if entry.is_file() and entry.name.lower().endswith(valid_extensions):
            image_paths.append(entry.path)
            count += 1
            if limit and count >= limit:
                break
                
    return image_paths

def load_image(path):
    """
    Loads an image from disk.
    
    Args:
        path (str): File path to the image.
        
    Returns:
        numpy.ndarray or None: The loaded image, or None if failed.
    """
    try:
        img = cv2.imread(path)
        if img is None:
            print(f"Warning: Failed to load image at {path}")
        return img
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def save_image(image, output_path):
    """
    Saves an image to disk.
    
    Args:
        image (numpy.ndarray): The image to save.
        output_path (str): The destination path.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        if os.path.dirname(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return cv2.imwrite(output_path, image)
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")
        return False
