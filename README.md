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
    *   **Filters**: Brightness, 3x3 Blur, Sharpening, Grayscale, Sobel.
    *   **I/O**: Safe image loading and saving.
    *   **Worker Logic**: The `worker_task` function that processes a single image.
*   **`requirements.txt`**: List of dependencies (`opencv-python`, `numpy`, `matplotlib`).

#### **Parallel Paradigms**
*   **`method_mp.py`**:  
    **Paradigm 1 (Multiprocessing)**. Implements parallelism using `multiprocessing.Pool` (Processes). Best for true CPU parallelism on Linux, but has high startup cost on Windows.
*   **`method_cf.py`**:  
    **Paradigm 2 (Concurrent Futures)**. Implements parallelism using `ThreadPoolExecutor` (Threads). Extremely fast for this specific workload because OpenCV operations release the Python GIL.

#### **Analysis & Testing**
*   **`benchmark.py`**:  
    The **Performance Tester**. Automatically runs both methods across 1, 2, 4, and 8 cores, calculates Speedup/Efficiency, generates a data CSV, and plots a comparison graph.
*   **`benchmark_plot.png`**: The visual result of the benchmark.rt

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
Every image goes through this exact sequence (defined in `utils.py`):
1.  **Brightness**: +60 Value (HSV space).
2.  **Gaussian Blur**: 3x3 Kernel (Noise reduction).
3.  **Sharpening**: High-pass filter (Edge enhancement).
4.  **Grayscale**: Luminance conversion.
5.  **Sobel Edge Detection**: Gradient calculation.