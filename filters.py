import cv2
import numpy as np

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
