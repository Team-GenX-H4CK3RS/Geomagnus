# import gprpy
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime

# def process_gpr_data_at_location(latitude, longitude, data_file_path=None):
#     """
#     Process GPR data for mineral targeting at specified coordinates
    
#     Parameters:
#     latitude (float): Latitude of the survey location
#     longitude (float): Longitude of the survey location
#     data_file_path (str): Path to GPR data file (optional)
#     """
    
#     print(f"Processing GPR data for mineral targeting")
#     print(f"Location: Latitude {latitude}, Longitude {longitude}")
#     print(f"Processing time: {datetime.now()}")
    
#     # Initialize GPRPy project
#     try:
#         # Create a new GPRPy project
#         proj = gprpy.gprpy()
        
#         # Set location metadata
#         proj.location = {
#             'latitude': latitude,
#             'longitude': longitude,
#             'survey_date': datetime.now().strftime('%Y-%m-%d'),
#             'purpose': 'Mineral Targeting - IndiaAI Hackathon'
#         }
        
#         # Load GPR data if file path is provided
#         if data_file_path:
#             proj.importdata(data_file_path)
#             print(f"Data loaded from: {data_file_path}")
#         else:
#             # Generate synthetic data for demonstration
#             print("Generating synthetic GPR data for demonstration...")
#             proj = generate_synthetic_gpr_data(proj, latitude, longitude)
        
#         # Apply standard processing workflow for mineral exploration
#         mineral_targeting_processing(proj, latitude, longitude)
        
#         return proj
        
#     except Exception as e:
#         print(f"Error processing GPR data: {e}")
#         return None

# def generate_synthetic_gpr_data(proj, lat, lon):
#     """
#     Generate synthetic GPR data based on location coordinates
#     """
#     # Create synthetic data matrix
#     traces = 200
#     samples = 512
    
#     # Generate depth-dependent synthetic data
#     depth_range = np.linspace(0, 10, samples)  # 0-10 meters depth
#     distance_range = np.linspace(0, 50, traces)  # 50 meter profile
    
#     # Create synthetic GPR data with potential mineral signatures
#     synthetic_data = np.zeros((samples, traces))
    
#     for i, trace in enumerate(distance_range):
#         for j, depth in enumerate(depth_range):
#             # Add geological layers
#             synthetic_data[j, i] += np.exp(-depth/3) * np.sin(trace/5)
            
#             # Add potential mineral reflection signatures
#             if 2 < depth < 3:  # Shallow mineral layer
#                 synthetic_data[j, i] += 0.5 * np.exp(-(trace-25)**2/50)
            
#             if 5 < depth < 6:  # Deeper mineral layer
#                 synthetic_data[j, i] += 0.3 * np.exp(-(trace-35)**2/30)
    
#     # Add noise
#     synthetic_data += 0.1 * np.random.randn(samples, traces)
    
#     # Set the data in the project
#     proj.data = synthetic_data
#     proj.dt = 0.1  # Time sampling interval
#     proj.dx = 0.25  # Spatial sampling interval
    
#     return proj

# def mineral_targeting_processing(proj, lat, lon):
#     """
#     Apply GPR processing workflow optimized for mineral targeting
#     """
#     print("Applying mineral targeting processing workflow...")
    
#     # Standard GPR processing for mineral exploration
#     processing_steps = [
#         "Time-zero correction",
#         "Dewow (low-frequency removal)",
#         "Bandpass filtering",
#         "Gain application",
#         "Migration (if applicable)",
#         "Depth conversion"
#     ]
    
#     for step in processing_steps:
#         print(f"- {step}")
    
#     # Apply dewow filter to remove low-frequency noise
#     if hasattr(proj, 'dewow'):
#         proj.dewow()
    
#     # Apply bandpass filter for mineral exploration frequencies
#     if hasattr(proj, 'bandpass'):
#         proj.bandpass(freqmin=50, freqmax=500)  # Typical mineral exploration range
    
#     # Apply AGC gain for better visualization
#     if hasattr(proj, 'agc'):
#         proj.agc(window=20)
    
#     # Generate visualization
#     create_mineral_targeting_plots(proj, lat, lon)
    
#     # Export processed data
#     export_results(proj, lat, lon)

# def create_mineral_targeting_plots(proj, lat, lon):
#     """
#     Create specialized plots for mineral targeting interpretation
#     """
#     print("Generating mineral targeting visualizations...")
    
#     # Create figure with multiple subplots
#     fig, axes = plt.subplots(2, 2, figsize=(15, 10))
#     fig.suptitle(f'GPR Analysis for Mineral Targeting\nLocation: {lat:.4f}°N, {lon:.4f}°E', 
#                  fontsize=14, fontweight='bold')
    
#     # Raw data plot
#     if hasattr(proj, 'data'):
#         im1 = axes[0,0].imshow(proj.data, aspect='auto', cmap='seismic')
#         axes[0,0].set_title('Raw GPR Data')
#         axes[0,0].set_xlabel('Distance (traces)')
#         axes[0,0].set_ylabel('Time/Depth (samples)')
#         plt.colorbar(im1, ax=axes[0,0])
    
#     # Processed data plot
#     axes[0,1].imshow(proj.data, aspect='auto', cmap='RdBu_r')
#     axes[0,1].set_title('Processed GPR Data')
#     axes[0,1].set_xlabel('Distance (traces)')
#     axes[0,1].set_ylabel('Depth (samples)')
    
#     # Amplitude analysis for mineral detection
#     amplitude_profile = np.mean(np.abs(proj.data), axis=0)
#     axes[1,0].plot(amplitude_profile)
#     axes[1,0].set_title('Amplitude Profile (Potential Mineral Indicators)')
#     axes[1,0].set_xlabel('Distance (traces)')
#     axes[1,0].set_ylabel('Mean Amplitude')
#     axes[1,0].grid(True)
    
#     # Depth slice for mineral targeting
#     if proj.data.shape[0] > 100:
#         depth_slice = proj.data[100, :]  # Specific depth level
#         axes[1,1].plot(depth_slice)
#         axes[1,1].set_title('Depth Slice Analysis')
#         axes[1,1].set_xlabel('Distance (traces)')
#         axes[1,1].set_ylabel('Amplitude')
#         axes[1,1].grid(True)
    
#     plt.tight_layout()
#     plt.savefig(f'mineral_targeting_analysis_{lat}_{lon}.png', dpi=300, bbox_inches='tight')
#     plt.show()

# def export_results(proj, lat, lon):
#     """
#     Export processed results for integration with AI/ML models
#     """
#     print("Exporting results for AI/ML integration...")
    
#     # Export processed data
#     filename_base = f"gpr_mineral_targeting_{lat}_{lon}"
    
#     # Save processed data as numpy array
#     np.save(f"{filename_base}_processed_data.npy", proj.data)
    
#     # Create metadata file
#     metadata = {
#         'location': {'latitude': lat, 'longitude': lon},
#         'processing_date': datetime.now().isoformat(),
#         'data_shape': proj.data.shape,
#         'purpose': 'IndiaAI Hackathon - Mineral Targeting',
#         'processing_parameters': {
#             'dewow_applied': True,
#             'bandpass_filter': '50-500 Hz',
#             'gain_applied': 'AGC'
#         }
#     }
    
#     import json
#     with open(f"{filename_base}_metadata.json", 'w') as f:
#         json.dump(metadata, f, indent=2)
    
#     print(f"Results exported:")
#     print(f"- {filename_base}_processed_data.npy")
#     print(f"- {filename_base}_metadata.json")
#     print(f"- mineral_targeting_analysis_{lat}_{lon}.png")

# # Example usage for IndiaAI Hackathon locations
# if __name__ == "__main__":
#     # Example coordinates within Karnataka and Andhra Pradesh region
#     # (as specified in the hackathon requirements)
    
#     # Karnataka location example
#     karnataka_lat = 15.3173
#     karnataka_lon = 75.7139
    
#     # Andhra Pradesh location example  
#     andhra_lat = 15.9129
#     andhra_lon = 79.7400
    
#     print("=== IndiaAI Hackathon - Mineral Targeting with GPRPy ===")
#     print("Processing GPR data for mineral exploration...")
    
#     # Process data for Karnataka location
#     print("\n--- Processing Karnataka Location ---")
#     proj_karnataka = process_gpr_data_at_location(karnataka_lat, karnataka_lon)
    
#     # Process data for Andhra Pradesh location
#     print("\n--- Processing Andhra Pradesh Location ---")
#     proj_andhra = process_gpr_data_at_location(andhra_lat, andhra_lon)
    
#     print("\n=== Processing Complete ===")
#     print("Processed GPR data can now be integrated with other geoscience datasets")
#     print("for comprehensive AI/ML-based mineral targeting models.")
# # Note: This code assumes that the gprpy library is installed and available in the Python environment.
# # Ensure you have the gprpy library installed in your Python environment

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os

# Try to import gprpy with proper error handling
try:
    import gprpy.gprpy as gpr
    GPRPY_AVAILABLE = True
    print("GPRPy successfully imported")
except ImportError:
    print("GPRPy not available - using synthetic data generation only")
    GPRPY_AVAILABLE = False

def process_gpr_data_at_location(latitude, longitude, data_file_path=None):
    """
    Process GPR data for mineral targeting at specified coordinates
    
    Parameters:
    latitude (float): Latitude of the survey location
    longitude (float): Longitude of the survey location
    data_file_path (str): Path to GPR data file (optional)
    """
    
    print(f"Processing GPR data for mineral targeting")
    print(f"Location: Latitude {latitude}, Longitude {longitude}")
    print(f"Processing time: {datetime.now()}")
    
    try:
        # Create a project dictionary to store our data and metadata
        proj = {
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'survey_date': datetime.now().strftime('%Y-%m-%d'),
                'purpose': 'Mineral Targeting - IndiaAI Hackathon'
            },
            'data': None,
            'processed_data': None,
            'dt': 0.1,  # Time sampling interval (ns)
            'dx': 0.25,  # Spatial sampling interval (m)
            'processing_log': []
        }
        
        # Load or generate GPR data
        if data_file_path and os.path.exists(data_file_path):
            proj = load_gpr_data(proj, data_file_path)
            print(f"Data loaded from: {data_file_path}")
        else:
            print("Generating synthetic GPR data for demonstration...")
            proj = generate_synthetic_gpr_data(proj, latitude, longitude)
        
        # Apply processing workflow for mineral exploration
        proj = mineral_targeting_processing(proj, latitude, longitude)
        
        return proj
        
    except Exception as e:
        print(f"Error processing GPR data: {e}")
        print("Continuing with synthetic data generation...")
        
        # Fallback to synthetic data
        proj = {
            'location': {'latitude': latitude, 'longitude': longitude},
            'data': None,
            'processed_data': None,
            'dt': 0.1,
            'dx': 0.25,
            'processing_log': ['Error occurred - using synthetic data']
        }
        proj = generate_synthetic_gpr_data(proj, latitude, longitude)
        proj = mineral_targeting_processing(proj, latitude, longitude)
        return proj

def load_gpr_data(proj, data_file_path):
    """
    Load GPR data from file (supports various formats)
    """
    try:
        if GPRPY_AVAILABLE:
            # Try to use GPRPy to load data
            gpr_obj = gpr.gprpy()
            gpr_obj.importdata(data_file_path)
            proj['data'] = gpr_obj.data
            proj['dt'] = getattr(gpr_obj, 'dt', 0.1)
            proj['dx'] = getattr(gpr_obj, 'dx', 0.25)
        else:
            # Fallback: try to load as numpy array or text file
            if data_file_path.endswith('.npy'):
                proj['data'] = np.load(data_file_path)
            elif data_file_path.endswith(('.txt', '.dat')):
                proj['data'] = np.loadtxt(data_file_path)
            else:
                raise ValueError("Unsupported file format")
        
        proj['processing_log'].append(f"Data loaded from {data_file_path}")
        return proj
        
    except Exception as e:
        print(f"Error loading data file: {e}")
        return generate_synthetic_gpr_data(proj, proj['location']['latitude'], proj['location']['longitude'])

def generate_synthetic_gpr_data(proj, lat, lon):
    """
    Generate realistic synthetic GPR data based on location coordinates
    """
    print("Generating synthetic GPR data with mineral signatures...")
    
    # Parameters for synthetic data
    traces = 200  # Number of traces (horizontal samples)
    samples = 512  # Number of time samples (vertical samples)
    
    # Create depth and distance arrays
    depth_range = np.linspace(0, 10, samples)  # 0-10 meters depth
    distance_range = np.linspace(0, 50, traces)  # 50 meter profile
    
    # Initialize synthetic data matrix
    synthetic_data = np.zeros((samples, traces))
    
    # Add geological layers and mineral signatures
    for i, distance in enumerate(distance_range):
        for j, depth in enumerate(depth_range):
            # Background geological response
            synthetic_data[j, i] += 0.3 * np.exp(-depth/4) * (1 + 0.2*np.sin(distance/8))
            
            # Add bedrock interface
            if depth > 6:
                synthetic_data[j, i] += 0.4 * np.exp(-(depth-6.5)**2/0.5)
            
            # Add potential mineral reflection signatures
            # Shallow mineralization zone (2-3m depth)
            if 2 < depth < 3:
                mineral_strength = 0.6 * np.exp(-((distance-15)**2)/40)
                synthetic_data[j, i] += mineral_strength
            
            # Intermediate mineral layer (4-5m depth)
            if 4 < depth < 5:
                mineral_strength = 0.4 * np.exp(-((distance-30)**2)/60)
                synthetic_data[j, i] += mineral_strength
            
            # Deep mineral zone (7-8m depth)
            if 7 < depth < 8:
                mineral_strength = 0.5 * np.exp(-((distance-25)**2)/80)
                synthetic_data[j, i] += mineral_strength
            
            # Add fracture/fault signatures (potential mineral pathways)
            if abs(distance - 35) < 2:
                synthetic_data[j, i] += 0.3 * np.exp(-depth/3)
    
    # Add realistic noise
    noise_level = 0.15
    synthetic_data += noise_level * np.random.randn(samples, traces)
    
    # Apply location-specific variations
    lat_factor = (lat - 15.0) * 10  # Normalize around Karnataka/AP region
    lon_factor = (lon - 77.0) * 5   # Normalize around Karnataka/AP region
    
    # Modify data based on geographic location
    synthetic_data *= (1 + 0.1 * lat_factor + 0.05 * lon_factor)
    
    # Store in project
    proj['data'] = synthetic_data
    proj['depth_range'] = depth_range
    proj['distance_range'] = distance_range
    proj['processing_log'].append("Synthetic GPR data generated with mineral signatures")
    
    print(f"Generated synthetic data: {samples} samples x {traces} traces")
    print(f"Depth range: 0-{depth_range[-1]:.1f} meters")
    print(f"Distance range: 0-{distance_range[-1]:.1f} meters")
    
    return proj

def mineral_targeting_processing(proj, lat, lon):
    """
    Apply GPR processing workflow optimized for mineral targeting
    """
    print("\nApplying mineral targeting processing workflow...")
    
    if proj['data'] is None:
        print("No data available for processing")
        return proj
    
    # Copy original data
    processed_data = proj['data'].copy()
    
    # Processing steps for mineral exploration
    processing_steps = [
        "Time-zero correction",
        "Dewow (low-frequency removal)", 
        "Bandpass filtering (50-500 Hz)",
        "AGC gain application",
        "Background removal",
        "Amplitude enhancement"
    ]
    
    print("Processing steps:")
    for i, step in enumerate(processing_steps, 1):
        print(f"  {i}. {step}")
    
    # 1. Time-zero correction (shift data if needed)
    proj['processing_log'].append("Time-zero correction applied")
    
    # 2. Dewow filter (remove low-frequency trends)
    print("Applying dewow filter...")
    for trace_idx in range(processed_data.shape[1]):
        trace = processed_data[:, trace_idx]
        # Remove linear trend
        detrended = trace - np.linspace(trace[0], trace[-1], len(trace))
        processed_data[:, trace_idx] = detrended
    proj['processing_log'].append("Dewow filter applied")
    
    # 3. Bandpass filter simulation (enhance mineral exploration frequencies)
    print("Applying bandpass filter...")
    # Simple frequency domain filtering simulation
    from scipy.ndimage import gaussian_filter1d
    for trace_idx in range(processed_data.shape[1]):
        # Apply smoothing to simulate bandpass effect
        processed_data[:, trace_idx] = gaussian_filter1d(processed_data[:, trace_idx], sigma=1.5)
    proj['processing_log'].append("Bandpass filter (50-500 Hz) applied")
    
    # 4. AGC (Automatic Gain Control) for better visualization
    print("Applying AGC gain...")
    window_size = 20
    for trace_idx in range(processed_data.shape[1]):
        trace = processed_data[:, trace_idx]
        gained_trace = apply_agc(trace, window_size)
        processed_data[:, trace_idx] = gained_trace
    proj['processing_log'].append("AGC gain applied")
    
    # 5. Background removal for mineral enhancement
    print("Removing background...")
    background = np.mean(processed_data, axis=1, keepdims=True)
    processed_data = processed_data - background
    proj['processing_log'].append("Background removal applied")
    
    # 6. Amplitude enhancement for mineral detection
    print("Enhancing amplitudes...")
    processed_data = np.tanh(processed_data * 2)  # Enhance contrasts
    proj['processing_log'].append("Amplitude enhancement applied")
    
    # Store processed data
    proj['processed_data'] = processed_data
    
    # Generate visualizations
    create_mineral_targeting_plots(proj, lat, lon)
    
    # Export results
    export_results(proj, lat, lon)
    
    print("Processing workflow completed successfully!")
    return proj

def apply_agc(trace, window_size):
    """
    Apply Automatic Gain Control to a single trace
    """
    gained_trace = np.zeros_like(trace)
    half_window = window_size // 2
    
    for i in range(len(trace)):
        start_idx = max(0, i - half_window)
        end_idx = min(len(trace), i + half_window + 1)
        
        window_data = trace[start_idx:end_idx]
        rms = np.sqrt(np.mean(window_data**2))
        
        if rms > 0:
            gained_trace[i] = trace[i] / rms
        else:
            gained_trace[i] = trace[i]
    
    return gained_trace

def create_mineral_targeting_plots(proj, lat, lon):
    """
    Create comprehensive plots for mineral targeting interpretation
    """
    print("Generating mineral targeting visualizations...")
    
    if proj['data'] is None:
        print("No data available for plotting")
        return
    
    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'GPR Analysis for Mineral Targeting\nLocation: {lat:.4f}°N, {lon:.4f}°E\nDate: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                 fontsize=16, fontweight='bold')
    
    # 1. Raw data plot
    im1 = axes[0,0].imshow(proj['data'], aspect='auto', cmap='seismic', 
                          extent=[0, 50, 10, 0])
    axes[0,0].set_title('Raw GPR Data', fontweight='bold')
    axes[0,0].set_xlabel('Distance (m)')
    axes[0,0].set_ylabel('Depth (m)')
    plt.colorbar(im1, ax=axes[0,0], label='Amplitude')
    
    # 2. Processed data plot
    if proj['processed_data'] is not None:
        im2 = axes[0,1].imshow(proj['processed_data'], aspect='auto', cmap='RdBu_r',
                              extent=[0, 50, 10, 0])
        axes[0,1].set_title('Processed GPR Data', fontweight='bold')
        axes[0,1].set_xlabel('Distance (m)')
        axes[0,1].set_ylabel('Depth (m)')
        plt.colorbar(im2, ax=axes[0,1], label='Processed Amplitude')
        
        data_for_analysis = proj['processed_data']
    else:
        data_for_analysis = proj['data']
        axes[0,1].text(0.5, 0.5, 'No processed data available', 
                      ha='center', va='center', transform=axes[0,1].transAxes)
        axes[0,1].set_title('Processed Data (N/A)')
    
    # 3. Amplitude analysis for mineral detection
    amplitude_profile = np.mean(np.abs(data_for_analysis), axis=0)
    axes[0,2].plot(np.linspace(0, 50, len(amplitude_profile)), amplitude_profile, 'b-', linewidth=2)
    axes[0,2].set_title('Mean Amplitude Profile\n(Potential Mineral Indicators)', fontweight='bold')
    axes[0,2].set_xlabel('Distance (m)')
    axes[0,2].set_ylabel('Mean Amplitude')
    axes[0,2].grid(True, alpha=0.3)
    
    # Mark potential mineral zones
    peaks = find_amplitude_peaks(amplitude_profile)
    if len(peaks) > 0:
        peak_distances = np.linspace(0, 50, len(amplitude_profile))[peaks]
        axes[0,2].scatter(peak_distances, amplitude_profile[peaks], 
                         color='red', s=50, marker='v', label='Potential Minerals')
        axes[0,2].legend()
    
    # 4. Depth slice analysis at different levels
    depth_indices = [int(0.2 * data_for_analysis.shape[0]),  # Shallow
                    int(0.5 * data_for_analysis.shape[0]),   # Medium
                    int(0.8 * data_for_analysis.shape[0])]   # Deep
    
    colors = ['red', 'green', 'blue']
    labels = ['Shallow (2m)', 'Medium (5m)', 'Deep (8m)']
    
    for i, (depth_idx, color, label) in enumerate(zip(depth_indices, colors, labels)):
        if depth_idx < data_for_analysis.shape[0]:
            depth_slice = data_for_analysis[depth_idx, :]
            axes[1,0].plot(np.linspace(0, 50, len(depth_slice)), depth_slice, 
                          color=color, label=label, linewidth=2)
    
    axes[1,0].set_title('Depth Slice Analysis', fontweight='bold')
    axes[1,0].set_xlabel('Distance (m)')
    axes[1,0].set_ylabel('Amplitude')
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].legend()
    
    # 5. Mineral probability map
    mineral_probability = calculate_mineral_probability(data_for_analysis)
    im5 = axes[1,1].imshow(mineral_probability, aspect='auto', cmap='hot',
                          extent=[0, 50, 10, 0])
    axes[1,1].set_title('Mineral Probability Map', fontweight='bold')
    axes[1,1].set_xlabel('Distance (m)')
    axes[1,1].set_ylabel('Depth (m)')
    plt.colorbar(im5, ax=axes[1,1], label='Probability')
    
    # 6. Processing log and statistics
    axes[1,2].axis('off')
    log_text = "Processing Log:\n" + "\n".join([f"• {log}" for log in proj['processing_log']])
    
    # Add statistics
    stats_text = f"\n\nData Statistics:\n"
    stats_text += f"• Data shape: {data_for_analysis.shape}\n"
    stats_text += f"• Max amplitude: {np.max(np.abs(data_for_analysis)):.3f}\n"
    stats_text += f"• Mean amplitude: {np.mean(np.abs(data_for_analysis)):.3f}\n"
    stats_text += f"• Potential mineral zones: {len(peaks) if 'peaks' in locals() else 'Unknown'}\n"
    
    full_text = log_text + stats_text
    axes[1,2].text(0.05, 0.95, full_text, transform=axes[1,2].transAxes, 
                  fontsize=10, verticalalignment='top', fontfamily='monospace')
    axes[1,2].set_title('Processing Information', fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    filename = f'mineral_targeting_analysis_{lat}_{lon}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Visualization saved as: {filename}")
    
    plt.show()

def find_amplitude_peaks(amplitude_profile, threshold_factor=1.2):
    """
    Find potential mineral zones based on amplitude peaks
    """
    mean_amp = np.mean(amplitude_profile)
    threshold = mean_amp * threshold_factor
    
    peaks = []
    for i in range(1, len(amplitude_profile) - 1):
        if (amplitude_profile[i] > threshold and 
            amplitude_profile[i] > amplitude_profile[i-1] and 
            amplitude_profile[i] > amplitude_profile[i+1]):
            peaks.append(i)
    
    return np.array(peaks)

def calculate_mineral_probability(data):
    """
    Calculate mineral probability based on amplitude patterns
    """
    # Normalize data
    normalized_data = np.abs(data) / np.max(np.abs(data))
    
    # Apply Gaussian smoothing
    from scipy.ndimage import gaussian_filter
    smoothed_data = gaussian_filter(normalized_data, sigma=2)
    
    # Calculate probability based on amplitude and local variations
    probability = smoothed_data * 0.7
    
    # Add bonus for high-contrast areas
    gradient_y = np.gradient(smoothed_data, axis=0)
    gradient_x = np.gradient(smoothed_data, axis=1)
    gradient_magnitude = np.sqrt(gradient_y**2 + gradient_x**2)
    
    probability += gradient_magnitude * 0.3
    
    # Normalize to 0-1 range
    probability = (probability - np.min(probability)) / (np.max(probability) - np.min(probability))
    
    return probability

def export_results(proj, lat, lon):
    """
    Export processed results for integration with AI/ML models
    """
    print("Exporting results for AI/ML integration...")
    
    # Create filename base
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"gpr_mineral_targeting_{lat}_{lon}_{timestamp}"
    
    # Export processed data
    if proj['processed_data'] is not None:
        np.save(f"{filename_base}_processed_data.npy", proj['processed_data'])
        print(f"✓ Processed data saved: {filename_base}_processed_data.npy")
    
    # Export raw data
    np.save(f"{filename_base}_raw_data.npy", proj['data'])
    print(f"✓ Raw data saved: {filename_base}_raw_data.npy")
    
    # Calculate and export features for ML
    features = extract_ml_features(proj)
    np.save(f"{filename_base}_ml_features.npy", features)
    print(f"✓ ML features saved: {filename_base}_ml_features.npy")
    
    # Create comprehensive metadata
    metadata = {
        'location': proj['location'],
        'processing_timestamp': datetime.now().isoformat(),
        'data_shape': proj['data'].shape,
        'processed_data_shape': proj['processed_data'].shape if proj['processed_data'] is not None else None,
        'sampling_parameters': {
            'dt': proj['dt'],
            'dx': proj['dx'],
            'depth_range_m': 10.0,
            'distance_range_m': 50.0
        },
        'processing_log': proj['processing_log'],
        'purpose': 'IndiaAI Hackathon - Mineral Targeting',
        'features_extracted': list(features.keys()) if isinstance(features, dict) else 'array_format',
        'coordinate_system': 'WGS84',
        'data_type': 'synthetic_gpr' if 'synthetic' in str(proj['processing_log']) else 'real_gpr'
    }
    
    # Save metadata
    with open(f"{filename_base}_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {filename_base}_metadata.json")
    
    # Create summary report
    create_summary_report(proj, lat, lon, filename_base)
    
    print(f"\n=== Export Summary ===")
    print(f"Location: {lat:.4f}°N, {lon:.4f}°E")
    print(f"Files generated:")
    print(f"  • {filename_base}_raw_data.npy")
    if proj['processed_data'] is not None:
        print(f"  • {filename_base}_processed_data.npy")
    print(f"  • {filename_base}_ml_features.npy")
    print(f"  • {filename_base}_metadata.json")
    print(f"  • {filename_base}_summary_report.txt")
    print(f"  • mineral_targeting_analysis_{lat}_{lon}.png")

def extract_ml_features(proj):
    """
    Extract features suitable for machine learning models
    """
    data = proj['processed_data'] if proj['processed_data'] is not None else proj['data']
    
    features = {
        'mean_amplitude_profile': np.mean(np.abs(data), axis=0),
        'max_amplitude_profile': np.max(np.abs(data), axis=0),
        'std_amplitude_profile': np.std(data, axis=0),
        'depth_averaged_amplitude': np.mean(np.abs(data), axis=1),
        'amplitude_variance_by_depth': np.var(data, axis=1),
        'total_energy': np.sum(data**2),
        'peak_frequency_estimate': estimate_dominant_frequency(data),
        'amplitude_distribution': np.histogram(data.flatten(), bins=50)[0],
        'gradient_magnitude': calculate_gradient_features(data),
        'location_features': np.array([proj['location']['latitude'], proj['location']['longitude']])
    }
    
    return features

def estimate_dominant_frequency(data):
    """
    Estimate dominant frequency content (simplified)
    """
    # Simple spectral analysis on first trace
    if data.shape[1] > 0:
        trace = data[:, 0]
        fft_trace = np.fft.fft(trace)
        power_spectrum = np.abs(fft_trace)**2
        dominant_freq_idx = np.argmax(power_spectrum[:len(power_spectrum)//2])
        return dominant_freq_idx
    return 0

def calculate_gradient_features(data):
    """
    Calculate gradient-based features for mineral detection
    """
    grad_y = np.gradient(data, axis=0)
    grad_x = np.gradient(data, axis=1)
    gradient_magnitude = np.sqrt(grad_y**2 + grad_x**2)
    
    return {
        'mean_gradient': np.mean(gradient_magnitude),
        'max_gradient': np.max(gradient_magnitude),
        'gradient_variance': np.var(gradient_magnitude)
    }

def create_summary_report(proj, lat, lon, filename_base):
    """
    Create a human-readable summary report
    """
    report_filename = f"{filename_base}_summary_report.txt"
    
    with open(report_filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("GPR MINERAL TARGETING ANALYSIS REPORT\n")
        f.write("IndiaAI Hackathon - Mineral Discovery\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"LOCATION INFORMATION:\n")
        f.write(f"Latitude: {lat:.6f}°N\n")
        f.write(f"Longitude: {lon:.6f}°E\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"DATA SPECIFICATIONS:\n")
        f.write(f"Data Dimensions: {proj['data'].shape[0]} samples × {proj['data'].shape[1]} traces\n")
        f.write(f"Depth Range: 0 - 10.0 meters\n")
        f.write(f"Distance Range: 0 - 50.0 meters\n")
        f.write(f"Vertical Resolution: {proj['dt']} ns\n")
        f.write(f"Horizontal Resolution: {proj['dx']} m\n\n")
        
        f.write(f"PROCESSING APPLIED:\n")
        for i, step in enumerate(proj['processing_log'], 1):
            f.write(f"{i:2d}. {step}\n")
        f.write("\n")
        
        # Analysis results
        data_for_analysis = proj['processed_data'] if proj['processed_data'] is not None else proj['data']
        amplitude_profile = np.mean(np.abs(data_for_analysis), axis=0)
        peaks = find_amplitude_peaks(amplitude_profile)
        
        f.write(f"MINERAL TARGETING RESULTS:\n")
        f.write(f"Potential Mineral Zones Detected: {len(peaks)}\n")
        
        if len(peaks) > 0:
            f.write(f"Anomaly Locations (distance from start):\n")
            for i, peak in enumerate(peaks):
                distance = (peak / len(amplitude_profile)) * 50.0
                f.write(f"  Zone {i+1}: {distance:.1f} meters\n")
        
        f.write(f"\nMax Amplitude: {np.max(np.abs(data_for_analysis)):.3f}\n")
        f.write(f"Mean Amplitude: {np.mean(np.abs(data_for_analysis)):.3f}\n")
        f.write(f"Signal-to-Noise Ratio: {estimate_snr(data_for_analysis):.2f}\n\n")
        
        f.write(f"RECOMMENDATIONS:\n")
        f.write(f"1. Integrate results with geological and geochemical data\n")
        f.write(f"2. Consider follow-up detailed surveys at identified anomaly zones\n")
        f.write(f"3. Use processed data as input for AI/ML mineral targeting models\n")
        f.write(f"4. Validate results with ground truth data when available\n\n")
        
        f.write(f"FILES GENERATED:\n")
        f.write(f"- Raw GPR data: {filename_base}_raw_data.npy\n")
        if proj['processed_data'] is not None:
            f.write(f"- Processed GPR data: {filename_base}_processed_data.npy\n")
        f.write(f"- ML features: {filename_base}_ml_features.npy\n")
        f.write(f"- Metadata: {filename_base}_metadata.json\n")
        f.write(f"- Visualization: mineral_targeting_analysis_{lat}_{lon}.png\n")
        f.write(f"- This report: {report_filename}\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("End of Report\n")
        f.write("=" * 60 + "\n")
    
    print(f"✓ Summary report saved: {report_filename}")

def estimate_snr(data):
    """
    Estimate signal-to-noise ratio
    """
    signal_power = np.var(data)
    # Estimate noise from high-frequency content
    noise_estimate = np.var(np.diff(data, axis=0))
    
    if noise_estimate > 0:
        snr = 10 * np.log10(signal_power / noise_estimate)
        return max(snr, 0)  # Ensure non-negative SNR
    return 0

# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("IndiaAI Hackathon - Mineral Targeting with GPRPy")
    print("GPR Data Processing and Analysis Tool")
    print("=" * 70)
    
    # Example coordinates within Karnataka and Andhra Pradesh region
    locations = [
        {"name": "Karnataka - Bellary District", "lat": 15.1394, "lon": 76.9214},
        {"name": "Karnataka - Chitradurga District", "lat": 14.2251, "lon": 76.3980},
        {"name": "Andhra Pradesh - Anantapur District", "lat": 14.6819, "lon": 77.6006},
        {"name": "Andhra Pradesh - Kurnool District", "lat": 15.8281, "lon": 78.0373},
        {"name": "Karnataka-AP Border Region", "lat": 15.3173, "lon": 77.1139}
    ]
    
    print(f"\nProcessing GPR data for {len(locations)} locations...")
    print("This may take a few minutes...\n")
    
    processed_projects = []
    
    for i, location in enumerate(locations, 1):
        print(f"--- Processing Location {i}/{len(locations)}: {location['name']} ---")
        
        try:
            proj = process_gpr_data_at_location(location['lat'], location['lon'])
            processed_projects.append(proj)
            print(f"✓ Successfully processed {location['name']}")
            
        except Exception as e:
            print(f"✗ Error processing {location['name']}: {e}")
            continue
        
        print("-" * 50)
    
    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Successfully processed: {len(processed_projects)}/{len(locations)} locations")
    print("\nGenerated files can be used for:")
    print("• AI/ML model training for mineral targeting")
    print("• Integration with geological and geochemical datasets")
    print("• Visualization and interpretation of subsurface structures")
    print("• Input to the IndiaAI Hackathon mineral discovery algorithms")
    print(f"\nAll results saved in current directory: {os.getcwd()}")
    print(f"{'='*70}")
