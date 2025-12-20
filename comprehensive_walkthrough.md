# Comprehensive Project Walkthrough: Parallel Image Processing System

## 1. The Big Picture
**Goal**: We have a large dataset of food images ("Food-101"). We need to apply a series of artistic visual effects (filters) to them. Because processing thousands of images one by one is slow, we use **Parallel Computing** to split the work across multiple CPU cores, making it much faster.

**Analogy**: Imagine you have 1000 dishes to wash.
*   **Sequential (Normal)**: You wash them one by one.
*   **Parallel**: You hire 4 friends (cores). Each person takes 250 dishes and washes them at the same time. The job finishes 4x faster.

---

## 2. Project Architecture (How files fit together)
We split the code into 4 main parts (Modules) to keep it organized.

1.  **`data_loader.py`**: The **File Manager**. It finds, loads, and saves images. It doesn't know *how* to process them, just *where* they are.
2.  **`filters.py`**: The **Artist**. It contains the math to change the image pixels (blur, sharpen, etc). It doesn't know about files, just pixel data.
3.  **`parallel_ops.py`**: The **Manager**. It hires the workers (CPU cores) and assigns them tasks.
4.  **`main.py`**: The **Command Center**. You talk to this file. You tell it "Process 50 images using 4 cores", and it coordinates everything.

---

## 3. Detailed Code Explanation

### Module 1: `data_loader.py` (The File Manager)
This file handles the boring but essential work of reading/writing files.

*   **`get_image_paths(source_dir, limit=None)`**
    *   **What it does**: Looks inside a folder (and the nested `chicken_curry` folder) to find `.jpg` files.
    *   **Why**: We need a list of files to give to our workers.
    *   **Snippet**: `os.scandir(source_dir)` is a fast way to list files.

*   **`load_image(path)`**
    *   **What it does**: Uses the library `cv2` (OpenCV) to turn a file on your hard drive into a matrix of numbers (an image) that the computer can manipulate.
    *   **Why**: We can't do math on a filename; we need the pixel data.

*   **`save_image(image, output_path)`**
    *   **What it does**: Takes the processed matrix of numbers and writes it back to your hard drive as a `.jpg` file.
    *   **Smart Feature**: It automatically creates the output folder if it doesn't exist (`os.makedirs`).

### Module 2: `filters.py` (The Artist)
This is where the magic happens. We decided on a pipeline of **5 specific filters**.

*   **`process_pipeline(image)`**: The master function that runs the 5 steps in order.
    1.  **`adjust_brightness(image, value=60)`**
        *   **Math**: We convert the image to **HSV** (Hue, Saturation, Value) color space. 'Value' is brightness. We add 60 to the 'Value' channel.
        *   **Effect**: Makes the image much brighter.
    2.  **`apply_gaussian_blur(image)`**
        *   **Math**: Uses a "Gaussian Kernel" (a 7x7 grid of weighted numbers). It averages each pixel with its neighbors.
        *   **Effect**: Softens the image, reducing noise and detail.
    3.  **`apply_sharpening(image)`**
        *   **Math**: Uses a "High-Pass Kernel". It subtracts the neighbors from the center pixel to exaggerate differences (edges).
        *   **Effect**: Makes edges look crisp/hard, counteracting the blur.
    4.  **`apply_grayscale(image)`**
        *   **Math**: Calculates `0.299*Red + 0.587*Green + 0.114*Blue`.
        *   **Effect**: Removes color, leaving only black and white light intensity.
    5.  **`apply_sobel_edge_detection(image)`**
        *   **Math**: Calculates the change in intensity (gradient) in the X direction and Y direction. Replaces pixels with that rate of change.
        *   **Effect**: Turns the image into a black canvas where only the *edges* of objects are white lines.

### Module 3: `parallel_ops.py` (The Manager)
This file handles the Parallelism.

*   **`worker_task(task_args)`**
    *   **The Job Description**: This is the exact set of instructions given to each worker.
    *   **Steps**: `Load Image` -> `Process (Filters)` -> `Save Image`.
    *   **Why separate?**: By bundling these 3 steps, the main program just sends a filename ("do image A") and the worker does everything else. This reduces communication traffic.

*   **`run_multiprocessing(tasks, num_cores)`**
    *   **Technology**: Uses Python's native `multiprocessing`.
    *   **How it works**: It spawns completely separate Python programs (Processes). Each has its own memory.
    *   **Pros**: Bypasses Python's "GIL" (Global Interpreter Lock), allowing true parallel CPU usage.
    *   **Cons**: Taking time to start up ("spawn overhead").

*   **`run_concurrent_futures(tasks, num_cores)`**
    *   **Technology**: `ProcessPoolExecutor`.
    *   **How it works**: A modern, easier way to do the same thing as above. It's like a high-level wrapper.

### Module 4: `main.py` (The Command Center)
This ties it all together.

*   **Logic Flow**:
    1.  **Read Args**: Did you ask for 5 images? 2 cores?
    2.  **Setup**: Check if folders exist.
    3.  **Assign Work**: Create a list of tasks (one for each image).
    4.  **Execute**: Call `parallel_ops` to run the tasks.
    5.  **Timer**: Measure exactly how long it took (`time.time()`).
    6.  **Report**: Print the result ("Done in 0.3 seconds!").

---

## 4. How to Run It

You have a `venv` (Virtual Environment) active. This is a sandbox containing all the libraries (OpenCV, etc).

To process 5 images using 2 cores:
```bash
python main.py --count 5 --cores 2 --method mp --save
```

To run the full speed test (Benchmark):
```bash
python benchmark.py
```
This runs the code on 1, 2, 4, and 8 cores automatically and saves the results to a CSV file.
