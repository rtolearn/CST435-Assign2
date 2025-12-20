# Technical Report: Parallel Image Processing System

**Course**: CST435 - Parallel Computing
**Project**: Assignment 2 (Food-101 Processing)

## 1. System Overview
This project implements a parallel image processing pipeline for the Food-101 dataset. The system applies a chain of 5 computational filters to images using two Python parallel paradigms: `multiprocessing` and `concurrent.futures`. Ideally, the system is designed to run on GCP for scalability.

### Architecture
The solution follows a modular architecture:
*   **`data_loader.py`**: Managing file I/O, ensuring thread-safe/process-safe file handling by keeping workers stateless.
*   **`filters.py`**: Pure functional implementation of the 5 filters (Brightness, Blur, Sharpen, Grayscale, Sobel).
*   **`parallel_ops.py`**: The execution engines distributing work across cores.
*   **`main.py`**: The CLI controller for execution and benchmarking.

## 2. Implementation Details

### The Filter Pipeline
Each image undergoes the following transformation:
1.  **Brightness**: Increased by +60 (HSV conversion).
2.  **Gaussian Blur**: 7x7 Kernel (noise reduction).
3.  **Sharpening**: Custom High-Pass Kernel (edge enhancement).
4.  **Grayscale**: Luminance conversion.
5.  **Sobel Edge Detection**: Gradient magnitude calculation.

### Parallel Strategies
*   **Multiprocessing (`mp`)**: Uses `multiprocessing.Pool`. This spawns separate memory spaces for each worker. Heavy overhead for spawning but bypasses the Global Interpreter Lock (GIL).
*   **Concurrent Futures (`cf`)**: Uses `ProcessPoolExecutor`. A higher-level abstraction over multiprocessing.

## 3. Performance Analysis

### Benchmark Setup
*   **Dataset**: Subset of 20 images from `chicken_curry`.
*   **Environment**: Windows (Process Spawning).
*   **Metric**: Total Execution Time (seconds).

### Results
| Method | Cores | Time (s) | Speedup | Efficiency |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (1 Core)** | **1** | **0.3937** | **1.00x** | **1.00** |
| Multiprocessing | 2 | 0.3433 | 1.15x | 0.57 |
| Multiprocessing | 4 | 0.4309 | 0.91x | 0.23 |
| Multiprocessing | 8 | 0.4832 | 0.81x | 0.10 |
| Concurrent Futures | 2 | 0.4114 | 0.96x | 0.48 |
| Concurrent Futures | 4 | 0.4562 | 0.86x | 0.22 |

### Observations
1.  **Overhead Dominance**: The processing time for 20 images is very short (~0.4s). The overhead of creating processes on Windows (which does not support `fork()`) is significant.
2.  **Diminishing Returns**: As core count increases to 4 and 8, the time *increases*. This is because the time spent spawning 8 processes and pickling data exceeds the time saved by parallelizing such a small workload.
3.  **Recommendation**: For this specific dataset size, 2 cores provided the optimal balance. For a production run with thousands of images, the speedup would likely scale better with more cores as the computation time would vastly exceed the startup overhead.

## 4. Conclusion
The modular architecture successfully decouples logic from execution, allowing easy swapping of parallel backends. While the benchmark showed limited speedup for the small test set, the system is correctly implemented to scale for larger loads where parallel processing is essential.
