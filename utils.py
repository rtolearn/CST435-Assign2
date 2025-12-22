import cv2
import numpy as np
import os
import time

# --- DATA LOADER SECTION ---

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

# --- FILTERS SECTION ---

def apply_grayscale(image):
    """Filter 1: Grayscale Conversion"""
    # Check if already grayscale
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_gaussian_blur(image):
    """Filter 2: Gaussian Blur (3x3 kernel)"""
    return cv2.GaussianBlur(image, (3, 3), 0)

def apply_sobel_edge_detection(image):
    """Filter 3: Sobel Edge Detection"""
    # Ensure input is grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

def apply_sharpening(image):
    """Filter 4: Image Sharpening (Stronger)"""
    # Stronger sharpening kernel
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

def adjust_brightness(image, value=60):
    """Filter 5: Brightness Adjustment (+60)"""
    if len(image.shape) == 2: # Grayscale brightness
         return cv2.add(image, value)
         
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

def process_pipeline(image):
    """
    Applies the full chain of 5 filters to an input image.
    
    Args:
        image (numpy.ndarray): Input image.
        
    Returns:
        numpy.ndarray: Processed image.
    """
    if image is None:
        return None

    # Pipeline sequence
    # 1. Adjust Brightness
    img = adjust_brightness(image)
    
    # 2. Gaussian Blur
    img = apply_gaussian_blur(img)
    
    # 3. Sharpening
    img = apply_sharpening(img)
    
    # 4. Grayscale
    img = apply_grayscale(img)
    
    # 5. Sobel Edge Detection
    final_result = apply_sobel_edge_detection(img)
    
    return final_result

# --- WORKER TASK SECTION ---

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
        
        # 1. Load (Using local function)
        image = load_image(input_path)
        if image is None:
            return (False, f"Failed to load {input_path}")
            
        # 2. Process (Using local function)
        processed_image = process_pipeline(image)
        
        # 3. Save (Optional) (Using local function)
        if save_flag:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_folder, filename)
            save_image(processed_image, output_path)
            
        return (True, f"Processed {os.path.basename(input_path)}")
        
    except Exception as e:
        print(f"Error processing {task_args[0]}: {e}")
        return (False, str(e))
