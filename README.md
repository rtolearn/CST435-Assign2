# CST435 Assignment 2: Parallel Image Processing System

**Course:** CST435: Parallel and Cloud Computing
**Assignment:** Assignment 2 - Parallel Image Processing on GCP

---

## 🚀 Quick Start & Run Commands

### 1. Prerequisites
Ensure you have Python installed. It is recommended to run these commands from the **root directory** of the project (`CST435-Assignment2-Group/`).

### 2. Installation
Install the required dependencies (OpenCV, NumPy, Matplotlib) using the provided requirements file:
```bash
pip install -r requirements.txt
```
### 3. Run first methodology
cd Method_1_Multiprocessing
python main.py

### 4. Run second methodology
cd Method_2_ConcurrentFutures
python main.py

### 5. Run second methodology
cd ../Analysis
python generate_charts.py


CST435-Assignment2-Group/
│
├── README.md                      # Critical: Project description & instructions for the grader [cite: 50]
├── requirements.txt               # Dependencies (opencv-python-headless, numpy, matplotlib)
├── .gitignore                     # Ignores large input_images/, output_images/, and __pycache__
│
├── input_images/                  # Dataset: Subset of Food-101 for testing [cite: 20-21]
│   ├── class_subset/              # Contains the source .jpg images
│   └── README.txt                 # Data source attribution
│
├── Method_1_Multiprocessing/      # Paradigm 1: Python Multiprocessing [cite: 37-39]
│   ├── main.py                    # Entry point: Orchestrates parallel workers using multiprocessing.Pool
│   ├── filters.py                 # Implementation of 5 filters (Gray, Blur, Sobel, Sharpen, Brightness)
│   └── outputs/                   # Processed images are saved here
│
├── Method_2_ConcurrentFutures/    # Paradigm 2: Python Concurrent.Futures [cite: 37, 40]
│   ├── main.py                    # Entry point: Orchestrates parallel workers using ProcessPoolExecutor
│   ├── filters.py                 # Identical filter logic to ensure fair performance comparison
│   └── outputs/                   # Processed images are saved here
│
└── Analysis/                      # Performance Analysis & Technical Report Resources [cite: 44]
    ├── benchmarks.csv             # Raw timing data (Speedup/Efficiency metrics)
    ├── charts/                    # Generated Matplotlib comparison graphs
    ├── performance_analysis.md    # Discussion of scalability and bottlenecks
    └── generate_charts.py         # Script to visualize the results


### This has to be done manually as importing the whole dataset into git is not recommended (currently we are using chicken curry)
├── input_images/        
├── class_subset/   (put the folder of your dataset here)