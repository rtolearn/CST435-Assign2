import data_loader
import filters
import os
import cv2

def visualize_pipeline_steps():
    print("--- Visualizing Pipeline Steps ---")
    
    # 1. Get an image
    # Note: Corrected path based on previous investigation
    base_dir = "chicken_curry/chicken_curry" 
    paths = data_loader.get_image_paths(base_dir, limit=1)
    
    if not paths:
        print(f"No images found in {base_dir}. Using fallback to root.")
        paths = data_loader.get_image_paths(".", limit=1)
        
    if not paths:
        print("ERROR: No images found.")
        return

    input_path = paths[0]
    print(f"Processing image: {input_path}")
    
    original_img = data_loader.load_image(input_path)
    if original_img is None:
        return

    output_dir = "debug_steps"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 0: Original
    data_loader.save_image(original_img, os.path.join(output_dir, "0_original.jpg"))
    
    # Step 1: Brightness
    print("Applying Step 1: Brightness...")
    img_step1 = filters.adjust_brightness(original_img)
    data_loader.save_image(img_step1, os.path.join(output_dir, "1_brightness.jpg"))
    
    # Step 2: Gaussian Blur
    print("Applying Step 2: Gaussian Blur...")
    img_step2 = filters.apply_gaussian_blur(img_step1)
    data_loader.save_image(img_step2, os.path.join(output_dir, "2_blur.jpg"))
    
    # Step 3: Sharpening
    print("Applying Step 3: Sharpening...")
    img_step3 = filters.apply_sharpening(img_step2)
    data_loader.save_image(img_step3, os.path.join(output_dir, "3_sharpen.jpg"))
    
    # Step 4: Grayscale
    print("Applying Step 4: Grayscale...")
    img_step4 = filters.apply_grayscale(img_step3)
    data_loader.save_image(img_step4, os.path.join(output_dir, "4_grayscale.jpg"))
    
    # Step 5: Sobel
    print("Applying Step 5: Sobel Edge Detection...")
    img_step5 = filters.apply_sobel_edge_detection(img_step4)
    data_loader.save_image(img_step5, os.path.join(output_dir, "5_sobel_final.jpg"))
    
    print(f"\nAll steps saved to directory: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    visualize_pipeline_steps()
