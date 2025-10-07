import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import nibabel as nib
import tempfile
import os

def create_demo_data():
    x, y, z = np.mgrid[0:100, 0:100, 0:100]
    
    sphere1 = np.sqrt((x-30)**2 + (y-30)**2 + (z-30)**2) < 15
    sphere2 = np.sqrt((x-70)**2 + (y-70)**2 + (z-70)**2) < 20
    sphere3 = np.sqrt((x-50)**2 + (y-20)**2 + (z-80)**2) < 10
    
    demo_data = sphere1 * 100 + sphere2 * 150 + sphere3 * 200
    
    noise = np.random.normal(0, 10, demo_data.shape)
    demo_data = demo_data + noise
    
    demo_data = np.clip(demo_data, 0, 255).astype(np.uint8)
    
    return demo_data

def create_demo_eeg_data():
    
    # Параметры сигнала
    duration = 10  # секунды
    sampling_rate = 256  # Гц
    time = np.linspace(0, duration, int(duration * sampling_rate))
    
    # Создаем смесь синусоидальных волн разных частот
    alpha_wave = 10 * np.sin(2 * np.pi * 10 * time)  # Альфа ритм (10 Гц)
    beta_wave = 5 * np.sin(2 * np.pi * 20 * time)    # Бета ритм (20 Гц)
    theta_wave = 8 * np.sin(2 * np.pi * 6 * time)    # Тета ритм (6 Гц)
    
    eeg_signal = alpha_wave + beta_wave + theta_wave
    
    noise = np.random.normal(0, 2, len(time))
    eeg_signal = eeg_signal + noise
    
    return time, eeg_signal

def demo_3d_visualization():
    
    st.subheader("🎨 3D Visualization Demo")
    
    demo_data = create_demo_data()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**Controls**")
        isovalue = st.slider("Isosurface Value", 0.0, 1.0, 0.3, 0.01)
        opacity = st.slider("Opacity", 0.0, 1.0, 0.7, 0.1)
        
        visualization_type = st.selectbox(
            "Visualization Type",
            ["3D Surface", "Volume Rendering", "Orthogonal Slices"]
        )
    
    with col2:
        if visualization_type == "3D Surface":
            from skimage import measure
            verts, faces, _, _ = measure.marching_cubes(demo_data, level=isovalue * demo_data.max())
            
            fig = go.Figure(data=[go.Mesh3d(
                x=verts[:, 0],
                y=verts[:, 1],
                z=verts[:, 2],
                i=faces[:, 0],
                j=faces[:, 1],
                k=faces[:, 2],
                opacity=opacity,
                colorscale='viridis',
                name='3D Surface'
            )])
            
            fig.update_layout(
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z'
                ),
                title="Demo 3D Surface Visualization"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif visualization_type == "Orthogonal Slices":
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Axial', 'Coronal', 'Sagittal', '3D View'),
                specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}],
                       [{'type': 'heatmap'}, {'type': 'scatter3d'}]]
            )
            
            # Axial slice
            axial_slice = demo_data[:, :, 50]
            fig.add_trace(go.Heatmap(z=axial_slice, colorscale='gray', showscale=False), row=1, col=1)
            
            # Coronal slice
            coronal_slice = demo_data[:, 50, :]
            fig.add_trace(go.Heatmap(z=coronal_slice, colorscale='gray', showscale=False), row=1, col=2)
            
            # Sagittal slice
            sagittal_slice = demo_data[50, :, :]
            fig.add_trace(go.Heatmap(z=sagittal_slice, colorscale='gray', showscale=False), row=2, col=1)
            
            # 3D scatter
            x, y, z = np.where(demo_data > np.percentile(demo_data, 95))
            fig.add_trace(go.Scatter3d(x=x[::100], y=y[::100], z=z[::100], 
                                      mode='markers', marker=dict(size=2)), row=2, col=2)
            
            fig.update_layout(height=600, title_text="Demo Orthogonal Views")
            st.plotly_chart(fig, use_container_width=True)

def demo_slice_analysis():
    
    st.subheader("🔍 Slice Analysis Demo")
    
    demo_data = create_demo_data()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**Slice Controls**")
        slice_type = st.selectbox("Slice Type", ["axial", "coronal", "sagittal"])
        
        if slice_type == "axial":
            slice_num = st.slider("Slice Number", 0, demo_data.shape[2]-1, 50)
            slice_data = demo_data[:, :, slice_num]
        elif slice_type == "coronal":
            slice_num = st.slider("Slice Number", 0, demo_data.shape[1]-1, 50)
            slice_data = demo_data[:, slice_num, :]
        else:  # sagittal
            slice_num = st.slider("Slice Number", 0, demo_data.shape[0]-1, 50)
            slice_data = demo_data[slice_num, :, :]
    
    with col2:
        fig = px.imshow(slice_data, 
                       color_continuous_scale='gray',
                       title=f'Demo {slice_type.capitalize()} Slice {slice_num}')
        st.plotly_chart(fig, use_container_width=True)

        hist_fig = px.histogram(x=slice_data.flatten(), 
                               title=f'Histogram - {slice_type.capitalize()} Slice {slice_num}',
                               nbins=50)
        st.plotly_chart(hist_fig, use_container_width=True)

def demo_eeg_analysis():
    
    st.subheader("🧠 EEG Analysis Demo")
    
    time, eeg_signal = create_demo_eeg_data()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**EEG Controls**")
        
        time_range = st.slider(
            "Time Range (seconds)",
            min_value=0.0,
            max_value=float(time[-1]),
            value=(0.0, min(5.0, float(time[-1]))),
            step=0.1
        )
        
        show_spectrum = st.checkbox("Show Power Spectrum", value=True)
    
    with col2:
        start_idx = int(time_range[0] * 256)
        end_idx = int(time_range[1] * 256)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time[start_idx:end_idx], 
                                y=eeg_signal[start_idx:end_idx], 
                                mode='lines', 
                                name='EEG Signal'))
        
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
            spectrum_fig.add_trace(go.Scatter(x=freqs, y=psd, mode='lines'))
            spectrum_fig.update_layout(
                title='Demo Power Spectral Density',
                xaxis_title='Frequency (Hz)',
                yaxis_title='Power (μV²/Hz)',
                height=400
            )
            
            st.plotly_chart(spectrum_fig, use_container_width=True)

def demo_statistics():
    
    st.subheader("📊 Statistical Analysis Demo")
    
    demo_data = create_demo_data()
    
    stats = {
        'Shape': demo_data.shape,
        'Data Type': demo_data.dtype,
        'Min Value': float(demo_data.min()),
        'Max Value': float(demo_data.max()),
        'Mean Value': float(demo_data.mean()),
        'Std Value': float(demo_data.std()),
        'Non-zero Voxels': int(np.count_nonzero(demo_data)),
        'Total Voxels': int(demo_data.size),
        'Memory Usage (MB)': float(demo_data.nbytes / (1024 * 1024))
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Statistics")
        for prop, value in stats.items():
            if prop not in ['Shape', 'Data Type']:
                if isinstance(value, float):
                    st.metric(prop, f"{value:.2f}")
                else:
                    st.metric(prop, f"{value:,}")
    
    with col2:
        st.subheader("Data Distribution")
        
        hist_fig = px.histogram(x=demo_data.flatten(), 
                               title='Distribution of All Voxel Values',
                               nbins=50)
        hist_fig.update_layout(height=400)
        st.plotly_chart(hist_fig, use_container_width=True)

def main():
    
    st.set_page_config(
        page_title="Medical Visualization Tool - Demo",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Advanced Medical Visualization Tool - Demo")
    st.markdown("### Interactive demonstration of key features")
    
    st.info("""
    This demo showcases the main features of the Advanced Medical Visualization Tool using synthetic data. 
    In the full application, you can upload your own NIfTI and EEG files for analysis.
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 3D Visualization", "🔍 Slice Analysis", "🧠 EEG Analysis", "📊 Statistics"])
    
    with tab1:
        demo_3d_visualization()
    
    with tab2:
        demo_slice_analysis()
    
    with tab3:
        demo_eeg_analysis()
    
    with tab4:
        demo_statistics()
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 Ready to use with your own data?
    
    To use the full application with your own medical data:
    
    1. **Upload NIfTI files** (as ZIP archives containing .nii or .nii.gz files)
    2. **Upload EEG files** (.edf format)
    3. **Explore the full feature set** including advanced preprocessing, segmentation, and ROI analysis
    
    **Run the full application:**
    ```bash
    python run_app.py
    ```
    """)

if __name__ == "__main__":
    main()
