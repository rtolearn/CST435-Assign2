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
*   **`tasks.py`**:  
    The **Worker Logic**. Contains the `worker_task(args)` function, which represents a single unit of work (Load Image -> Process Pipeline -> Save Image). Used by both paradigms to share logic.
*   **`filters.py`**:  
    The **Mathematical Library**. Contains the pure implementation of the 5 image processing algorithms (Brightness, 3x3 Blur, Sharpening, Grayscale, Sobel).
*   **`data_loader.py`**:  
    The **I/O Manager**. Handles safely reading images from disk and creating output directories/files.

#### **Parallel Paradigms**
*   **`method_mp.py`**:  
    **Paradigm 1 (Multiprocessing)**. Implements parallelism using `multiprocessing.Pool`. This creates separate OS processes for each worker, bypassing the Python GIL. optimal for CPU-heavy tasks on Linux, but has high startup overhead on Windows.
*   **`method_cf.py`**:  
    **Paradigm 2 (Concurrent Futures)**. Implements parallelism using `ThreadPoolExecutor`. This uses Threads. While usually limited by the GIL, it performs exceptionally well here because OpenCV releases the GIL during heavy operations.

#### **Analysis & Testing**
*   **`benchmark.py`**:  
    The **Performance Tester**. Automatically runs both methods across 1, 2, 4, and 8 cores, calculates Speedup/Efficiency, generates a data CSV, and plots a comparison graph.
*   **`benchmark_plot.png`**: The visual result of the benchmark.
*   **`visualize_steps.py`**: A debug script that saves intermediate images (e.g. `step1_brightness.jpg`) to verified the filter chain visually.
*   **`verify_phase1.py`**: A simple health-check script to confirm the pipeline works on a single image.

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
You can run the processor manually:
```bash
# Method 1: Multiprocessing (4 cores, 10 images)
python main.py --count 10 --cores 4 --method mp --save

# Method 2: Concurrent Futures/Threads (4 cores, 10 images)
python main.py --count 10 --cores 4 --method cf --save
```

---

## 3. Benchmarking
To generate the "Speedup and Efficiency" report required by the assignment:

```bash
python benchmark.py
```
This will:
1.  Run the full 1000-image dataset on 1, 2, 4, 8 cores.
2.  Compare Multiprocessing vs Threads side-by-side.
3.  Output `benchmark_results.csv` and `benchmark_plot.png`.

---

## 4. Filter Pipeline Details
Every image goes through this exact sequence (defined in `filters.py`):
1.  **Brightness**: +60 Value (HSV space).
2.  **Gaussian Blur**: 3x3 Kernel (Noise reduction).
3.  **Sharpening**: High-pass filter (Edge enhancement).
4.  **Grayscale**: Luminance conversion.
5.  **Sobel Edge Detection**: Gradient calculation.