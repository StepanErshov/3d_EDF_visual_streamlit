"""
Simple demo of the Medical Visualization Tool
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Medical Visualization - Simple Demo",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Medical Visualization Tool - Simple Demo")
st.markdown("### Quick demonstration of key features")

@st.cache_data
def create_demo_brain_data():
    """Create demo brain-like 3D data"""
    x, y, z = np.mgrid[0:64, 0:64, 0:64]
    
    brain_structures = []
    
    main_brain = np.sqrt((x-32)**2 + (y-32)**2 + (z-32)**2) < 25
    brain_structures.append(main_brain * 100)
    
    structure1 = np.sqrt((x-25)**2 + (y-30)**2 + (z-30)**2) < 8
    brain_structures.append(structure1 * 150)
    
    structure2 = np.sqrt((x-40)**2 + (y-35)**2 + (z-25)**2) < 6
    brain_structures.append(structure2 * 180)
    
    structure3 = np.sqrt((x-30)**2 + (y-20)**2 + (z-40)**2) < 5
    brain_structures.append(structure3 * 200)
    
    combined_data = np.zeros_like(x, dtype=float)
    for structure in brain_structures:
        combined_data += structure
    
    noise = np.random.normal(0, 5, combined_data.shape)
    combined_data = combined_data + noise
    
    combined_data = np.clip(combined_data, 0, 255)
    
    return combined_data

@st.cache_data
def create_demo_eeg_data():
    """Create demo EEG-like data"""
    duration = 5
    sampling_rate = 256
    time = np.linspace(0, duration, int(duration * sampling_rate))
    
    alpha_wave = 15 * np.sin(2 * np.pi * 10 * time)
    beta_wave = 8 * np.sin(2 * np.pi * 20 * time)
    theta_wave = 12 * np.sin(2 * np.pi * 6 * time)
    
    eeg_signal = alpha_wave + beta_wave + theta_wave
    noise = np.random.normal(0, 3, len(time))
    eeg_signal = eeg_signal + noise
    
    return time, eeg_signal

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎛️ Controls")
    
    demo_type = st.selectbox(
        "Demo Type",
        ["3D Brain Visualization", "Slice Analysis", "EEG Analysis", "Statistics"]
    )
    
    if demo_type == "3D Brain Visualization":
        st.write("**3D Visualization Options:**")
        isovalue = st.slider("Isosurface Value", 0.1, 1.0, 0.3, 0.01)
        opacity = st.slider("Opacity", 0.1, 1.0, 0.7, 0.1)
        
    elif demo_type == "Slice Analysis":
        st.write("**Slice Options:**")
        slice_plane = st.selectbox("Slice Plane", ["axial", "coronal", "sagittal"])
        slice_num = st.slider("Slice Number", 0, 63, 32)
        
    elif demo_type == "EEG Analysis":
        st.write("**EEG Options:**")
        time_range = st.slider("Time Range (seconds)", 0.0, 5.0, (0.0, 2.0), 0.1)
        show_spectrum = st.checkbox("Show Power Spectrum", value=True)
        
    elif demo_type == "Statistics":
        st.write("**Statistical Analysis**")
        st.info("Click 'Generate Analysis' to see statistics")

with col2:
    if st.button("🚀 Generate Demo", key="generate_demo"):
        
        if demo_type == "3D Brain Visualization":
            with st.spinner("Creating 3D visualization..."):
                brain_data = create_demo_brain_data()
                
                from skimage import measure
                try:
                    verts, faces, _, _ = measure.marching_cubes(brain_data, level=isovalue * brain_data.max())
                    
                    fig = go.Figure(data=[go.Mesh3d(
                        x=verts[:, 0],
                        y=verts[:, 1],
                        z=verts[:, 2],
                        i=faces[:, 0],
                        j=faces[:, 1],
                        k=faces[:, 2],
                        opacity=opacity,
                        colorscale='viridis',
                        name='Brain Structure'
                    )])
                    
                    fig.update_layout(
                        scene=dict(
                            xaxis_title='X (mm)',
                            yaxis_title='Y (mm)',
                            zaxis_title='Z (mm)'
                        ),
                        title="Demo Brain 3D Visualization",
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error creating 3D visualization: {e}")
                    st.info("Try adjusting the isosurface value")
        
        elif demo_type == "Slice Analysis":
            with st.spinner("Creating slice analysis..."):
                brain_data = create_demo_brain_data()

                if slice_plane == "axial":
                    slice_data = brain_data[:, :, slice_num]
                elif slice_plane == "coronal":
                    slice_data = brain_data[:, slice_num, :]
                else:
                    slice_data = brain_data[slice_num, :, :]
                
                fig = px.imshow(slice_data, 
                               color_continuous_scale='gray',
                               title=f'Demo {slice_plane.capitalize()} Slice {slice_num}')
                st.plotly_chart(fig, use_container_width=True)
                
                hist_fig = px.histogram(x=slice_data.flatten(), 
                                       title=f'Histogram - {slice_plane.capitalize()} Slice',
                                       nbins=30)
                st.plotly_chart(hist_fig, use_container_width=True)
        
        elif demo_type == "EEG Analysis":
            with st.spinner("Creating EEG analysis..."):
                time, eeg_signal = create_demo_eeg_data()
                
                start_idx = int(time_range[0] * 256)
                end_idx = int(time_range[1] * 256)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=time[start_idx:end_idx], 
                    y=eeg_signal[start_idx:end_idx], 
                    mode='lines', 
                    name='EEG Signal',
                    line=dict(color='blue', width=1)
                ))
                
                fig.update_layout(
                    title='Demo EEG Signal',
                    xaxis_title='Time (s)',
                    yaxis_title='Amplitude (μV)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if show_spectrum:
                    from scipy import signal
                    freqs, psd = signal.welch(eeg_signal, fs=256, nperseg=1024)
                    
                    spectrum_fig = go.Figure()
                    spectrum_fig.add_trace(go.Scatter(
                        x=freqs, 
                        y=psd, 
                        mode='lines',
                        name='Power Spectral Density',
                        line=dict(color='red', width=2)
                    ))
                    
                    spectrum_fig.update_layout(
                        title='Demo Power Spectral Density',
                        xaxis_title='Frequency (Hz)',
                        yaxis_title='Power (μV²/Hz)',
                        height=400
                    )
                    
                    st.plotly_chart(spectrum_fig, use_container_width=True)
        
        elif demo_type == "Statistics":
            with st.spinner("Computing statistics..."):
                brain_data = create_demo_brain_data()
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Data Shape", f"{brain_data.shape}")
                    st.metric("Min Value", f"{brain_data.min():.2f}")
                    st.metric("Max Value", f"{brain_data.max():.2f}")
                
                with col_b:
                    st.metric("Mean Value", f"{brain_data.mean():.2f}")
                    st.metric("Std Deviation", f"{brain_data.std():.2f}")
                    st.metric("Non-zero Voxels", f"{np.count_nonzero(brain_data):,}")
                
                with col_c:
                    st.metric("Total Voxels", f"{brain_data.size:,}")
                    st.metric("Memory Usage", f"{brain_data.nbytes / (1024*1024):.1f} MB")
                
                hist_fig = px.histogram(x=brain_data.flatten(), 
                                       title='Distribution of All Voxel Values',
                                       nbins=50,
                                       color_discrete_sequence=['skyblue'])
                st.plotly_chart(hist_fig, use_container_width=True)

st.markdown("---")
st.markdown("### 📋 About This Demo")

st.info("""
This demo showcases the key features of the Advanced Medical Visualization Tool:

- **3D Brain Visualization**: Interactive 3D rendering of brain-like structures
- **Slice Analysis**: Multi-planar slice viewing with statistical analysis
- **EEG Analysis**: Simulated EEG signal processing and spectral analysis
- **Statistical Analysis**: Comprehensive data statistics and distribution analysis

**To use with real data:** Run the full application with `python run_app.py` and upload your own NIfTI and EEG files.
""")

st.success("🎉 Demo is working! The full application is ready for your medical data.")
