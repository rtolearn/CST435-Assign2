# CST435 Assignment 2: Parallel Image Processing System

**Course**: CST435: Parallel and Cloud Computing  
**Assignment**: Assignment 2 - Parallel Image Processing on Google Cloud Platform (GCP)

---

## 1. Project Overview

This system allows for high-performance parallel image processing by leveraging both multiprocessing and concurrent execution paradigms. It is designed to benchmark scalability on multi-core cloud architectures, processing large datasets through a compute-intensive filter pipeline.

### System Workflow
The execution follows a linear 6-stage pipeline:

1.  **Initialization**: The controller (`main.py`) indexes the dataset using `utils.py`.
2.  **Dispatch**: Workloads are partitioned and routed to the selected engine (`MP` or `CF`).
3.  **Instantiation**: Worker pools are spawned to separate execution contexts.
4.  **Execution**: Workers process the image pipeline concurrently (non-blocking).
5.  **Synchronization**: Results are aggregated and synchronized.
6.  **Analysis**: Performance metrics (Speedup, Efficiency) are synthesized into visual reports.

---

## 2. Project Structure

The codebase is organized into modular components for logic, execution, and analysis.

```text
CST435-Assign2/
├── images/                      # Raw dataset (Hierarchical format)
├── output/                      # Artifacts & Results Hub
│   ├── benchmark/               # Performance Graphs (Speedup/Efficiency)
│   ├── cf_proc/                 # Output: Concurrent Futures (Process)
│   ├── cf_thread/               # Output: Concurrent Futures (Thread)
│   └── mp/                      # Output: Multiprocessing
├── find_optimal_image_count.py  # Stress Testing Utility
├── main.py                      # Core CLI Controller
├── method_cf.py                 # Wrapper: Concurrent.Futures
├── method_mp.py                 # Wrapper: Multiprocessing
├── utils.py                     # Processing Logic & I/O
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
```

---

## 3. Filter Pipeline Details

To simulate a CPU-bound workload, every image undergoes a sequence of 5 computationally expensive operations:

1.  **Gaussian Blur**: Noise reduction (3x3 Kernel).
2.  **Brightness Adjustment**: HSV Value channel modification (+60).
3.  **Sharpening**: Edge contrast enhancement (Convolution).
4.  **Grayscale**: RGB to Luminance conversion.
5.  **Sobel Edge Detection**: Gradient magnitude calculation.

---

## 4. Google Cloud Platform (GCP) Instructions

### 1. Install system tools and dependencies

sudo apt update && sudo apt install -y git python3-pip unzip sudo apt-get
install -y python3-matplotlib python3-numpy libgl1 libglib2.0-0

### 2. Clone the repository

git clone https://github.com/rtolearn/CST435-Assign2.git cd CST435-Assign2

### 3. Install Python packages

pip3 install -r requirements.txt --break-system-packages

### 4. Import and Unzip Images

mkdir -p images

### (Upload images.zip to your VM home directory first)

mv ~/images.zip ~/CST435-Assign2/images/ cd images unzip images.zip cd ..

## 5. Run the command in GCP

### 1. Find optimal number of images:

python3 find_optimal_image_count.py

#### File path of result for preview

plots/plot_saturation_speedup.png saturation.csv

### 2. Run code (Save mode)

python3 main.py --count 10 --workers 1 2 4 8 --runs 3 --multi-run --save

### 3. Run code (Without Save mode)

python3 main.py --count 10 --workers 1 2 4 8 --runs 3 --multi-run

#### File path of result for preview

plots/plot_saturation_speedup.png output/benchmark/plot_time_vs_workers.png
output/benchmark/plot_speedup.png output/benchmark/plot_efficiency.png
