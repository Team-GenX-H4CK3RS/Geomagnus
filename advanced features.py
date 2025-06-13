import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import pandas as pd
from scipy.interpolate import griddata, Rbf
from scipy.spatial.distance import cdist
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from folium import plugins
import webbrowser
import tempfile

# Try to import gprpy with proper error handling
try:
    import gprpy.gprpy as gpr
    GPRPY_AVAILABLE = True
    print("GPRPy successfully imported")
except ImportError:
    print("GPRPy not available - using synthetic data generation")
    GPRPY_AVAILABLE = False

class Enhanced3DGPRMineralController:
    """
    Enhanced 3D GPR Location-based Analysis Controller for Mineral Targeting
    with Interactive Mapping, 3D Interpolation, and Comprehensive Mineral Analysis
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced 3D GPR Mineral Targeting - IndiaAI Hackathon")
        self.root.geometry("1200x800")
        
        # Data storage
        self.current_project = None
        self.location_history = []
        self.analysis_results = {}
        self.mineral_database = self.initialize_mineral_database()
        self.geochemical_data = self.load_geochemical_data()
        
        # Initialize GUI
        self.setup_enhanced_gui()
        
    def initialize_mineral_database(self):
        """Initialize comprehensive mineral database for Karnataka and Andhra Pradesh"""
        return {
            'Karnataka': {
                'Iron Ore': {'lat': 15.1394, 'lon': 76.9214, 'grade': 65.2, 'reserves': 'High'},
                'Gold': {'lat': 14.0833, 'lon': 76.6500, 'grade': 4.8, 'reserves': 'Medium'},
                'Copper': {'lat': 14.2251, 'lon': 76.3980, 'grade': 1.2, 'reserves': 'Medium'},
                'Chromite': {'lat': 14.5000, 'lon': 75.8000, 'grade': 45.0, 'reserves': 'High'},
                'Manganese': {'lat': 15.2500, 'lon': 75.5000, 'grade': 38.5, 'reserves': 'Medium'},
                'REE (Monazite)': {'lat': 14.8000, 'lon': 74.5000, 'grade': 0.8, 'reserves': 'Low'},
                'Nickel': {'lat': 14.1000, 'lon': 76.1000, 'grade': 0.6, 'reserves': 'Low'},
                'Titanium': {'lat': 14.3000, 'lon': 74.8000, 'grade': 12.5, 'reserves': 'Medium'}
            },
            'Andhra Pradesh': {
                'Iron Ore': {'lat': 14.6819, 'lon': 77.6006, 'grade': 62.8, 'reserves': 'High'},
                'Copper': {'lat': 14.9167, 'lon': 79.7333, 'grade': 1.8, 'reserves': 'High'},
                'Gold': {'lat': 15.8281, 'lon': 78.0373, 'grade': 3.2, 'reserves': 'Medium'},
                'Barite': {'lat': 14.4673, 'lon': 78.8242, 'grade': 85.0, 'reserves': 'High'},
                'Limestone': {'lat': 15.9129, 'lon': 79.7400, 'grade': 95.2, 'reserves': 'Very High'},
                'REE (Rare Earth)': {'lat': 15.5000, 'lon': 78.5000, 'grade': 1.2, 'reserves': 'Medium'},
                'Mica': {'lat': 14.2000, 'lon': 79.1000, 'grade': 78.5, 'reserves': 'High'},
                'Graphite': {'lat': 15.1000, 'lon': 78.8000, 'grade': 92.0, 'reserves': 'High'}
            }
        }
        
    def load_geochemical_data(self):
        """Load and simulate geochemical data based on the images shown"""
        # Simulate geochemical data points based on the mineral composition shown
        np.random.seed(42)  # For reproducible results
        
        # Generate sample points across Karnataka and Andhra Pradesh
        n_samples = 150
        lat_range = (13.5, 16.5)
        lon_range = (74.0, 80.0)
        
        data = {
            'lat': np.random.uniform(lat_range[0], lat_range[1], n_samples),
            'lon': np.random.uniform(lon_range[0], lon_range[1], n_samples),
            'SiO2_%': np.random.normal(62.5, 8.2, n_samples),
            'Al2O3_%': np.random.normal(15.8, 3.1, n_samples),
            'Fe2O3_%': np.random.normal(6.2, 2.8, n_samples),
            'TiO2_%': np.random.normal(0.8, 0.3, n_samples),
            'CaO_%': np.random.normal(4.1, 1.5, n_samples),
            'MgO_%': np.random.normal(3.2, 1.2, n_samples),
            'MnO_%': np.random.normal(0.12, 0.05, n_samples),
            'Na2O_%': np.random.normal(3.8, 0.8, n_samples),
            'K2O_%': np.random.normal(2.9, 0.9, n_samples),
            'P2O5_%': np.random.normal(0.18, 0.08, n_samples),
            'LOI_%': np.random.normal(1.2, 0.5, n_samples),
            'Au_ppb': np.random.lognormal(1.5, 1.8, n_samples),
            'Cu_ppm': np.random.lognormal(3.2, 1.2, n_samples),
            'Ni_ppm': np.random.lognormal(2.8, 0.9, n_samples),
            'Cr_ppm': np.random.lognormal(4.1, 1.1, n_samples),
            'Zn_ppm': np.random.lognormal(3.5, 0.8, n_samples),
            'Pb_ppm': np.random.lognormal(2.1, 0.7, n_samples),
            'REE_ppm': np.random.lognormal(4.5, 1.3, n_samples)
        }
        
        return pd.DataFrame(data)
        
    def setup_enhanced_gui(self):
        """Setup enhanced GUI with 3D capabilities"""
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Location Control and GPR Processing
        gpr_frame = ttk.Frame(notebook)
        notebook.add(gpr_frame, text="GPR Processing")
        self.setup_gpr_tab(gpr_frame)
        
        # Tab 2: 3D Visualization and Mapping
        viz_frame = ttk.Frame(notebook)
        notebook.add(viz_frame, text="3D Visualization")
        self.setup_visualization_tab(viz_frame)
        
        # Tab 3: Mineral Analysis
        mineral_frame = ttk.Frame(notebook)
        notebook.add(mineral_frame, text="Mineral Analysis")
        self.setup_mineral_tab(mineral_frame)
        
    def setup_gpr_tab(self, parent):
        """Setup GPR processing tab"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="GPR Location Controller with 3D Analysis", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Location input section
        location_frame = ttk.LabelFrame(main_frame, text="Location Input", padding="10")
        location_frame.pack(fill='x', pady=(0, 10))
        
        # Coordinate inputs
        coord_frame = ttk.Frame(location_frame)
        coord_frame.pack(fill='x')
        
        ttk.Label(coord_frame, text="Latitude:").grid(row=0, column=0, sticky=tk.W)
        self.lat_var = tk.StringVar(value="15.3173")
        self.lat_entry = ttk.Entry(coord_frame, textvariable=self.lat_var, width=15)
        self.lat_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(coord_frame, text="Longitude:").grid(row=0, column=2, sticky=tk.W)
        self.lon_var = tk.StringVar(value="75.7139")
        self.lon_entry = ttk.Entry(coord_frame, textvariable=self.lon_var, width=15)
        self.lon_entry.grid(row=0, column=3, padx=(5, 10))
        
        ttk.Label(coord_frame, text="Location Name:").grid(row=1, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(value="Karnataka Site")
        self.name_entry = ttk.Entry(coord_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=1, column=1, columnspan=2, padx=(5, 10), pady=(5, 0))
        
        # Quick location buttons
        quick_frame = ttk.Frame(location_frame)
        quick_frame.pack(pady=(10, 0))
        
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
        control_frame.pack(pady=10)
        
        self.process_btn = ttk.Button(control_frame, text="Process Location", 
                                    command=self.process_location)
        self.process_btn.grid(row=0, column=0, padx=5)
        
        self.analyze_btn = ttk.Button(control_frame, text="3D Analysis", 
                                    command=self.run_3d_analysis)
        self.analyze_btn.grid(row=0, column=1, padx=5)
        
        self.map_btn = ttk.Button(control_frame, text="Create Interactive Map", 
                                command=self.create_interactive_map)
        self.map_btn.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # Results display
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.results_text = tk.Text(text_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def setup_visualization_tab(self, parent):
        """Setup 3D visualization tab"""
        viz_frame = ttk.Frame(parent, padding="10")
        viz_frame.pack(fill='both', expand=True)
        
        ttk.Label(viz_frame, text="3D Visualization Controls", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Visualization options
        options_frame = ttk.LabelFrame(viz_frame, text="Visualization Options", padding="10")
        options_frame.pack(fill='x', pady=(0, 10))
        
        # 3D visualization buttons
        viz_buttons_frame = ttk.Frame(options_frame)
        viz_buttons_frame.pack(fill='x')
        
        ttk.Button(viz_buttons_frame, text="3D Surface Plot", 
                  command=self.create_3d_surface).grid(row=0, column=0, padx=5)
        ttk.Button(viz_buttons_frame, text="3D Scatter Plot", 
                  command=self.create_3d_scatter).grid(row=0, column=1, padx=5)
        ttk.Button(viz_buttons_frame, text="3D Interpolation", 
                  command=self.create_3d_interpolation).grid(row=0, column=2, padx=5)
        ttk.Button(viz_buttons_frame, text="Mineral Distribution", 
                  command=self.create_mineral_distribution).grid(row=0, column=3, padx=5)
        
        # Parameter controls
        param_frame = ttk.LabelFrame(viz_frame, text="Interpolation Parameters", padding="10")
        param_frame.pack(fill='x', pady=10)
        
        ttk.Label(param_frame, text="Grid Resolution:").grid(row=0, column=0, sticky=tk.W)
        self.grid_res_var = tk.StringVar(value="50")
        ttk.Entry(param_frame, textvariable=self.grid_res_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(param_frame, text="Interpolation Method:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.interp_method_var = tk.StringVar(value="cubic")
        method_combo = ttk.Combobox(param_frame, textvariable=self.interp_method_var, 
                                   values=["linear", "cubic", "rbf"], width=10)
        method_combo.grid(row=0, column=3, padx=5)
        
    def setup_mineral_tab(self, parent):
        """Setup mineral analysis tab"""
        mineral_frame = ttk.Frame(parent, padding="10")
        mineral_frame.pack(fill='both', expand=True)
        
        ttk.Label(mineral_frame, text="Mineral Targeting Analysis", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Mineral selection
        selection_frame = ttk.LabelFrame(mineral_frame, text="Target Minerals", padding="10")
        selection_frame.pack(fill='x', pady=(0, 10))
        
        # Checkboxes for minerals
        self.mineral_vars = {}
        minerals = ['Gold', 'Copper', 'Iron Ore', 'REE', 'Nickel', 'Chromite', 'Titanium', 'Barite']
        
        for i, mineral in enumerate(minerals):
            var = tk.BooleanVar(value=True)
            self.mineral_vars[mineral] = var
            ttk.Checkbutton(selection_frame, text=mineral, variable=var).grid(
                row=i//4, column=i%4, sticky=tk.W, padx=10, pady=2)
        
        # Analysis buttons
        analysis_frame = ttk.Frame(mineral_frame)
        analysis_frame.pack(pady=10)
        
        ttk.Button(analysis_frame, text="Analyze Mineral Potential", 
                  command=self.analyze_mineral_potential).grid(row=0, column=0, padx=5)
        ttk.Button(analysis_frame, text="Generate Mineral Map", 
                  command=self.generate_mineral_map).grid(row=0, column=1, padx=5)
        ttk.Button(analysis_frame, text="Export Analysis", 
                  command=self.export_mineral_analysis).grid(row=0, column=2, padx=5)
        
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
            self.log_result(f"Starting enhanced analysis for {name}")
            self.log_result(f"Coordinates: {lat:.6f}°N, {lon:.6f}°E")
            
            # Create enhanced project
            project = self.create_enhanced_project(lat, lon, name)
            
            # Generate comprehensive data
            project = self.generate_comprehensive_data(project, lat, lon)
            
            # Store project
            self.current_project = project
            self.location_history.append({
                'name': name,
                'lat': lat,
                'lon': lon,
                'timestamp': datetime.now().isoformat()
            })
            
            self.log_result("Enhanced location processing completed successfully")
            
            # Update UI on main thread
            self.root.after(0, self._processing_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._processing_error(str(e)))
            
    def create_enhanced_project(self, lat, lon, name):
        """Create enhanced project structure"""
        return {
            'name': name,
            'location': {
                'latitude': lat,
                'longitude': lon,
                'coordinate_system': 'WGS84'
            },
            'timestamp': datetime.now().isoformat(),
            'gpr_data': None,
            'geochemical_data': None,
            'mineral_potential': {},
            'interpolated_surfaces': {},
            'analysis_results': {},
            'processing_log': []
        }
        
    def generate_comprehensive_data(self, project, lat, lon):
        """Generate comprehensive geophysical and geochemical data"""
        self.log_result("Generating comprehensive dataset...")
        
        # Generate GPR data
        project['gpr_data'] = self.generate_enhanced_gpr_data(lat, lon)
        
        # Extract local geochemical data
        project['geochemical_data'] = self.extract_local_geochemical_data(lat, lon)
        
        # Calculate mineral potential
        project['mineral_potential'] = self.calculate_mineral_potential(lat, lon)
        
        project['processing_log'].append("Comprehensive data generated")
        return project
        
    def generate_enhanced_gpr_data(self, lat, lon):
        """Generate enhanced GPR data with mineral signatures"""
        traces = 200
        samples = 512
        depth_range = np.linspace(0, 15, samples)  # Deeper penetration
        distance_range = np.linspace(0, 100, traces)  # Longer profile
        
        data = np.zeros((samples, traces))
        
        # Location-specific geological modeling
        lat_factor = (lat - 15.0) * 2
        lon_factor = (lon - 76.0) * 1.5
        
        for i, distance in enumerate(distance_range):
            for j, depth in enumerate(depth_range):
                # Complex geological layering
                data[j, i] += 0.4 * np.exp(-depth/5) * (1 + 0.15*np.sin(distance/12))
                
                # Mineral-specific signatures based on location
                if self.is_in_mineral_zone(lat, lon, 'Gold'):
                    if 3 < depth < 8:
                        data[j, i] += 0.8 * np.exp(-((distance-40)**2)/200) * np.exp(-((depth-5.5)**2)/4)
                
                if self.is_in_mineral_zone(lat, lon, 'Copper'):
                    if 2 < depth < 6:
                        data[j, i] += 0.6 * np.exp(-((distance-60)**2)/150) * np.exp(-((depth-4)**2)/2)
                
                if self.is_in_mineral_zone(lat, lon, 'Iron Ore'):
                    if 1 < depth < 12:
                        data[j, i] += 0.7 * np.exp(-((distance-30)**2)/300) * np.exp(-((depth-6)**2)/8)
                
                # REE signatures (typically deeper)
                if self.is_in_mineral_zone(lat, lon, 'REE'):
                    if 8 < depth < 14:
                        data[j, i] += 0.5 * np.exp(-((distance-70)**2)/250) * np.exp(-((depth-11)**2)/6)
        
        # Add realistic noise
        data += 0.12 * np.random.randn(samples, traces)
        
        return {
            'data': data,
            'depth_range': depth_range,
            'distance_range': distance_range,
            'traces': traces,
            'samples': samples
        }
        
    def is_in_mineral_zone(self, lat, lon, mineral_type):
        """Check if location is in known mineral zone"""
        # Simple distance-based check to known mineral locations
        for state in self.mineral_database:
            for mineral, info in self.mineral_database[state].items():
                if mineral_type.lower() in mineral.lower():
                    distance = np.sqrt((lat - info['lat'])**2 + (lon - info['lon'])**2)
                    if distance < 0.5:  # Within 0.5 degrees
                        return True
        return False
        
    def extract_local_geochemical_data(self, lat, lon):
        """Extract geochemical data near the specified location"""
        # Filter geochemical data within radius
        radius = 0.5  # degrees
        mask = ((self.geochemical_data['lat'] - lat)**2 + 
                (self.geochemical_data['lon'] - lon)**2) < radius**2
        
        local_data = self.geochemical_data[mask].copy()
        
        if len(local_data) < 10:
            # Generate additional synthetic points if sparse
            additional_points = self.generate_additional_geochemical_points(lat, lon, 20)
            local_data = pd.concat([local_data, additional_points], ignore_index=True)
        
        return local_data
        
    def generate_additional_geochemical_points(self, center_lat, center_lon, n_points):
        """Generate additional geochemical data points around location"""
        np.random.seed(int((center_lat + center_lon) * 1000) % 2**32)
        
        # Generate points in circular pattern around center
        angles = np.random.uniform(0, 2*np.pi, n_points)
        distances = np.random.uniform(0, 0.3, n_points)
        
        lats = center_lat + distances * np.cos(angles)
        lons = center_lon + distances * np.sin(angles)
        
        # Generate realistic geochemical values based on location
        data = {
            'lat': lats,
            'lon': lons,
            'SiO2_%': np.random.normal(65.0, 5.0, n_points),
            'Al2O3_%': np.random.normal(14.5, 2.0, n_points),
            'Fe2O3_%': np.random.normal(5.8, 2.5, n_points),
            'Au_ppb': np.random.lognormal(2.0, 1.5, n_points),
            'Cu_ppm': np.random.lognormal(3.5, 1.0, n_points),
            'REE_ppm': np.random.lognormal(4.8, 1.2, n_points)
        }
        
        return pd.DataFrame(data)
        
    def calculate_mineral_potential(self, lat, lon):
        """Calculate mineral potential scores"""
        potential = {}
        
        # Distance-based scoring to known deposits
        for state in self.mineral_database:
            for mineral, info in self.mineral_database[state].items():
                distance = np.sqrt((lat - info['lat'])**2 + (lon - info['lon'])**2)
                
                # Inverse distance weighting
                if distance < 0.1:
                    score = 0.95
                elif distance < 0.5:
                    score = 0.8 * np.exp(-distance * 2)
                elif distance < 1.0:
                    score = 0.6 * np.exp(-distance * 1.5)
                else:
                    score = 0.3 * np.exp(-distance)
                
                # Adjust based on grade and reserves
                grade_factor = info['grade'] / 100.0 if info['grade'] > 10 else info['grade'] / 10.0
                reserve_factors = {'Very High': 1.2, 'High': 1.0, 'Medium': 0.8, 'Low': 0.6}
                reserve_factor = reserve_factors.get(info['reserves'], 0.5)
                
                final_score = score * grade_factor * reserve_factor
                
                if mineral not in potential:
                    potential[mineral] = final_score
                else:
                    potential[mineral] = max(potential[mineral], final_score)
        
        return potential
        
    def run_3d_analysis(self):
        """Run comprehensive 3D analysis"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please process a location first")
            return
            
        self.progress.start()
        self.update_status("Running 3D analysis...")
        
        thread = threading.Thread(target=self._run_3d_analysis_thread)
        thread.daemon = True
        thread.start()
        
    def _run_3d_analysis_thread(self):
        """Run 3D analysis in separate thread"""
        try:
            project = self.current_project
            
            self.log_result("Starting comprehensive 3D analysis...")
            
            # Perform 3D interpolation
            self.perform_3d_interpolation(project)
            
            # Analyze mineral distributions
            self.analyze_3d_mineral_distribution(project)
            
            # Generate 3D visualizations
            self.create_comprehensive_3d_plots(project)
            
            self.root.after(0, self._analysis_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._analysis_error(str(e)))
            
    def perform_3d_interpolation(self, project):
        """Perform 3D spatial interpolation of geochemical data"""
        self.log_result("Performing 3D spatial interpolation...")
        
        geochem_data = project['geochemical_data']
        
        if len(geochem_data) < 4:
            self.log_result("Insufficient data for interpolation")
            return
        
        # Create interpolation grid
        grid_res = int(self.grid_res_var.get())
        lat_min, lat_max = geochem_data['lat'].min(), geochem_data['lat'].max()
        lon_min, lon_max = geochem_data['lon'].min(), geochem_data['lon'].max()
        
        # Expand grid slightly
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        lat_min -= lat_range * 0.1
        lat_max += lat_range * 0.1
        lon_min -= lon_range * 0.1
        lon_max += lon_range * 0.1
        
        lat_grid = np.linspace(lat_min, lat_max, grid_res)
        lon_grid = np.linspace(lon_min, lon_max, grid_res)
        lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
        
        # Interpolate key elements
        elements = ['Au_ppb', 'Cu_ppm', 'REE_ppm', 'Fe2O3_%', 'SiO2_%']
        interpolated_surfaces = {}
        
        method = self.interp_method_var.get()
        
        for element in elements:
            if element in geochem_data.columns:
                try:
                    if method == 'rbf':
                        # Radial Basis Function interpolation
                        rbf = Rbf(geochem_data['lon'], geochem_data['lat'], 
                                 geochem_data[element], function='cubic')
                        interpolated = rbf(lon_mesh, lat_mesh)
                    else:
                        # Grid data interpolation
                        points = np.column_stack((geochem_data['lon'], geochem_data['lat']))
                        values = geochem_data[element].values
                        interpolated = griddata(points, values, (lon_mesh, lat_mesh), 
                                              method=method, fill_value=np.nan)
                    
                    interpolated_surfaces[element] = {
                        'data': interpolated,
                        'lat_grid': lat_grid,
                        'lon_grid': lon_grid,
                        'lat_mesh': lat_mesh,
                        'lon_mesh': lon_mesh
                    }
                    
                    self.log_result(f"Interpolated {element} using {method} method")
                    
                except Exception as e:
                    self.log_result(f"Failed to interpolate {element}: {e}")
        
        project['interpolated_surfaces'] = interpolated_surfaces
        
    def analyze_3d_mineral_distribution(self, project):
        """Analyze 3D mineral distribution patterns"""
        self.log_result("Analyzing 3D mineral distribution patterns...")
        
        # Combine GPR and geochemical analysis
        gpr_data = project['gpr_data']['data']
        geochem_data = project['geochemical_data']
        
        # Calculate mineral favorability index
        favorability = {}
        
        # Gold favorability
        if 'Au_ppb' in geochem_data.columns:
            au_values = geochem_data['Au_ppb']
            favorability['Gold'] = {
                'mean': au_values.mean(),
                'max': au_values.max(),
                'anomalous_points': len(au_values[au_values > au_values.quantile(0.9)]),
                'favorability_score': min(au_values.mean() / 10.0, 1.0)
            }
        
        # Copper favorability
        if 'Cu_ppm' in geochem_data.columns:
            cu_values = geochem_data['Cu_ppm']
            favorability['Copper'] = {
                'mean': cu_values.mean(),
                'max': cu_values.max(),
                'anomalous_points': len(cu_values[cu_values > cu_values.quantile(0.9)]),
                'favorability_score': min(cu_values.mean() / 100.0, 1.0)
            }
        
        # REE favorability
        if 'REE_ppm' in geochem_data.columns:
            ree_values = geochem_data['REE_ppm']
            favorability['REE'] = {
                'mean': ree_values.mean(),
                'max': ree_values.max(),
                'anomalous_points': len(ree_values[ree_values > ree_values.quantile(0.9)]),
                'favorability_score': min(ree_values.mean() / 200.0, 1.0)
            }
        
        project['analysis_results']['mineral_favorability'] = favorability
        
        # GPR-based structural analysis
        gpr_analysis = self.analyze_gpr_structures(gpr_data)
        project['analysis_results']['gpr_structures'] = gpr_analysis
        
    def analyze_gpr_structures(self, gpr_data):
        """Analyze GPR data for structural features"""
        # Calculate amplitude statistics
        mean_amplitude = np.mean(np.abs(gpr_data))
        max_amplitude = np.max(np.abs(gpr_data))
        
        # Find potential reflectors (high amplitude zones)
        amplitude_threshold = mean_amplitude * 2
        high_amplitude_mask = np.abs(gpr_data) > amplitude_threshold
        
        # Calculate depth distribution of anomalies
        depth_profile = np.sum(high_amplitude_mask, axis=1)
        distance_profile = np.sum(high_amplitude_mask, axis=0)
        
        return {
            'mean_amplitude': mean_amplitude,
            'max_amplitude': max_amplitude,
            'anomaly_count': np.sum(high_amplitude_mask),
            'depth_distribution': depth_profile.tolist(),
            'distance_distribution': distance_profile.tolist()
        }
        
    def create_comprehensive_3d_plots(self, project):
        """Create comprehensive 3D visualizations"""
        self.log_result("Creating comprehensive 3D visualizations...")
        
        try:
            # Create multiple 3D plots
            self.create_3d_gpr_visualization(project)
            self.create_3d_geochemical_visualization(project)
            self.create_integrated_3d_analysis(project)
            
        except Exception as e:
            self.log_result(f"Error creating 3D plots: {e}")
            
    def create_3d_gpr_visualization(self, project):
        """Create 3D GPR visualization"""
        gpr_data = project['gpr_data']
        data = gpr_data['data']
        
        # Create 3D surface plot
        fig = go.Figure()
        
        # Add GPR data as 3D surface
        fig.add_trace(go.Surface(
            z=data,
            x=gpr_data['distance_range'],
            y=gpr_data['depth_range'],
            colorscale='RdBu',
            name='GPR Amplitude'
        ))
        
        fig.update_layout(
            title=f"3D GPR Analysis - {project['name']}",
            scene=dict(
                xaxis_title='Distance (m)',
                yaxis_title='Depth (m)',
                zaxis_title='Amplitude',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            width=1000,
            height=700
        )
        
        # Save and show
        filename = f"3d_gpr_{project['name'].replace(' ', '_')}.html"
        fig.write_html(filename)
        webbrowser.open(filename)
        self.log_result(f"3D GPR visualization saved: {filename}")
        
    def create_3d_geochemical_visualization(self, project):
        """Create 3D geochemical visualization"""
        if 'interpolated_surfaces' not in project or not project['interpolated_surfaces']:
            self.log_result("No interpolated surfaces available")
            return
        
        # Create subplots for multiple elements
        elements = list(project['interpolated_surfaces'].keys())[:4]  # Limit to 4 elements
        
        if len(elements) == 0:
            return
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=elements,
            specs=[[{'type': 'surface'}, {'type': 'surface'}],
                   [{'type': 'surface'}, {'type': 'surface'}]]
        )
        
        for i, element in enumerate(elements):
            surface_data = project['interpolated_surfaces'][element]
            row = i // 2 + 1
            col = i % 2 + 1
            
            fig.add_trace(
                go.Surface(
                    z=surface_data['data'],
                    x=surface_data['lon_grid'],
                    y=surface_data['lat_grid'],
                    colorscale='Viridis',
                    name=element
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title=f"3D Geochemical Analysis - {project['name']}",
            height=800,
            width=1200
        )
        
        filename = f"3d_geochemical_{project['name'].replace(' ', '_')}.html"
        fig.write_html(filename)
        webbrowser.open(filename)
        self.log_result(f"3D geochemical visualization saved: {filename}")
        
    def create_integrated_3d_analysis(self, project):
        """Create integrated 3D analysis combining all data"""
        geochem_data = project['geochemical_data']
        
        if len(geochem_data) == 0:
            return
        
        # Create 3D scatter plot with multiple variables
        fig = go.Figure()
        
        # Add geochemical points
        if 'Au_ppb' in geochem_data.columns:
            fig.add_trace(go.Scatter3d(
                x=geochem_data['lon'],
                y=geochem_data['lat'],
                z=geochem_data['Au_ppb'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=geochem_data['Au_ppb'],
                    colorscale='Reds',
                    colorbar=dict(title="Au (ppb)", x=0.1)
                ),
                name='Gold'
            ))
        
        if 'Cu_ppm' in geochem_data.columns:
            fig.add_trace(go.Scatter3d(
                x=geochem_data['lon'],
                y=geochem_data['lat'],
                z=geochem_data['Cu_ppm'],
                mode='markers',
                marker=dict(
                    size=6,
                    color=geochem_data['Cu_ppm'],
                    colorscale='Blues',
                    colorbar=dict(title="Cu (ppm)", x=0.9)
                ),
                name='Copper',
                visible='legendonly'
            ))
        
        # Add mineral deposit locations
        for state in self.mineral_database:
            for mineral, info in self.mineral_database[state].items():
                if 'Gold' in mineral or 'Copper' in mineral:
                    fig.add_trace(go.Scatter3d(
                        x=[info['lon']],
                        y=[info['lat']],
                        z=[info['grade']],
                        mode='markers',
                        marker=dict(
                            size=15,
                            color='red' if 'Gold' in mineral else 'blue',
                            symbol='diamond'
                        ),
                        name=f"{mineral} Deposit",
                        text=f"{mineral}<br>Grade: {info['grade']}<br>Reserves: {info['reserves']}"
                    ))
        
        fig.update_layout(
            title=f"Integrated 3D Mineral Analysis - {project['name']}",
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Concentration/Grade',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))
            ),
            width=1000,
            height=700
        )
        
        filename = f"integrated_3d_{project['name'].replace(' ', '_')}.html"
        fig.write_html(filename)
        webbrowser.open(filename)
        self.log_result(f"Integrated 3D analysis saved: {filename}")
        
    def create_interactive_map(self):
        """Create interactive map with mineral locations and analysis"""
        if not self.current_project:
            messagebox.showwarning("Warning", "Please process a location first")
            return
            
        self.log_result("Creating interactive mineral targeting map...")
        
        try:
            project = self.current_project
            center_lat = project['location']['latitude']
            center_lon = project['location']['longitude']
            
            # Create base map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=8,
                tiles='OpenStreetMap'
            )
            
            # Add different tile layers
            folium.TileLayer('Stamen Terrain').add_to(m)
            folium.TileLayer('CartoDB positron').add_to(m)
            
            # Add current location marker
            folium.Marker(
                [center_lat, center_lon],
                popup=f"<b>{project['name']}</b><br>Analysis Location",
                tooltip="Current Analysis Location",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Add mineral deposit markers
            for state in self.mineral_database:
                for mineral, info in self.mineral_database[state].items():
                    # Color coding for different minerals
                    color_map = {
                        'Gold': 'yellow',
                        'Copper': 'orange',
                        'Iron Ore': 'red',
                        'REE': 'purple',
                        'Chromite': 'darkgreen',
                        'Nickel': 'lightgreen',
                        'Titanium': 'blue',
                        'Barite': 'gray'
                    }
                    
                    # Find appropriate color
                    color = 'blue'  # default
                    for key, col in color_map.items():
                        if key.lower() in mineral.lower():
                            color = col
                            break
                    
                    # Create popup content
                    popup_content = f"""
                    <b>{mineral}</b><br>
                    Location: {state}<br>
                    Grade: {info['grade']}%<br>
                    Reserves: {info['reserves']}<br>
                    Coordinates: {info['lat']:.4f}, {info['lon']:.4f}
                    """
                    
                    folium.Marker(
                        [info['lat'], info['lon']],
                        popup=folium.Popup(popup_content, max_width=200),
                        tooltip=f"{mineral} - {info['reserves']} reserves",
                        icon=folium.Icon(color=color, icon='star')
                    ).add_to(m)
            
            # Add geochemical data points if available
            if 'geochemical_data' in project and len(project['geochemical_data']) > 0:
                geochem_data = project['geochemical_data']
                
                # Create feature groups for different elements
                au_group = folium.FeatureGroup(name='Gold Anomalies')
                cu_group = folium.FeatureGroup(name='Copper Anomalies')
                ree_group = folium.FeatureGroup(name='REE Anomalies')
                
                for idx, row in geochem_data.iterrows():
                    # Gold anomalies
                    if 'Au_ppb' in geochem_data.columns and row['Au_ppb'] > geochem_data['Au_ppb'].quantile(0.8):
                        folium.CircleMarker(
                            [row['lat'], row['lon']],
                            radius=5,
                            popup=f"Au: {row['Au_ppb']:.2f} ppb",
                            color='gold',
                            fill=True,
                            fillOpacity=0.7
                        ).add_to(au_group)
                    
                    # Copper anomalies
                    if 'Cu_ppm' in geochem_data.columns and row['Cu_ppm'] > geochem_data['Cu_ppm'].quantile(0.8):
                        folium.CircleMarker(
                            [row['lat'], row['lon']],
                            radius=4,
                            popup=f"Cu: {row['Cu_ppm']:.2f} ppm",
                            color='orange',
                            fill=True,
                            fillOpacity=0.7
                        ).add_to(cu_group)
                    
                    # REE anomalies
                    if 'REE_ppm' in geochem_data.columns and row['REE_ppm'] > geochem_data['REE_ppm'].quantile(0.8):
                        folium.CircleMarker(
                            [row['lat'], row['lon']],
                            radius=3,
                            popup=f"REE: {row['REE_ppm']:.2f} ppm",
                            color='purple',
                            fill=True,
                            fillOpacity=0.7
                        ).add_to(ree_group)
                
                au_group.add_to(m)
                cu_group.add_to(m)
                ree_group.add_to(m)
            
            # Add heat map for mineral potential
            if 'mineral_potential' in project:
                potential_data = []
                for state in self.mineral_database:
                    for mineral, info in self.mineral_database[state].items():
                        if mineral in project['mineral_potential']:
                            potential_data.append([
                                info['lat'], 
                                info['lon'], 
                                project['mineral_potential'][mineral]
                            ])
                
                if potential_data:
                    heat_map = plugins.HeatMap(potential_data, name='Mineral Potential')
                    heat_map.add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Add fullscreen button
            plugins.Fullscreen().add_to(m)
            
            # Add measure tool
            plugins.MeasureControl().add_to(m)
            
            # Save map
            map_filename = f"interactive_mineral_map_{project['name'].replace(' ', '_')}.html"
            m.save(map_filename)
            
            # Open in browser
            webbrowser.open(map_filename)
            
            self.log_result(f"Interactive map created: {map_filename}")
            
        except Exception as e:
            self.log_result(f"Error creating interactive map: {e}")
            messagebox.showerror("Error", f"Failed to create map: {e}")
            
    def create_3d_surface(self):
        """Create 3D surface plot"""
        if not self.current_project or 'interpolated_surfaces' not in self.current_project:
            messagebox.showwarning("Warning", "No interpolated data available. Run 3D Analysis first.")
            return
        
        self.create_3d_geochemical_visualization(self.current_project)
        
    def create_3d_scatter(self):
        """Create 3D scatter plot"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project data available")
            return
        
        self.create_integrated_3d_analysis(self.current_project)
        
    def create_3d_interpolation(self):
        """Create 3D interpolation visualization"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project data available")
            return
        
        # Perform interpolation if not done
        if 'interpolated_surfaces' not in self.current_project:
            self.perform_3d_interpolation(self.current_project)
        
        self.create_3d_geochemical_visualization(self.current_project)
        
    def create_mineral_distribution(self):
        """Create mineral distribution visualization"""
        self.create_interactive_map()
        
    def analyze_mineral_potential(self):
        """Analyze mineral potential for selected minerals"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project data available")
            return
        
        selected_minerals = [mineral for mineral, var in self.mineral_vars.items() if var.get()]
        
        if not selected_minerals:
            messagebox.showwarning("Warning", "Please select at least one mineral")
            return
        
        self.log_result(f"Analyzing potential for: {', '.join(selected_minerals)}")
        
        # Detailed analysis for selected minerals
        analysis_results = {}
        
        for mineral in selected_minerals:
            potential_score = self.current_project['mineral_potential'].get(mineral, 0)
            
            # Enhanced analysis based on geochemical data
            if 'geochemical_data' in self.current_project:
                geochem_data = self.current_project['geochemical_data']
                
                if mineral == 'Gold' and 'Au_ppb' in geochem_data.columns:
                    au_stats = {
                        'mean': geochem_data['Au_ppb'].mean(),
                        'max': geochem_data['Au_ppb'].max(),
                        'anomalous_samples': len(geochem_data[geochem_data['Au_ppb'] > 10])
                    }
                    analysis_results[mineral] = {
                        'potential_score': potential_score,
                        'geochemical_stats': au_stats,
                        'recommendation': self.get_mineral_recommendation(mineral, potential_score, au_stats)
                    }
                
                elif mineral == 'Copper' and 'Cu_ppm' in geochem_data.columns:
                    cu_stats = {
                        'mean': geochem_data['Cu_ppm'].mean(),
                        'max': geochem_data['Cu_ppm'].max(),
                        'anomalous_samples': len(geochem_data[geochem_data['Cu_ppm'] > 100])
                    }
                    analysis_results[mineral] = {
                        'potential_score': potential_score,
                        'geochemical_stats': cu_stats,
                        'recommendation': self.get_mineral_recommendation(mineral, potential_score, cu_stats)
                    }
                
                else:
                    analysis_results[mineral] = {
                        'potential_score': potential_score,
                        'recommendation': self.get_mineral_recommendation(mineral, potential_score, {})
                    }
        
        # Display results
        self.display_mineral_analysis_results(analysis_results)
        
    def get_mineral_recommendation(self, mineral, potential_score, stats):
        """Get recommendation based on analysis"""
        if potential_score > 0.8:
            return f"High potential for {mineral}. Recommend detailed exploration."
        elif potential_score > 0.6:
            return f"Moderate potential for {mineral}. Consider follow-up surveys."
        elif potential_score > 0.4:
            return f"Low-moderate potential for {mineral}. Monitor area."
        else:
            return f"Low potential for {mineral} in this area."
            
    def display_mineral_analysis_results(self, results):
        """Display mineral analysis results"""
        self.log_result("\n=== MINERAL POTENTIAL ANALYSIS ===")
        
        for mineral, analysis in results.items():
            self.log_result(f"\n{mineral}:")
            self.log_result(f"  Potential Score: {analysis['potential_score']:.3f}")
            
            if 'geochemical_stats' in analysis:
                stats = analysis['geochemical_stats']
                self.log_result(f"  Mean Concentration: {stats['mean']:.2f}")
                self.log_result(f"  Max Concentration: {stats['max']:.2f}")
                self.log_result(f"  Anomalous Samples: {stats['anomalous_samples']}")
            
            self.log_result(f"  Recommendation: {analysis['recommendation']}")
        
        self.log_result("\n=== END ANALYSIS ===")
        
    def generate_mineral_map(self):
        """Generate comprehensive mineral map"""
        self.create_interactive_map()
        
    def export_mineral_analysis(self):
        """Export comprehensive mineral analysis"""
        if not self.current_project:
            messagebox.showwarning("Warning", "No project data available")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = self.current_project['name'].replace(' ', '_')
            
            # Create export directory
            export_dir = f"mineral_analysis_export_{project_name}_{timestamp}"
            os.makedirs(export_dir, exist_ok=True)
            
            # Export project data
            export_data = {
                'project_info': self.current_project['location'],
                'timestamp': self.current_project['timestamp'],
                'mineral_potential': self.current_project['mineral_potential'],
                'analysis_results': self.current_project.get('analysis_results', {}),
                'processing_log': self.current_project.get('processing_log', [])
            }
            
            # Save as JSON
            with open(os.path.join(export_dir, 'analysis_results.json'), 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Export geochemical data as CSV
            if 'geochemical_data' in self.current_project:
                geochem_file = os.path.join(export_dir, 'geochemical_data.csv')
                self.current_project['geochemical_data'].to_csv(geochem_file, index=False)
            
            # Export GPR data
            if 'gpr_data' in self.current_project:
                gpr_file = os.path.join(export_dir, 'gpr_data.npy')
                np.save(gpr_file, self.current_project['gpr_data']['data'])
            
            # Export interpolated surfaces
            if 'interpolated_surfaces' in self.current_project:
                for element, surface_data in self.current_project['interpolated_surfaces'].items():
                    surface_file = os.path.join(export_dir, f'interpolated_{element}.npy')
                    np.save(surface_file, surface_data['data'])
            
            self.log_result(f"Analysis exported to: {export_dir}")
            messagebox.showinfo("Export Complete", f"Analysis exported to:\n{export_dir}")
            
        except Exception as e:
            self.log_result(f"Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export: {e}")
            
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
        
    def _analysis_complete(self):
        """Handle analysis completion"""
        self.progress.stop()
        self.update_status("Analysis completed")
        self.log_result("3D analysis workflow completed successfully")
        
    def _analysis_error(self, error_msg):
        """Handle analysis error"""
        self.progress.stop()
        self.update_status("Analysis failed")
        self.log_result(f"Analysis error: {error_msg}")
        messagebox.showerror("Analysis Error", error_msg)
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

# Main execution
if __name__ == "__main__":
    print("=" * 80)
    print("Enhanced 3D GPR Mineral Targeting Controller")
    print("IndiaAI Hackathon - Advanced Mineral Discovery Tool")
    print("Features: 3D Visualization, Interactive Mapping, Spatial Interpolation")
    print("=" * 80)
    
    try:
        app = Enhanced3DGPRMineralController()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
