# CST435 Assignment 2: Parallel Image Processing System

**Course**: CST435: Parallel and Cloud Computing  
 **Assignment**: Assignment 2 - Parallel Image Processing on GCP

---

## 1. Project Overview

This project implements a high-performance parallel image processing system capable of filtering thousands of images using multiple CPU cores. It compares two parallel paradigms: **Multiprocessing** (Processes) vs **Concurrent Futures** (Threads).

### 📂 File Structure & Functionality

The code is organized into modular components for clarity and reusability:

#### **Core Logic**

- **`main.py`**:  
  The **Command Center**. It handles argument parsing (`--count`, `--cores`, `--method`), orchestrates the workflow, and reports success/failure. It imports the specific method modules.
- **`utils.py`**:  
  The **Unified Helper Library**. Implements the "Separation of Concerns" pattern by containing:
  - **Processing Pipeline**: Includes a **CPU-intensive Custom Blur** (pure Python) to demonstrate GIL bottlenecks and make Process-based parallelism shine, along with standard OpenCV filters (Brightness, Gaussian Blur, Sharpening, Grayscale, Sobel).
  - **I/O**: Safe image loading and saving logic.
  - **Worker Logic**: The `worker_task` function that processes a single image.
- **`requirements.txt`**: List of dependencies (`opencv-python`, `numpy`, `matplotlib`).

#### **Parallel Paradigms**

- **`method_mp.py`**:  
  **Paradigm 1 (Multiprocessing)**. Implements parallelism using `multiprocessing.Pool` (Processes). Best for true CPU parallelism on Linux and handling CPU-bound Python tasks (bypassing GIL).
- **`method_cf.py`**:  
  **Paradigm 2 & 3 (Concurrent Futures)**. Unified module implementing both:
  - **Threads** (`ThreadPoolExecutor`): Fast for I/O-bound tasks but limited by GIL for CPU-bound Python code.
  - **Processes** (`ProcessPoolExecutor`): Similar to Multiprocessing, offering CPU isolation.
  - Controlled via the `mode` parameter.

#### **Analysis & Testing**

- **`benchmark.py`**:  
  The **Performance Tester**. Automatically runs both methods across 1, 2, 4, and 8 cores/workers on datasets of varying sizes (e.g., 50, 100, 500 images). It calculates **Speedup, Efficiency, and Throughput**, logs results to `benchmark_results_scalability.csv`, and generates performance plots in the `plots/` directory.
- **`plots/`**: Directory containing the generated performance graphs (`time_vs_images_{workers}worker.png`).

---

## 2. Quick Start

### Prerequisites

- Python 3.x
- Virtual Environment (Recommended)

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

### Command Line Usage

The `benchmark.py` script is now fully configurable via command line arguments. You can customize image count, worker counts, number of runs, and more without editing the code.

#### **Basic Syntax**

```bash
python benchmark.py [--count N] [--workers W ...] [--runs R] [--multi-run] [--plots] [--no-plots]
```

#### **Arguments**

- `--count N` : Number of images to process (default: 50)
- `--workers W ...` : Worker counts to test, space-separated (default: 1 2 4 8)
- `--runs R` : Number of runs per configuration (default: 1)
- `--multi-run` : Enable multiple runs and average calculation (default: False)
- `--plots` : Generate performance plots (enabled by default)
- `--no-plots` : Disable plot generation

#### **Examples**

**1. Large-scale single run (3000 images, 1,2,4,8 workers):**

```bash
python benchmark.py --count 3000 --workers 1 2 4 8 --runs 1
```

**2. Large-scale with multiple runs for averaging (3000 images, 3 runs):**

```bash
python benchmark.py --count 3000 --workers 1 2 4 8 --runs 3 --multi-run
```

**3. Performance testing with fewer images (1000 images, single run):**

```bash
python benchmark.py --count 1000 --workers 1 2 4 8 --runs 1
```

**4. Quick test with minimal images (50 images, single run):**

```bash
python benchmark.py --count 50 --workers 1 2 4 8 --runs 1
```

**5. Extended analysis with multiple runs (1500 images, 3 runs each):**

```bash
python benchmark.py --count 1500 --workers 1 2 4 8 --runs 3 --multi-run
```

**6. Custom worker scaling test (500 images with more workers):**

```bash
python benchmark.py --count 500 --workers 1 2 4 8 16 --runs 1
```

**7. Generate results without plots:**

```bash
python benchmark.py --count 2000 --workers 1 2 4 8 --runs 1 --no-plots
```

**8. Default configuration (50 images, default workers [1,2,4,8], single run, with plots):**

```bash
python benchmark.py
```

#### **Output**

The benchmark will:

1. Display **live results** as each test completes (Method | Workers | Run | Time)
2. Save raw data to `benchmark_results_averaged.csv` (Methods as columns, Runs as rows)
3. Print detailed **Performance Analysis Table** with:
   - Execution times for all methods (MP, CF_Proc, CF_Thread)
   - **Speedup** metrics (T(1) / T(n)) where Serial = baseline
   - **Efficiency** metrics (Speedup / Workers × 100%)
   - **Best method** for each run
4. Generate 3 performance plots (if `--plots` enabled):
   - **Execution Time vs Workers** - Shows how runtime decreases with more workers
   - **Speedup vs Workers** - Shows speedup factor relative to serial execution
   - **Efficiency vs Workers** - Shows parallel efficiency percentage

#### **Example Output Structure**

```
Method       | Workers    | Run  | Time (s)
--------------------------------------------------
MP           | Serial     | 1    | 24.7887
CF_Proc      | Serial     | 1    | 25.2750
CF_Thread    | Serial     | 1    | 23.4894
MP           | 2          | 1    | 14.1448
...
--------------------------------------------------

DETAILED PERFORMANCE ANALYSIS: All Runs with Speedup & Efficiency
(Serial = 1 worker baseline for speedup/efficiency calculation)
Workers    Run      MP           CF_Proc      CF_Thread    Best         Speedup      Efficiency
Serial     Run1      24.7887     25.2750     23.4894     CF_Thread   1.0000       100.00%
2          Run1      14.1448     14.2354     13.2832     CF_Thread   1.7684       88.42%
4          Run1      9.6266      9.1495      8.5215      CF_Thread   2.7565       68.91%
8          Run1      7.9206      8.7267      6.8570      CF_Thread   3.4256       42.82%

CSV & Plots generated in: benchmark_results_averaged.csv and plots/
```

---

## 4. Filter Pipeline Details

Every image goes through this exact sequence (defined in `utils.py`):

1.  **Custom Python Blur**: CPU-intensive, pure Python loop. Added to intentionally hold the GIL and demonstrate the advantage of Process-based parallelism.
2.  **Brightness**: +60 Value (HSV space).
3.  **Gaussian Blur**: 3x3 Kernel (Noise reduction).
4.  **Sharpening**: High-pass filter (Edge enhancement).
5.  **Grayscale**: Luminance conversion.
6.  **Sobel Edge Detection**: Gradient calculation.
