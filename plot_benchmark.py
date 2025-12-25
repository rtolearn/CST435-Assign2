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
        print(f"Loaded {count} data points.\n")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Output directory
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Map CSV method names to Plot labels/Styles
    styles = {
        "Multiprocessing": {'marker': 'o', 'linestyle': '-', 'label': 'Multiprocessing', 'color': 'blue'},
        "CF (Process)":    {'marker': '^', 'linestyle': '--', 'label': 'CF (Process)', 'color': 'orange'},
        "CF (Thread)":     {'marker': 's', 'linestyle': '-', 'label': 'CF (Thread)', 'color': 'green'}
    }

    # ========== PERFORMANCE ANALYSIS ==========
    print("="*80)
    print("PERFORMANCE ANALYSIS: SPEEDUP & EFFICIENCY")
    print("="*80)
    
    # For each image count, calculate speedup and efficiency
    all_image_counts = set()
    for methods in plot_data.values():
        for points in methods.values():
            for img, _ in points:
                all_image_counts.add(img)
    
    for img_count in sorted(all_image_counts):
        print(f"\n[ Dataset Size: {img_count} Images ]")
        print(f"{'Method':<20} | {'Workers':<8} | {'Time (s)':<10} | {'Speedup':<8} | {'Efficiency':<10} | {'Throughput (img/s)':<18}")
        print("-" * 110)
        
        # Collect data for this image count across all workers
        data_by_method = defaultdict(dict)  # method -> {workers: time}
        
        for w in sorted(plot_data.keys()):
            methods = plot_data[w]
            for method_name, points in methods.items():
                # Find the time for this specific image count
                for img, time_val in points:
                    if img == img_count:
                        data_by_method[method_name][w] = time_val
        
        # Calculate and print metrics for each method
        for method_name in ["Multiprocessing", "CF (Process)", "CF (Thread)"]:
            if method_name not in data_by_method:
                continue
                
            worker_times = data_by_method[method_name]
            
            # Get baseline (1 worker) time
            t_1 = worker_times.get(1, None)
            
            for w in sorted(worker_times.keys()):
                t_w = worker_times[w]
                
                # Calculate metrics
                speedup = t_1 / t_w if t_1 else 1.0
                efficiency = (speedup / w) * 100 if w > 0 else 0.0
                throughput = img_count / t_w if t_w > 0 else 0.0
                
                print(f"{method_name:<20} | {w:<8} | {t_w:<10.4f} | {speedup:<8.2f} | {efficiency:<9.1f}% | {throughput:<18.1f}")
    
    print("\n" + "="*80 + "\n")
    
    # ========== GENERATE TIME PLOTS (Original) ==========
    print("Generating Time vs Workers plots...")
    
    for w in sorted(plot_data.keys()):
        plt.figure(figsize=(10, 6))
        
        methods = plot_data[w]
        
        for method_name, points in methods.items():
            points.sort(key=lambda x: x[0])
            
            if not points: 
                continue
                
            x_vals, y_vals = zip(*points)
            style = styles.get(method_name, {'marker': 'x', 'linestyle': '-', 'label': method_name, 'color': 'gray'})
            
            plt.plot(x_vals, y_vals, 
                     marker=style['marker'], 
                     linestyle=style['linestyle'], 
                     label=style['label'],
                     color=style['color'],
                     linewidth=2)
        
        plt.title(f'Execution Time: {w} Workers', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Images', fontsize=12)
        plt.ylabel('Execution Time (seconds)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # X-ticks
        all_x = set()
        for pts in methods.values():
            for x, _ in pts:
                all_x.add(x)
        if all_x:
            plt.xticks(sorted(list(all_x)))
        
        filename = os.path.join(output_dir, f"time_{w}worker.png")
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"  > Saved {filename}")
        plt.close()
    
    print(f"\n✓ All plots saved to '{output_dir}/' directory")

if __name__ == "__main__":
    generate_plots()
