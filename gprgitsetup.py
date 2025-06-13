import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Try to import gprpy with proper error handling
try:
    import gprpy.gprpy as gpr
    GPRPY_AVAILABLE = True
    print("GPRPy successfully imported")
except ImportError:
    print("GPRPy not available - using synthetic data generation")
    GPRPY_AVAILABLE = False

class GPRLocationController:
    """
    GPR Location-based Analysis Controller for Mineral Targeting
    Integrates with GPRPy for coordinate-controlled GPR processing
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPRPy Location Controller - IndiaAI Mineral Targeting")
        self.root.geometry("800x600")
        
        # Data storage
        self.current_project = None
        self.location_history = []
        self.analysis_results = {}
        
        # Initialize GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the graphical user interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="GPRPy Location Controller", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Location input section
        location_frame = ttk.LabelFrame(main_frame, text="Location Input", padding="10")
        location_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Latitude input
        ttk.Label(location_frame, text="Latitude:").grid(row=0, column=0, sticky=tk.W)
        self.lat_var = tk.StringVar(value="15.3173")
        self.lat_entry = ttk.Entry(location_frame, textvariable=self.lat_var, width=15)
        self.lat_entry.grid(row=0, column=1, padx=(5, 10))
        
        # Longitude input
        ttk.Label(location_frame, text="Longitude:").grid(row=0, column=2, sticky=tk.W)
        self.lon_var = tk.StringVar(value="75.7139")
        self.lon_entry = ttk.Entry(location_frame, textvariable=self.lon_var, width=15)
        self.lon_entry.grid(row=0, column=3, padx=(5, 10))
        
        # Location name
        ttk.Label(location_frame, text="Location Name:").grid(row=1, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(value="Karnataka Site")
        self.name_entry = ttk.Entry(location_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=1, column=1, columnspan=2, padx=(5, 10), pady=(5, 0))
        
        # Quick location buttons
        quick_frame = ttk.Frame(location_frame)
        quick_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        locations = [
            ("Karnataka-Bellary", 15.1394, 76.9214),
            ("Karnataka-Chitradurga", 14.2251, 76.3980),
            ("AP-Anantapur", 14.6819, 77.6006),
            ("AP-Kurnool", 15.8281, 78.0373)
        ]
        
        for i, (name, lat, lon) in enumerate(locations):
            btn = ttk.Button(quick_frame, text=name, 
                           command=lambda n=name, la=lat, lo=lon: self.set_quick_location(n, la, lo))
            btn.grid(row=0, column=i, padx=2)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.process_btn = ttk.Button(control_frame, text="Process Location", 
                                    command=self.process_location, style="Accent.TButton")
        self.process_btn.grid(row=0, column=0, padx=5)
        
        self.load_data_btn = ttk.Button(control_frame, text="Load GPR Data", 
                                      command=self.load_gpr_data)
        self.load_data_btn.grid(row=0, column=1, padx=5)
        
        self.analyze_btn = ttk.Button(control_frame, text="Run Analysis", 
                                    command=self.run_analysis)
        self.analyze_btn.grid(row=0, column=2, padx=5)
        
        self.export_btn = ttk.Button(control_frame, text="Export Results", 
                                   command=self.export_results)
        self.export_btn.grid(row=0, column=3, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Results text area with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = tk.Text(text_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
    def set_quick_location(self, name, lat, lon):
        """Set quick location coordinates"""
        self.lat_var.set(str(lat))
        self.lon_var.set(str(lon))
        self.name_var.set(name)
        self.update_status(f"Location set to {name}")
        
    def update_status(self, message):
        """Update status message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def log_result(self, message):
        """Add message to results display"""
        self.results_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
        
    def process_location(self):
        """Process GPR data for the specified location"""
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
            name = self.name_var.get()
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                messagebox.showerror("Error", "Invalid coordinates")
                return
                
            self.progress.start()
            self.update_status("Processing location...")
            
            # Run processing in separate thread
            thread = threading.Thread(target=self._process_location_thread, 
                                     args=(lat, lon, name))
            thread.daemon = True
            thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid coordinates")
            
    def _process_location_thread(self, lat, lon, name):
        """Process location in separate thread"""
        try:
            self.log_result(f"Starting analysis for {name}")
            self.log_result(f"Coordinates: {lat:.6f}°N, {lon:.6f}°E")
            
            # Create GPR project
            project = self.create_gpr_project(lat, lon, name)
            
            # Generate or load data
            if GPRPY_AVAILABLE:
                self.log_result("GPRPy available - initializing project")
                project = self.initialize_gprpy_project(project, lat, lon)
            else:
                self.log_result("Using synthetic data generation")
                project = self.generate_location_data(project, lat, lon)
            
            # Store project
            self.current_project = project
            self.location_history.append({
                'name': name,
                'lat': lat,
                'lon': lon,
                'timestamp': datetime.now().isoformat()
            })
            
            self.log_result("Location processing completed successfully")
            
            # Update UI on main thread
            self.root.after(0, self._processing_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._processing_error(str(e)))
            
    def _processing_complete(self):
        """Handle processing completion"""
        self.progress.stop()
        self.update_status("Processing completed")
        self.analyze_btn.config(state="normal")
        
    def _processing_error(self, error_msg):
        """Handle processing error"""
        self.progress.stop()
        self.update_status("Processing failed")
        self.log_result(f"Error: {error_msg}")
        messagebox.showerror("Processing Error", error_msg)
        
    def create_gpr_project(self, lat, lon, name):
        """Create a new GPR project structure"""
        return {
            'name': name,
            'location': {
                'latitude': lat,
                'longitude': lon,
                'coordinate_system': 'WGS84'
            },
            'timestamp': datetime.now().isoformat(),
            'data': None,
            'processed_data': None,
            'gpr_object': None,
            'processing_log': [],
            'analysis_results': {}
        }
        
    def initialize_gprpy_project(self, project, lat, lon):
        """Initialize actual GPRPy project"""
        try:
            # Create GPRPy object
            gpr_obj = gpr.gprpy()
            
            # Set location metadata
            gpr_obj.latitude = lat
            gpr_obj.longitude = lon
            
            # Generate synthetic data if no real data available
            project['data'] = self.generate_synthetic_gpr_data(lat, lon)
            gpr_obj.data = project['data']
            
            # Set basic parameters
            gpr_obj.dt = 0.1  # Time sampling
            gpr_obj.dx = 0.25  # Spatial sampling
            gpr_obj.velocity = 0.1  # Default velocity
            
            project['gpr_object'] = gpr_obj
            project['processing_log'].append("GPRPy object initialized")
            
            return project
            
        except Exception as e:
            self.log_result(f"GPRPy initialization failed: {e}")
            return self.generate_location_data(project, lat, lon)
            
    def generate_location_data(self, project, lat, lon):
        """Generate synthetic GPR data for location"""
        self.log_result("Generating synthetic GPR data...")
        
        # Create realistic synthetic data
        traces = 200
        samples = 512
        
        # Location-specific parameters
        lat_factor = (lat - 15.0) * 2  # Normalize around study area
        lon_factor = (lon - 76.0) * 1.5
        
        # Generate data
        data = np.zeros((samples, traces))
        depth_range = np.linspace(0, 10, samples)
        distance_range = np.linspace(0, 50, traces)
        
        for i, distance in enumerate(distance_range):
            for j, depth in enumerate(depth_range):
                # Background geology
                data[j, i] += 0.3 * np.exp(-depth/4) * (1 + 0.1*np.sin(distance/10))
                
                # Location-specific mineral signatures
                mineral_depth = 3 + lat_factor * 0.5
                if abs(depth - mineral_depth) < 0.5:
                    mineral_strength = 0.6 * np.exp(-((distance-25)**2)/100)
                    data[j, i] += mineral_strength
                
                # Deep structures influenced by longitude
                if depth > 6 + lon_factor * 0.3:
                    data[j, i] += 0.4 * np.exp(-(depth-7)**2/1.0)
        
        # Add realistic noise
        data += 0.1 * np.random.randn(samples, traces)
        
        project['data'] = data
        project['depth_range'] = depth_range
        project['distance_range'] = distance_range
        project['processing_log'].append("Synthetic data generated with location-specific characteristics")
        
        return project
        
    def generate_synthetic_gpr_data(self, lat, lon):
        """Generate synthetic GPR data matrix"""
        traces = 200
        samples = 512
        data = np.zeros((samples, traces))
        
        # Simple synthetic data generation
        for i in range(traces):
            for j in range(samples):
                depth = j * 0.02  # Convert to approximate depth
                distance = i * 0.25
                
                # Add some realistic GPR signatures
                data[j, i] = 0.5 * np.exp(-depth/3) * np.sin(distance/5 + depth*2)
                
                # Add mineral-like reflections
                if 2 < depth < 3:
                    data[j, i] += 0.3 * np.exp(-((distance-25)**2)/50)
        
        # Add noise
        data += 0.1 * np.random.randn(samples, traces)
        
        return data
        
    def load_gpr_data(self):
        """Load GPR data from file"""
        file_path = filedialog.askopenfilename(
            title="Select GPR Data File",
            filetypes=[
                ("GPR files", "*.gpr"),
                ("NumPy files", "*.npy"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.update_status("Loading GPR data...")
                
                if file_path.endswith('.npy'):
                    data = np.load(file_path)
                elif file_path.endswith('.txt'):
                    data = np.loadtxt(file_path)
                elif file_path.endswith('.gpr') and GPRPY_AVAILABLE:
                    # Load GPRPy format
                    gpr_obj = gpr.gprpy()
                    gpr_obj.importdata(file_path)
                    data = gpr_obj.data
                else:
                    messagebox.showerror("Error", "Unsupported file format")
                    return
                
                if self.current_project:
                    self.current_project['data'] = data
                    self.current_project['processing_log'].append(f"Data loaded from {file_path}")
                    self.log_result(f"Data loaded: {data.shape[0]} samples × {data.shape[1]} traces")
                else:
                    messagebox.showwarning("Warning", "Please process a location first")
                    
                self.update_status("Data loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")
                
    def run_analysis(self):
        """Run comprehensive GPR analysis"""
        if not self.current_project or self.current_project['data'] is None:
            messagebox.showwarning("Warning", "No data available for analysis")
            return
            
        self.progress.start()
        self.update_status("Running analysis...")
        
        thread = threading.Thread(target=self._run_analysis_thread)
        thread.daemon = True
        thread.start()
        
    def _run_analysis_thread(self):
        """Run analysis in separate thread"""
        try:
            project = self.current_project
            data = project['data']
            
            self.log_result("Starting comprehensive GPR analysis...")
            
            # Apply GPRPy-style processing
            processed_data = self.apply_gpr_processing(data)
            project['processed_data'] = processed_data
            
            # Mineral targeting analysis
            results = self.analyze_mineral_targets(processed_data, project)
            project['analysis_results'] = results
            
            # Generate visualizations
            self.create_analysis_plots(project)
            
            # Export results
            self.export_analysis_results(project)
            
            self.root.after(0, self._analysis_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._analysis_error(str(e)))
            
    def apply_gpr_processing(self, data):
        """Apply GPRPy-style processing workflow"""
        processed = data.copy()
        
        self.log_result("Applying processing workflow:")
        
        # 1. Dewow (remove low-frequency trends)
        self.log_result("  - Dewow filter")
        for i in range(processed.shape[1]):
            trace = processed[:, i]
            detrended = trace - np.linspace(trace[0], trace[-1], len(trace))
            processed[:, i] = detrended
            
        # 2. AGC Gain
        self.log_result("  - AGC gain")
        window = 20
        for i in range(processed.shape[1]):
            trace = processed[:, i]
            gained = self.apply_agc_gain(trace, window)
            processed[:, i] = gained
            
        # 3. Background removal
        self.log_result("  - Background removal")
        background = np.mean(processed, axis=1, keepdims=True)
        processed = processed - background
        
        # 4. Amplitude enhancement
        self.log_result("  - Amplitude enhancement")
        processed = np.tanh(processed * 1.5)
        
        return processed
        
    def apply_agc_gain(self, trace, window):
        """Apply AGC gain to trace"""
        gained = np.zeros_like(trace)
        half_window = window // 2
        
        for i in range(len(trace)):
            start = max(0, i - half_window)
            end = min(len(trace), i + half_window + 1)
            
            window_data = trace[start:end]
            rms = np.sqrt(np.mean(window_data**2))
            
            if rms > 0:
                gained[i] = trace[i] / rms
            else:
                gained[i] = trace[i]
                
        return gained
        
    def analyze_mineral_targets(self, data, project):
        """Analyze for mineral targeting"""
        self.log_result("Analyzing mineral targets...")
        
        results = {}
        
        # Amplitude analysis
        amplitude_profile = np.mean(np.abs(data), axis=0)
        results['amplitude_profile'] = amplitude_profile
        
        # Find potential mineral zones
        mean_amp = np.mean(amplitude_profile)
        threshold = mean_amp * 1.3
        
        peaks = []
        for i in range(1, len(amplitude_profile) - 1):
            if (amplitude_profile[i] > threshold and 
                amplitude_profile[i] > amplitude_profile[i-1] and 
                amplitude_profile[i] > amplitude_profile[i+1]):
                peaks.append(i)
        
        results['mineral_zones'] = peaks
        results['num_zones'] = len(peaks)
        
        # Calculate mineral probability map
        probability = self.calculate_mineral_probability(data)
        results['probability_map'] = probability
        
        # Statistics
        results['max_amplitude'] = np.max(np.abs(data))
        results['mean_amplitude'] = np.mean(np.abs(data))
        results['data_quality'] = self.assess_data_quality(data)
        
        # Location-specific interpretation
        lat = project['location']['latitude']
        lon = project['location']['longitude']
        results['geological_context'] = self.get_geological_context(lat, lon)
        
        self.log_result(f"Analysis complete: {len(peaks)} potential mineral zones detected")
        
        return results
        
    def calculate_mineral_probability(self, data):
        """Calculate mineral probability map"""
        # Normalize data
        normalized = np.abs(data) / np.max(np.abs(data))
        
        # Simple probability calculation based on amplitude patterns
        probability = normalized * 0.7
        
        # Add gradient information
        grad_y = np.gradient(normalized, axis=0)
        grad_x = np.gradient(normalized, axis=1)
        gradient_mag = np.sqrt(grad_y**2 + grad_x**2)
        
        probability += gradient_mag * 0.3
        
        # Normalize to 0-1
        probability = (probability - np.min(probability)) / (np.max(probability) - np.min(probability))
        
        return probability
        
    def assess_data_quality(self, data):
        """Assess GPR data quality"""
        signal_power = np.var(data)
        noise_estimate = np.var(np.diff(data, axis=0))
        
        if noise_estimate > 0:
            snr = 10 * np.log10(signal_power / noise_estimate)
            if snr > 20:
                return "Excellent"
            elif snr > 15:
                return "Good"
            elif snr > 10:
                return "Fair"
            else:
                return "Poor"
        return "Unknown"
        
    def get_geological_context(self, lat, lon):
        """Get geological context for location"""
        # Simple geological context based on coordinates
        if 14.0 <= lat <= 16.0 and 75.0 <= lon <= 78.0:
            return "Dharwar Craton - High potential for gold, iron ore, and base metals"
        else:
            return "Regional geological context - Moderate mineral potential"
            
    def create_analysis_plots(self, project):
        """Create comprehensive analysis plots"""
        try:
            data = project['processed_data']
            results = project['analysis_results']
            lat = project['location']['latitude']
            lon = project['location']['longitude']
            
            # Create figure
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'GPR Analysis - {project["name"]}\n{lat:.6f}°N, {lon:.6f}°E', 
                        fontsize=14, fontweight='bold')
            
            # 1. Processed GPR data
            im1 = axes[0,0].imshow(data, aspect='auto', cmap='seismic',
                                  extent=[0, 50, 10, 0])
            axes[0,0].set_title('Processed GPR Data')
            axes[0,0].set_xlabel('Distance (m)')
            axes[0,0].set_ylabel('Depth (m)')
            plt.colorbar(im1, ax=axes[0,0])
            
            # 2. Amplitude profile
            amplitude_profile = results['amplitude_profile']
            distance = np.linspace(0, 50, len(amplitude_profile))
            axes[0,1].plot(distance, amplitude_profile, 'b-', linewidth=2)
            axes[0,1].set_title('Amplitude Profile')
            axes[0,1].set_xlabel('Distance (m)')
            axes[0,1].set_ylabel('Mean Amplitude')
            axes[0,1].grid(True)
            
            # Mark mineral zones
            if results['mineral_zones']:
                zone_distances = distance[results['mineral_zones']]
                zone_amplitudes = amplitude_profile[results['mineral_zones']]
                axes[0,1].scatter(zone_distances, zone_amplitudes, 
                                color='red', s=50, marker='v', label='Mineral Zones')
                axes[0,1].legend()
            
            # 3. Mineral probability map
            im3 = axes[1,0].imshow(results['probability_map'], aspect='auto', cmap='hot',
                                  extent=[0, 50, 10, 0])
            axes[1,0].set_title('Mineral Probability Map')
            axes[1,0].set_xlabel('Distance (m)')
            axes[1,0].set_ylabel('Depth (m)')
            plt.colorbar(im3, ax=axes[1,0])
            
            # 4. Analysis summary
            axes[1,1].axis('off')
            summary_text = f"""Analysis Summary:
            
Location: {project['name']}
Coordinates: {lat:.6f}°N, {lon:.6f}°E
            
Data Quality: {results['data_quality']}
Max Amplitude: {results['max_amplitude']:.3f}
Mean Amplitude: {results['mean_amplitude']:.3f}

Mineral Zones Detected: {results['num_zones']}

Geological Context:
{results['geological_context']}

Processing Applied:
• Dewow filter
• AGC gain
• Background removal
• Amplitude enhancement
            """
            
            axes[1,1].text(0.05, 0.95, summary_text, transform=axes[1,1].transAxes,
                          fontsize=10, verticalalignment='top', fontfamily='monospace')
            
            plt.tight_layout()
            
            # Save plot
            filename = f"gpr_analysis_{lat}_{lon}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
            self.log_result(f"Analysis plot saved: {filename}")
            
            plt.show()
            
        except Exception as e:
            self.log_result(f"Error creating plots: {e}")
            
    def export_analysis_results(self, project):
        """Export analysis results"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            lat = project['location']['latitude']
            lon = project['location']['longitude']
            
            # Create export directory
            export_dir = f"gpr_export_{lat}_{lon}_{timestamp}"
            os.makedirs(export_dir, exist_ok=True)
            
            # Export processed data
            if project['processed_data'] is not None:
                np.save(os.path.join(export_dir, 'processed_data.npy'), 
                       project['processed_data'])
            
            # Export analysis results
            results_file = os.path.join(export_dir, 'analysis_results.json')
            exportable_results = {}
            for key, value in project['analysis_results'].items():
                if isinstance(value, np.ndarray):
                    exportable_results[key] = value.tolist()
                else:
                    exportable_results[key] = value
            
            with open(results_file, 'w') as f:
                json.dump({
                    'project_info': project['location'],
                    'timestamp': project['timestamp'],
                    'processing_log': project['processing_log'],
                    'analysis_results': exportable_results
                }, f, indent=2)
            
            self.log_result(f"Results exported to: {export_dir}")
            
        except Exception as e:
            self.log_result(f"Export error: {e}")
            
    def _analysis_complete(self):
        """Handle analysis completion"""
        self.progress.stop()
        self.update_status("Analysis completed")
        self.log_result("Analysis workflow completed successfully")
        
    def _analysis_error(self, error_msg):
        """Handle analysis error"""
        self.progress.stop()
        self.update_status("Analysis failed")
        self.log_result(f"Analysis error: {error_msg}")
        
    def export_results(self):
        """Export current results"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project to export")
            return
            
        self.export_analysis_results(self.current_project)
        messagebox.showinfo("Export", "Results exported successfully")
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("GPRPy Location Controller - IndiaAI Mineral Targeting")
    print("Coordinate-controlled GPR processing and analysis")
    print("=" * 70)
    
    app = GPRLocationController()
    app.run()
# End of gprgitsetup.py
# Ensure the script runs only if executed directly