# CST435 Assignment 2: Parallel Image Processing System

**Course**: CST435: Parallel and Cloud Computing  
 **Assignment**: Assignment 2 - Parallel Image Processing on GCP

---

## 1. Project Overview

This project implements a high-performance parallel image processing system
capable of filtering thousands of images using multiple CPU cores. It compares
two parallel paradigms: **Multiprocessing** (Processes) vs **Concurrent
Futures** (Threads).

### 📂 File Structure & Functionality

The code is organized into modular components for clarity and reusability:

#### **Core Logic**

- **`main.py`**:  
  The **Command Center**. It handles argument parsing (`--count`, `--cores`,
  `--method`), orchestrates the workflow, and reports success/failure. It
  imports the specific method modules.
- **`utils.py`**:  
  The **Unified Helper Library**. Implements the "Separation of Concerns"
  pattern by containing:
  - **Processing Pipeline**: Includes a **CPU-intensive Custom Blur** (pure
    Python) to demonstrate GIL bottlenecks and make Process-based parallelism
    shine, along with standard OpenCV filters (Brightness, Gaussian Blur,
    Sharpening, Grayscale, Sobel).
  - **I/O**: Safe image loading and saving logic.
  - **Worker Logic**: The `worker_task` function that processes a single image.
- **`requirements.txt`**: List of dependencies (`opencv-python`, `numpy`,
  `matplotlib`).

#### **Parallel Paradigms**

- **`method_mp.py`**:  
  **Paradigm 1 (Multiprocessing)**. Implements parallelism using
  `multiprocessing.Pool` (Processes). Best for true CPU parallelism on Linux and
  handling CPU-bound Python tasks (bypassing GIL).
- **`method_cf.py`**:  
  **Paradigm 2 & 3 (Concurrent Futures)**. Unified module implementing both:
  - **Threads** (`ThreadPoolExecutor`): Fast for I/O-bound tasks but limited by
    GIL for CPU-bound Python code.
  - **Processes** (`ProcessPoolExecutor`): Similar to Multiprocessing, offering
    CPU isolation.
  - Controlled via the `mode` parameter.

#### **Analysis & Testing**

- **`benchmark.py`**:  
  The **Performance Tester**. Automatically runs both methods across 1, 2, 4,
  and 8 cores/workers on datasets of varying sizes (e.g., 50, 100, 500 images).
  It calculates **Speedup, Efficiency, and Throughput**, logs results to
  `benchmark_results_scalability.csv`, and generates performance plots in the
  `plots/` directory.
- **`plots/`**: Directory containing the generated performance graphs
  (`time_vs_images_{workers}worker.png`).

---

## 2. Quick Start

### Prerequisites

- Python 3.x
- Virtual Environment (Recommended)

### Installation

```bash
# 2. Install dependencies
pip install -r requirements.txt
```

### Running the Processor

You can run the processor manually:



---

## 3. Benchmarking

### Command Line Usage

The `benchmark.py` script is now fully configurable via command line arguments.
You can customize image count, worker counts, number of runs, and more without
editing the code.

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

#### **Output**

The benchmark will:

1. Display **live results** as each test completes (Method | Workers | Run |
   Time)
2. Save raw data to `benchmark_results_averaged.csv` (Methods as columns, Runs
   as rows)
3. Print detailed **Performance Analysis Table** with:
   - Execution times for all methods (MP, CF_Proc, CF_Thread)
   - **Speedup** metrics (T(1) / T(n)) where Serial = baseline
   - **Efficiency** metrics (Speedup / Workers × 100%)
   - **Best method** for each run
4. Generate 3 performance plots (if `--plots` enabled):
   - **Execution Time vs Workers** - Shows how runtime decreases with more
     workers
   - **Speedup vs Workers** - Shows speedup factor relative to serial execution
   - **Efficiency vs Workers** - Shows parallel efficiency percentage

#### **Example Output Structure**


## 4. Filter Pipeline Details

Every image goes through this exact sequence (defined in `utils.py`):

1.  **Custom Python Blur**: CPU-intensive, pure Python loop. Added to
    intentionally hold the GIL and demonstrate the advantage of Process-based
    parallelism.
2.  **Brightness**: +60 Value (HSV space).
3.  **Gaussian Blur**: 3x3 Kernel (Noise reduction).
4.  **Sharpening**: High-pass filter (Edge enhancement).
5.  **Grayscale**: Luminance conversion.
6.  **Sobel Edge Detection**: Gradient calculation.













## 4. Command to run the code:

python main.py --count 100 --workers 1 2 4 8 --runs 3 --multi-run

## 5. Command used in Google Cloud Platform

Command:

Install necessary tools: sudo apt update && sudo apt install -y git python3-pip
pip install matplotlib numpy
sudo apt-get update
sudo apt-get install python3-matplotlib python3-numpy -y
sudo apt-get install unzip -y
unzip libgl1 libglib2.0-0

Clone: git clone https://github.com/rtolearn/CST435-Assign2.git

After cloning:

- cd CST435-Assign2
- pip3 install -r requirements.txt --break-system-packages

Import files (zip -> unzip)

- mkdir -p images
- ls -lh (check if the zip file is import)
- mv ~/images.zip ~/CST435-Assign2/images/
- cd images
- unzip images.zip
- cd ..

Start the process: python3 main.py --count 500 --workers 1 2 4 8 --runs 3
