# CST435 Assignment 2: Parallel Image Processing System
 
 **Course**: CST435: Parallel and Cloud Computing  
 **Assignment**: Assignment 2 - Parallel Image Processing on GCP
 
 ---
 
 ## 1. Project Overview
 This project implements a high-performance parallel image processing system capable of filtering thousands of images using multiple CPU cores. It compares two parallel paradigms: **Multiprocessing** (Processes) vs **Concurrent Futures** (Threads).
 
 ### 📂 File Structure & Functionality
 The code is organized into modular components for clarity and reusability:
 
 #### **Core Logic**
 *   **`main.py`**:  
     The **Command Center**. It handles argument parsing (`--count`, `--cores`, `--method`), orchestrates the workflow, and reports success/failure. It imports the specific method modules.
 *   **`utils.py`**:  
     The **Unified Helper Library**. Implements the "Separation of Concerns" pattern by containing:
     *   **Processing Pipeline**: Includes a **CPU-intensive Custom Blur** (pure Python) to demonstrate GIL bottlenecks and make Process-based parallelism shine, along with standard OpenCV filters (Brightness, Gaussian Blur, Sharpening, Grayscale, Sobel).
     *   **I/O**: Safe image loading and saving logic.
     *   **Worker Logic**: The `worker_task` function that processes a single image.
 *   **`requirements.txt`**: List of dependencies (`opencv-python`, `numpy`, `matplotlib`).
 
 #### **Parallel Paradigms**
 *   **`method_mp.py`**:  
     **Paradigm 1 (Multiprocessing)**. Implements parallelism using `multiprocessing.Pool` (Processes). Best for true CPU parallelism on Linux and handling CPU-bound Python tasks (bypassing GIL).
 *   **`method_cf.py`**:  
     **Paradigm 2 & 3 (Concurrent Futures)**. Unified module implementing both:
     *   **Threads** (`ThreadPoolExecutor`): Fast for I/O-bound tasks but limited by GIL for CPU-bound Python code.
     *   **Processes** (`ProcessPoolExecutor`): Similar to Multiprocessing, offering CPU isolation.
     *   Controlled via the `mode` parameter.
 
 #### **Analysis & Testing**
 *   **`benchmark.py`**:  
     The **Performance Tester**. Automatically runs both methods across 1, 2, 4, and 8 cores/workers on datasets of varying sizes (e.g., 50, 100, 500 images). It calculates **Speedup, Efficiency, and Throughput**, logs results to `benchmark_results_scalability.csv`, and generates performance plots in the `plots/` directory.
 *   **`plots/`**: Directory containing the generated performance graphs (`time_vs_images_{workers}worker.png`).
 
 ---
 
 ## 2. Quick Start
 
 ### Prerequisites
 *   Python 3.x
 *   Virtual Environment (Recommended)
 
 ### Installation
 ```bash
 # 1. Activate your venv (Windows)
 ./venv/Scripts/Activate.ps1
 
 # 2. Install dependencies
 pip install -r requirements.txt
 ```
 
 ### Running the Processor
 You can run the processor manually:
 ```bash
 # Method 1: Multiprocessing (4 cores, 10 images, SAVE output)
 python main.py --count 10 --cores 4 --method mp --save
 
 # Method 2: Concurrent Futures Threads (4 cores, 10 images, SAVE output)
 python main.py --count 10 --cores 4 --method cf --save
 
 # Method 3: Concurrent Futures Process (4 cores, 10 images, SAVE output)
 python main.py --count 10 --cores 4 --method cfp --save
 
 # Run WITHOUT saving (Benchmark Mode - Faster)
 python main.py --count 100 --cores 8 --method cf
 ```
 
 ---
 
 ## 3. Benchmarking
 To generate the full "Speedup and Efficiency" analysis required by the assignment:
 
 ```bash
 python benchmark.py
 ```
 This will:
 1.  Run the benchmark on multiple dataset sizes (e.g., 50, 100, 500 images).
 2.  Test with **1, 2, 4, 8 Workers**.
 3.  Compare **Multiprocessing** vs **Threads** vs **Concurrent Processes**.
 4.  Print detailed **Speedup and Efficiency tables** to the console.
 5.  Save raw data to `benchmark_results_scalability.csv`.
 6.  Generate execution time plots (`time_vs_images_...`) in the `plots/` folder.
 
 ---
 
 ## 4. Filter Pipeline Details
 Every image goes through this exact sequence (defined in `utils.py`):
 1.  **Custom Python Blur**: CPU-intensive, pure Python loop. Added to intentionally hold the GIL and demonstrate the advantage of Process-based parallelism.
 2.  **Brightness**: +60 Value (HSV space).
 3.  **Gaussian Blur**: 3x3 Kernel (Noise reduction).
 4.  **Sharpening**: High-pass filter (Edge enhancement).
 5.  **Grayscale**: Luminance conversion.
 6.  **Sobel Edge Detection**: Gradient calculation.