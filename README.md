# CST435 Assignment 2: Parallel Image Processing System

**Course**: CST435: Parallel and Cloud Computing  
**Assignment**: Assignment 2 - Parallel Image Processing on Google Cloud
Platform (GCP)

---

## 1. Project Overview

This project implements a high-performance parallel image processing system
capable of filtering thousands of images efficiently. The primary goal is to
compare different parallel paradigms in Python to understand how they handle
CPU-bound tasks and the Global Interpreter Lock (GIL).

### Key Features:

- **Parallel Paradigms**: Compares `Multiprocessing` (Process-based) vs.
  `Concurrent Futures` (Process & Thread-based).
- **Intensive Pipeline**: Includes a custom-built Python blur to simulate high
  CPU load.
- **Automated Benchmarking**: Measures execution time, speedup, and efficiency
  across varying worker counts.
- **Cloud Ready**: Optimized for deployment on Google Cloud Platform (GCP)
  Compute Engine.

---

## 2. Project Structure

```text
.
├── images/               # Input image folders (imageFolder 1, 2, 3)
├── output/               # Processed images and benchmark results
├── plots/                # Generated performance visualizations
├── find_optimal_image_count.py  # Utility to test scaling limits
├── main.py               # Main entry point for benchmarking
├── method_cf.py          # Concurrent Futures implementation
├── method_mp.py          # Multiprocessing implementation
├── utils.py              # Image processing filter pipeline
└── requirements.txt      # Project dependencies
```

## 3. Filter Pipeline Details

Every image goes through a 6-stage sequence. This pipeline is designed to be
computationally expensive to test parallel efficiency:

1.  **Custom Python Blur**: A pure Python loop implementation. This is
    intentionally slow to demonstrate the **Global Interpreter Lock (GIL)**
    bottleneck in threads.
2.  **Brightness**: +60 Value (HSV space).
3.  **Gaussian Blur**: 3x3 Kernel (Noise reduction).
4.  **Sharpening**: High-pass filter (Edge enhancement).
5.  **Grayscale**: Luminance conversion.
6.  **Sobel Edge Detection**: Gradient calculation.

## 4. Google Cloud Platform (GCP) Instructions

### 1. Install system tools and dependencies

sudo apt update && sudo apt install -y git python3-pip unzip sudo apt-get install -y python3-matplotlib python3-numpy libgl1 libglib2.0-0

### 2. Clone the repository

git clone https://github.com/rtolearn/CST435-Assign2.git cd CST435-Assign2

### 3. Install Python packages

pip3 install -r requirements.txt --break-system-packages

### 4. Import and Unzip Images

mkdir -p images

### (Upload images.zip to your VM home directory first)

mv '*.zip' ~/CST435-Assign2/images/ 

mv .zip CST435-Assign2/images/ && cd CST435-Assign2/images/ && unzip ".zip"

cd images unzip images.zip cd ..

## 5. Run the command in GCP

### 1. Find optimal number of images:

python3 find_optimal_image_count.py

#### File path of result for preview

plots/plot_saturation_speedup.png saturation.csv

### 2. Run code (Save mode)

python3 main.py --count 4000 --workers 1 2 4 8 --runs 3 --multi-run --save

### 3. Run code (Without Save mode)

python3 main.py --count 10 --workers 1 2 4 8 --runs 3 --multi-run

#### File path of result for preview

plots/plot_saturation_speedup.png output/benchmark/plot_time_vs_workers.png
output/benchmark/plot_speedup.png output/benchmark/plot_efficiency.png
