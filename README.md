File Architecture: 
CST435-Assignment2-Group/
│
├── README.md                      # Critical: Project description & instructions for the grader [cite: 50]
├── requirements.txt               # List dependencies (opencv-python, numpy, etc.) for GCP setup
├── .gitignore                     # Ignore input_images/ (if large), output_images/, __pycache__/
│
├── input_images/                  # Your "manageable subset" of Food-101 for testing [cite: 21]
│   ├── class_subset/              # e.g., 50-100 images for testing
│   └── README.txt                 # Explain where these images came from
│
├── Method_1_Multiprocessing/      # Paradigm 1: Python Multiprocessing [cite: 39]
│   ├── main.py                    # Entry point: Loads images -> distributes work -> saves results
│   ├── filters.py                 # The 5 filter functions (Gray, Blur, Sobel, Sharp, Brightness)
│   └── outputs/                   # (Empty folder) Where processed images go
│
├── Method_2_ConcurrentFutures/    # Paradigm 2: Python Concurrent.Futures [cite: 40]
│   ├── main.py                    # Entry point (using ThreadPoolExecutor or ProcessPoolExecutor)
│   ├── filters.py                 # Same filter logic, but kept separate to ensure isolation
│   └── outputs/                   # (Empty folder)
│
├── Analysis/                      # For your Technical 
│    ├── benchmarks.csv             # Record your speedup/efficiency metrics here 
│    ├── charts/                    # Save your matplotlib comparison graphs here
│    └── performance_analysis.md    # Draft your discussion for the report
├── gitignore
├── README.md
├── requirement.txt # Download all the library when it come to the deployment in Google Cloud Platform