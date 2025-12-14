import cv2
import numpy as np
import os

def apply_grayscale(image):
    """Filter 1: Grayscale Conversion"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_gaussian_blur(image):
    """Filter 2: Gaussian Blur (3x3 kernel)"""
    return cv2.GaussianBlur(image, (3, 3), 0)

def apply_sobel_edge_detection(image):
    """Filter 3: Edge Detection (Sobel)"""
    # Convert to gray if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    return cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

def apply_sharpening(image):
    """Filter 4: Image Sharpening"""
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)

def adjust_brightness(image, value=30):
    """Filter 5: Brightness Adjustment"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

def process_single_image(file_data):
    """
    Worker function to process one image.
    Args:
        file_data: tuple containing (input_path, output_folder)
    """
    input_path, output_folder = file_data
    
    try:
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            return f"Failed to read: {input_path}"

        filename = os.path.basename(input_path)

        # --- APPLY PIPELINE ---
        # 1. Adjust Brightness
        img = adjust_brightness(img)
        # 2. Gaussian Blur
        img = apply_gaussian_blur(img)
        # 3. Sharpening
        img = apply_sharpening(img)
        # 4. Grayscale (Final conversion before edge detection often looks best)
        # Note: If you want colored output, skip this or save separate files.
        # But usually Edge Detection requires grayscale.
        gray_img = apply_grayscale(img)
        # 5. Sobel Edge Detection
        final_result = apply_sobel_edge_detection(img)

        # Save result
        output_path = os.path.join(output_folder, f"processed_{filename}")
        cv2.imwrite(output_path, final_result)
        
        return None # Success
        
    except Exception as e:
        return f"Error processing {input_path}: {str(e)}"