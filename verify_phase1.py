import data_loader
import filters
import os

def test_phase1():
    print("--- Testing Phase 1: Core Logic ---")
    
    # 1. Test get_image_paths
    # Try the chicken_curry folder first
    input_dir = os.path.join("chicken_curry")
    paths = data_loader.get_image_paths(input_dir, limit=1)
    
    if not paths:
        print(f"No images found in {input_dir}. Checking root for jpgs...")
        paths = data_loader.get_image_paths(".", limit=1)
        
    if not paths:
        print("ERROR: No images found to test with.")
        return
        
    test_image_path = paths[0]
    print(f"Testing with image: {test_image_path}")
    
    # 2. Test load_image
    img = data_loader.load_image(test_image_path)
    if img is None:
        print("ERROR: Failed to load image.")
        return
    print(f"Image loaded. Shape: {img.shape}")
    
    # 3. Test filters
    try:
        processed_img = filters.process_pipeline(img)
        print(f"Image processed. Shape: {processed_img.shape}")
    except Exception as e:
        print(f"ERROR during processing: {e}")
        return

    # 4. Test save_image
    output_path = "test_output_phase1.jpg"
    success = data_loader.save_image(processed_img, output_path)
    
    if success:
        print(f"SUCCESS: Image saved to {output_path}")
    else:
        print("ERROR: Failed to save image.")

if __name__ == "__main__":
    test_phase1()
