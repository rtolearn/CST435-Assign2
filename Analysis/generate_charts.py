import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# 1. INPUT YOUR DATA HERE
# ==========================================
# Copy the "Cores" column from your terminal output
cores = [1, 2, 4, 8]  

# Copy "Time (s)" from Method 1 (Multiprocessing)
times_method1 = [15.2, 7.8, 4.1, 2.3]  

# Copy "Time (s)" from Method 2 (Concurrent Futures)
times_method2 = [15.5, 8.0, 4.3, 2.4]  
# ==========================================

# Create output folder if it doesn't exist
output_folder = "charts"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Calculate Speedup (Time_1_Core / Time_N_Cores)
speedup_m1 = [times_method1[0] / t for t in times_method1]
speedup_m2 = [times_method2[0] / t for t in times_method2]

# Ideal Speedup (Linear) for comparison
ideal_speedup = cores

# --- CHART 1: EXECUTION TIME (Bar Chart) ---
plt.figure(figsize=(10, 6))
x = np.arange(len(cores))
width = 0.35

plt.bar(x - width/2, times_method1, width, label='Multiprocessing', color='#4285F4') # Google Blue
plt.bar(x + width/2, times_method2, width, label='Concurrent.Futures', color='#34A853') # Google Green

plt.xlabel('Number of Cores')
plt.ylabel('Time (seconds)')
plt.title('Execution Time Comparison')
plt.xticks(x, cores)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Save
plt.savefig(f"{output_folder}/execution_time.png")
print(f"Generated {output_folder}/execution_time.png")
plt.close()

# --- CHART 2: SPEEDUP (Line Chart) ---
plt.figure(figsize=(10, 6))

plt.plot(cores, speedup_m1, marker='o', label='Multiprocessing', color='#4285F4', linewidth=2)
plt.plot(cores, speedup_m2, marker='s', label='Concurrent.Futures', color='#34A853', linewidth=2)
plt.plot(cores, ideal_speedup, '--', label='Ideal Linear Speedup', color='gray', alpha=0.5)

plt.xlabel('Number of Cores')
plt.ylabel('Speedup Factor (x times faster)')
plt.title('Speedup Analysis')
plt.xticks(cores)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)

# Save
plt.savefig(f"{output_folder}/speedup_chart.png")
print(f"Generated {output_folder}/speedup_chart.png")
plt.close()