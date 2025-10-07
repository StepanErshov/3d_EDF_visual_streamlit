# 🧠 Advanced Medical Visualization Tool

A comprehensive web-based application for medical data visualization and analysis, built with Streamlit. This tool provides advanced capabilities for visualizing NIfTI files and analyzing EEG data.

## ✨ Features

### 🎨 3D Visualization
- **Volume Rendering**: Interactive 3D volume visualization with customizable opacity and color maps
- **Isosurface Generation**: Create 3D surfaces from volume data
- **Orthogonal Slices**: View axial, coronal, and sagittal slices simultaneously
- **Real-time Controls**: Adjust visualization parameters in real-time

### 🔍 Slice Analysis
- **Interactive Slicing**: Navigate through different slices with slider controls
- **Multi-plane Views**: Axial, coronal, and sagittal orientations
- **Histogram Analysis**: Statistical distribution of slice data
- **Customizable Display**: Adjust contrast, brightness, and color maps

### 🧠 EEG Analysis
- **Multi-channel Support**: Analyze multiple EEG channels
- **Spectral Analysis**: Power spectral density and frequency domain analysis
- **Rhythm Classification**: Automatic classification of EEG rhythms (delta, theta, alpha, beta, gamma)
- **Time-series Visualization**: Interactive plotting with zoom and pan capabilities

### 🔬 Advanced Features
- **Data Preprocessing**: Normalization, filtering, and morphological operations
- **Segmentation Analysis**: Threshold-based and watershed segmentation
- **ROI Analysis**: Region of Interest selection and statistical analysis
- **Multi-modal Fusion**: Combine different data modalities
- **Export Capabilities**: Export visualizations and reports in various formats

### 📊 Statistical Analysis
- **Comprehensive Statistics**: Detailed volume and spatial statistics
- **Data Distribution Analysis**: Histograms and distribution plots
- **Spatial Analysis**: Mean values along different axes
- **Comparative Analysis**: Side-by-side data comparison

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   cd web
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run_app.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   - The application will automatically open at `http://localhost:8501`
   - If not, navigate to the URL manually

## 📁 Data Formats

### Supported Input Formats
- **NIfTI Files**: `.nii`, `.nii.gz` (upload as ZIP archives)
- **EEG Files**: `.edf` (European Data Format)

### Sample Data
The application includes sample data from the original 3d-nii-visualizer-master project:
- Brain tumor segmentation data (BRATS dataset)
- EEG recordings in EDF format

## 🎯 Usage Guide

### 1. Data Upload
- **Home Page**: Upload ZIP files containing NIfTI files or individual EDF files
- **Data Overview**: View file statistics and metadata
- **Data Validation**: Automatic format checking and error reporting

### 2. 3D Visualization
- **Select Visualization Type**: Choose from volume rendering, isosurface, or orthogonal slices
- **Adjust Parameters**: Modify opacity, threshold, and color settings
- **Interactive Controls**: Rotate, zoom, and pan the 3D visualization

### 3. Slice Analysis
- **Navigate Slices**: Use sliders to move through different anatomical planes
- **View Statistics**: Examine histograms and statistical measures
- **Compare Views**: Switch between different slice orientations

### 4. EEG Analysis
- **Channel Selection**: Choose specific EEG channels for analysis
- **Time Range**: Select specific time periods for detailed analysis
- **Spectral Analysis**: View power spectral density and frequency content
- **Rhythm Classification**: Automatic identification of brain rhythms

### 5. Advanced Features
- **Preprocessing**: Apply filters, normalization, and morphological operations
- **Segmentation**: Perform automated tissue segmentation
- **ROI Analysis**: Define and analyze specific regions of interest
- **Export Results**: Save visualizations and analysis reports

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Visualization**: Plotly for interactive plots
- **Medical Imaging**: Nibabel for NIfTI file handling
- **EEG Processing**: MNE-Python for EEG analysis
- **Image Processing**: Scikit-image for advanced image operations

### Performance
- **Memory Management**: Efficient handling of large medical datasets
- **Caching**: Streamlit session state for optimal performance
- **Temporary Files**: Automatic cleanup of uploaded data
- **Responsive Design**: Optimized for different screen sizes

### Browser Compatibility
- **Recommended**: Chrome, Firefox, Safari (latest versions)
- **Mobile**: Responsive design works on tablets and phones
- **WebGL**: Required for 3D visualizations

## 🔧 Configuration

### Environment Variables
```bash
STREAMLIT_SERVER_FILE_WATCHER_TYPE=none  # Disable file watching for better performance
```

### Customization
- **Color Schemes**: Modify color maps in the visualization settings
- **Default Parameters**: Adjust default values in the configuration files
- **UI Themes**: Customize the Streamlit theme in `.streamlit/config.toml`

## 📚 API Reference

### Main Functions
- `load_nifti_file()`: Load and validate NIfTI files
- `create_3d_surface_plot()`: Generate 3D surface visualizations
- `create_slice_plots()`: Create 2D slice visualizations
- `create_eeg_plot()`: Generate EEG time-series plots
- `analyze_volume_statistics()`: Compute comprehensive statistics

### Utility Functions
- `normalize_data()`: Data normalization methods
- `apply_filters()`: Image filtering operations
- `segment_regions()`: Automated segmentation
- `compute_statistics()`: Statistical analysis

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Memory Issues**
   - Reduce image resolution in visualization settings
   - Use smaller time ranges for EEG analysis
   - Clear browser cache and restart

3. **File Upload Problems**
   - Ensure files are in supported formats
   - Check file size limits (typically 200MB)
   - Verify ZIP file contains valid NIfTI files

4. **Performance Issues**
   - Close other browser tabs
   - Use a modern browser with WebGL support
   - Consider using a more powerful computer for large datasets

### Getting Help
- Check the console output for error messages
- Verify all dependencies are installed correctly
- Ensure sufficient system memory and processing power

## 📄 License

This project is based on the original 3d-nii-visualizer-master and extends its functionality for web-based medical data analysis.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review the console output for error messages
- Ensure all dependencies are properly installed

---

**Built with ❤️ for medical data analysis and visualization**
