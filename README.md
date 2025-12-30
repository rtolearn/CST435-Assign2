# Parallel Image Processing System

**Course**: CST435 - Parallel and Cloud Computing  
**Assignment**: Assignment 2 - Parallel Image Processing on GCP

---

## 1. Project Overview
This project implements a high-performance image processing pipeline designed to benchmark and analyze parallel computing paradigms. It leverages the **Food-101** dataset to simulate a large-scale computational workload, applying a series of computationally intensive filters (Gaussian Blur, HSV Brightness, Sharpening, Grayscale, and Sobel Edge Detection) to thousands of images.

The core objective is to evaluate the scalability and efficiency of **Multiprocessing (IPC-based)** versus **Concurrent Futures (Thread/Process-based)** architectures. The system provides a unified CLI for execution, automated benchmarking, and visual performance analytics (Speedup, Efficiency, and Throughput graphs), making it suitable for deployment on high-core cloud infrastructure like **Google Cloud Platform (GCP)**.

---

## 2. Code Organization

The project is structured into modular components to ensure separation of concerns between control logic, processing implementation, and analysis tools.

```text
CST435-Assign2/
├── images/                      # Raw input dataset (hierarchical structure)
├── output/                      # Artifacts and results
│   ├── benchmark/               # Generated performance plots
│   │   ├── plot_efficiency.png
│   │   ├── plot_speedup.png
│   │   └── plot_time_vs_workers.png
│   ├── mp/                      # Output images from Multiprocessing
│   ├── cf_proc/                 # Output images from CF (Process)
│   └── cf_thread/               # Output images from CF (Thread)
├── main.py                      # CLI Controller & Orchestrator
├── benchmark.py                 # Automated Benchmark Suite
├── utils.py                     # Core Processing Library (Filters & I/O)
├── method_mp.py                 # Multiprocessing Implementation
├── method_cf.py                 # Concurrent Futures Implementation
├── find_optimal_image_count.py  # Load Stress Testing Tool
├── requirements.txt             # Dependency Definitions
└── README.md                    # Project Documentation
```

---

## 3. Quick Start

### Prerequisites
*   Python 3.8+
*   Virtual Environment (Recommended)

### Installation
```bash
# 1. Create and activate venv
python -m venv venv
./venv/Scripts/Activate.ps1  # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt
```

### Usage
Run the processor via the centralized `main.py` controller:

```bash
# Basic Run: Process 50 images with 4 workers using Multiprocessing
python main.py --count 50 --workers 4 --save

# Full Benchmark: Test 1, 2, 4, 8 workers on 500 images (3 runs each for averaging)
python main.py --count 500 --runs 3 --save
```

---

## 4. Google Cloud Platform (GCP) Instructions

To deploy and benchmark this system on a GCP Compute Engine instance (e.g., e2-standard-8), follow these steps:

### 4.1. VM Setup
1.  **Create Instance**:
    *   **Machine Type**: `e2-standard-8` (8 vCPUs, 32 GB memory).
    *   **OS**: Ubuntu 20.04 LTS (recommended for Python multiprocessing).
    *   **Disk**: 20 GB+ SSD.
2.  **SSH Connection**: Connect to your instance via the Gcloud Console or terminal.

### 4.2. Environment Configuration
Update the system and install necessary libraries:

```bash
# Update package list
sudo apt-get update
sudo apt-get upgrade -y

# Install Python & Pip
sudo apt-get install python3-pip python3-venv git htop -y

# Install core system dependencies for OpenCV (headless)
sudo apt-get install libgl1-mesa-glx libglib2.0-0 -y
```

### 4.3. Project Deployment
```bash
# Clone the repository
git clone https://github.com/rtolearn/CST435-Assign2.git
cd CST435-Assign2

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Python Requirements
pip install -r requirements.txt
```

### 4.4. Running the Benchmark
Execute the benchmark suite to generate performance data. This script will utilize all 8 vCPUs.

```bash
# Run the benchmark (ensure you are inside the venv)
python main.py --count 5000 --runs 3 --save
```
*Note: Depending on the dataset size, this may take several minutes.*

### 4.5. Result Preview Paths
After the benchmark completes, the results and plots will be available at the following paths:

*   **Performance Plots**:
    *   `output/benchmark/plot_time_vs_workers.png`
    *   `output/benchmark/plot_speedup.png`
    *   `output/benchmark/plot_efficiency.png`
*   **Processed Images (if --save enabled)**:
    *   `output/mp/images/`
    *   `output/cf_proc/images/`
    *   `output/cf_thread/images/`

---

## 5. Filter Pipeline Details
The application applies a computationally intensive sequence of operations to every image:
1.  **Gaussian Blur**: 3x3 Kernel noise reduction.
2.  **Brightness Adjustment**: HSV Value channel modification (+60).
3.  **Sharpening**: Convolution with high-pass kernel.
4.  **Grayscale**: RGB to Single-channel conversion.
5.  **Sobel Edge Detection**: Gradient magnitude calculation (X+Y).
