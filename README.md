# CST435 Assignment 2: Parallel Image Processing System

**Course**: CST435: Parallel and Cloud Computing  
**Assignment**: Assignment 2 - Parallel Image Processing on GCP

---

## 1. Project Overview & Architecture
This project implements a high-performance parallel image processing system capable of filtering thousands of images using multiple CPU cores.

**The Goal**: Apply a chain of 5 effects (Brightness, Blur, Sharpen, Grayscale, Sobel) to the Food-101 dataset.  
**The Solution**: We compare two Python parallel paradigms:
1.  **Multiprocessing (`mp`)**: Uses separate Processes (bypass GIL, high overhead on Windows).
2.  **Concurrent Futures (`cf`)**: Implemented using **Threads** to demonstrate the difference (fast startup, but limited by GIL). *Note: Threads perform surprisingly well here due to OpenCV releasing the GIL.*

### File Structure
We use a clean, modular architecture:
*   **`main.py`**: The Command Center. Usage: `python main.py --count 10`.
*   **`parallel_ops.py`**: The Engine. Contains the logic for both Multiprocessing and Threading engines.
*   **`filters.py`**: The Artist. Contains the math for the 5 image filters.
*   **`data_loader.py`**: The File Manager. Handles loading/saving images.
*   **`benchmark.py`**: The Tester. Auto-runs speed tests and plots graphs.

---

## 2. Quick Start

### Prerequisites
*   Python 3.x
*   Virtual Environment (Recommended)

### Installation
```bash
# 1. Activate your venv (Windows)
./venv/Scripts/Activate.ps1

# 2. Install dependencies (OpenCV, Matplotlib, etc)
pip install -r requirements.txt
```

### Running the Processor
You can run the processor manually on a small set of images to see it work.
```bash
# Process 10 images using 4 cores with Multiprocessing
python main.py --count 10 --cores 4 --method mp --save

# Process 10 images using 4 cores with Threads
python main.py --count 10 --cores 4 --method cf --save
```
*   Check the `outputs/` folder to see the results.

---

## 3. Benchmarking
To satisfy the assignment usage of "Speedup and Efficiency metrics", use the automated benchmark tool.

```bash
python benchmark.py
```
This script will:
1.  Run the pipeline on **1, 2, 4, 8 cores**.
2.  Test **both** Multiprocessing and Threading.
3.  Calculate **Speedup** (vs 1 core) and **Efficiency**.
4.  Generate a side-by-side comparison table.
5.  Generate a visual plot: `benchmark_plot.png`.
6.  Save raw data to: `benchmark_results.csv`.

---

## 4. Technical Details (For Graders)

### The Filter Pipeline
Every image goes through this exact sequence:
1.  **Brightness**: +60 Value (HSV space).
2.  **Gaussian Blur**: 7x7 Kernel (Noise reduction).
3.  **Sharpening**: High-pass filter (Edge enhancement).
4.  **Grayscale**: Luminance conversion.
5.  **Sobel Edge Detection**: Gradient calculation.

### Design Decisions
*   **Process vs Threads**: We implemented both. 
    *   `--method mp` uses `multiprocessing.Pool` (Processes).
    *   `--method cf` uses `ThreadPoolExecutor` (Threads).
*   **Input Data**: The system expects input images in `chicken_curry/chicken_curry/`.
*   **Output Data**: Processed images are saved to `outputs/` (automatically created).