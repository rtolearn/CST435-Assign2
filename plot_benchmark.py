import csv
import os
import matplotlib.pyplot as plt
from collections import defaultdict

def generate_plots(csv_path="benchmark_results_scalability.csv"):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run benchmark.py first.")
        return

    print(f"Reading data from {csv_path}...")
    
    # Data Structure: data[worker_count][method] = [(images, time), ...]
    plot_data = defaultdict(lambda: defaultdict(list))
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    w = int(row['Workers'])
                    img = int(row['Images'])
                    method = row['Method']
                    time_val = float(row['Time'])
                    
                    plot_data[w][method].append((img, time_val))
                    count += 1
                except ValueError:
                    continue
        print(f"Loaded {count} data points.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Output directory
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating plots...")
    
    # Sort data for distinct lines
    # Map CSV method names to Plot labels/Styles
    # CSV Method names: "Multiprocessing", "CF (Process)", "CF (Thread)"
    styles = {
        "Multiprocessing": {'marker': 'o', 'linestyle': '-', 'label': 'Multiprocessing'},
        "CF (Process)":    {'marker': '^', 'linestyle': '--', 'label': 'CF (Process)'},
        "CF (Thread)":     {'marker': 's', 'linestyle': '-', 'label': 'CF (Thread)'}
    }

    generated_count = 0
    for w in sorted(plot_data.keys()):
        plt.figure(figsize=(10, 6))
        
        methods = plot_data[w]
        
        for method_name, points in methods.items():
            # Sort by image count (x-axis)
            points.sort(key=lambda x: x[0])
            
            if not points: 
                continue
                
            x_vals, y_vals = zip(*points)
            
            # Get style or default
            style = styles.get(method_name, {'marker': 'x', 'linestyle': '-', 'label': method_name})
            
            plt.plot(x_vals, y_vals, 
                     marker=style['marker'], 
                     linestyle=style['linestyle'], 
                     label=style['label'], 
                     linewidth=2)
        
        plt.title(f'Scalability Analysis: {w} Workers')
        plt.xlabel('Number of Images')
        plt.ylabel('Execution Time (seconds)')
        plt.legend()
        plt.grid(True)
        
        # Determine X-ticks based on data present
        # Use all unique image counts found for this worker
        all_x = set()
        for pts in methods.values():
            for x, _ in pts:
                all_x.add(x)
        if all_x:
            plt.xticks(sorted(list(all_x)))
        
        filename = os.path.join(output_dir, f"benchmark_plot_{w}worker.png")
        plt.savefig(filename)
        print(f"  > Saved {filename}")
        plt.close()
        generated_count += 1
        
    if generated_count == 0:
        print("No plots generated. Is the CSV empty?")

if __name__ == "__main__":
    generate_plots()
