"""
Page content functions for the Advanced Medical Visualization Tool
"""

import streamlit as st
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import tempfile
import zipfile
from glob import glob
import random
import string
import shutil
import os
import mne
from skimage import measure
import pandas as pd
from utils import *

def render_upload_overview_page():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload NIfTI Files (ZIP)")
        uploaded_nifti = st.file_uploader("Choose a ZIP file with NIfTI files", type=['zip'], key="nifti_upload")
        
        if uploaded_nifti is not None:
            if (st.session_state.uploaded_file != uploaded_nifti.name or 
                st.session_state.data_dir is None):
                
                if does_zip_have_nifti(uploaded_nifti):
                    data_dir = f'./temp_data_{get_random_string(10)}'
                    
                    if extract_zip(uploaded_nifti, data_dir):
                        st.session_state.data_dir = data_dir
                        st.session_state.uploaded_file = uploaded_nifti.name
                        st.success("✅ NIfTI files uploaded and extracted successfully!")
                    else:
                        st.error("❌ Failed to extract ZIP file")
                else:
                    st.error("❌ No NIfTI files found in the ZIP archive")
    
    with col2:
        st.subheader("Upload EEG Files (EDF)")
        uploaded_eeg = st.file_uploader("Choose an EDF file", type=['edf'], key="eeg_upload")
        
        if uploaded_eeg is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.edf') as tmp_file:
                tmp_file.write(uploaded_eeg.getvalue())
                tmp_path = tmp_file.name
            
            try:
                eeg_data = load_eeg_data(tmp_path)
                if eeg_data is not None:
                    st.session_state.eeg_data = eeg_data
                    st.success("✅ EEG data loaded successfully!")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    if st.session_state.data_dir and os.path.exists(st.session_state.data_dir):
        nifti_files = glob(f'{st.session_state.data_dir}/**/*.nii.gz', recursive=True) + \
                     glob(f'{st.session_state.data_dir}/**/*.nii', recursive=True)
        
        if nifti_files:
            st.subheader("📊 Available NIfTI Files")
            selected_file = st.selectbox("Select a file to analyze", nifti_files)
            
            if st.button("Load File"):
                data, header, affine = load_nifti_file(selected_file)
                if data is not None:
                    st.session_state.nifti_data = {
                        'data': data,
                        'header': header,
                        'affine': affine,
                        'file_path': selected_file
                    }
                    st.success("✅ File loaded successfully!")

                    stats = analyze_volume_statistics(data)
                    st.subheader("📈 Volume Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Shape", f"{stats['Shape']}")
                        st.metric("Min Value", f"{stats['Min Value']:.2f}")
                        st.metric("Max Value", f"{stats['Max Value']:.2f}")
                    with col2:
                        st.metric("Mean Value", f"{stats['Mean Value']:.2f}")
                        st.metric("Std Value", f"{stats['Std Value']:.2f}")
                        st.metric("Non-zero Voxels", f"{stats['Non-zero Voxels']:,}")
                    with col3:
                        st.metric("Total Voxels", f"{stats['Total Voxels']:,}")
                        st.metric("Memory Usage", f"{stats['Memory Usage (MB)']:.1f} MB")
    
    if st.session_state.eeg_data is not None:
        st.subheader("🧠 EEG Data Overview")
        raw = st.session_state.eeg_data
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Channels:** {len(raw.ch_names)}")
            st.write(f"**Sampling Rate:** {raw.info['sfreq']} Hz")
            st.write(f"**Duration:** {raw.times[-1]:.1f} seconds")
        
        with col2:
            st.write("**Channel Names:**")
            for i, ch in enumerate(raw.ch_names):
                st.write(f"{i+1}. {ch}")

def render_3d_visualization_content():
    
    if st.session_state.nifti_data is not None:
        data = st.session_state.nifti_data['data']
        file_path = st.session_state.nifti_data['file_path']
        
        st.subheader(f"Visualizing: {os.path.basename(file_path)}")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Controls")
            
            visualization_type = st.selectbox(
                "Visualization Type",
                ["3D Surface", "Volume Rendering", "Orthogonal Slices"]
            )
            
            if visualization_type == "3D Surface":
                isovalue = st.slider("Isosurface Value", 0.0, 1.0, 0.5, 0.01)
                opacity = st.slider("Opacity", 0.0, 1.0, 0.7, 0.1)
            
            if st.button("Generate Visualization"):
                with st.spinner("Creating 3D visualization..."):
                    if visualization_type == "3D Surface":
                        fig = create_3d_surface_plot(data, isovalue, opacity)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif visualization_type == "Orthogonal Slices":
                        fig = create_orthogonal_slices(data)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif visualization_type == "Volume Rendering":
                        threshold = np.percentile(data, 95)
                        x, y, z = np.where(data > threshold)
                        
                        fig = go.Figure(data=[go.Scatter3d(
                            x=x[::1000],
                            y=y[::1000],
                            z=z[::1000],
                            mode='markers',
                            marker=dict(
                                size=2,
                                color=data[x[::1000], y[::1000], z[::1000]],
                                colorscale='viridis',
                                opacity=0.6
                            )
                        )])
                        
                        fig.update_layout(
                            scene=dict(
                                xaxis_title='X',
                                yaxis_title='Y',
                                zaxis_title='Z'
                            ),
                            title="Volume Rendering (Simplified)"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.info("💡 Use the controls on the left to customize your visualization")

def render_slice_analysis_content():
    
    if st.session_state.nifti_data is not None:
        data = st.session_state.nifti_data['data']
        file_path = st.session_state.nifti_data['file_path']
        
        st.subheader(f"Analyzing: {os.path.basename(file_path)}")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Slice Controls")
            
            slice_type = st.selectbox("Slice Type", ["axial", "coronal", "sagittal"])
            
            if slice_type == "axial":
                slice_num = st.slider("Slice Number", 0, data.shape[2]-1, data.shape[2]//2)
            elif slice_type == "coronal":
                slice_num = st.slider("Slice Number", 0, data.shape[1]-1, data.shape[1]//2)
            else:  # sagittal
                slice_num = st.slider("Slice Number", 0, data.shape[0]-1, data.shape[0]//2)
            
            show_histogram = st.checkbox("Show Histogram", value=True)
            show_orthogonal = st.checkbox("Show Orthogonal View", value=False)
        
        with col2:
            if slice_type == "axial":
                slice_data = data[:, :, slice_num]
            elif slice_type == "coronal":
                slice_data = data[:, slice_num, :]
            else:  # sagittal
                slice_data = data[slice_num, :, :]
            
            fig = px.imshow(slice_data, 
                           color_continuous_scale='gray',
                           title=f'{slice_type.capitalize()} Slice {slice_num}')
            st.plotly_chart(fig, use_container_width=True)
            
            if show_histogram:
                hist_fig = px.histogram(x=slice_data.flatten(), 
                                       title=f'Histogram - {slice_type.capitalize()} Slice {slice_num}',
                                       nbins=50)
                st.plotly_chart(hist_fig, use_container_width=True)

            if show_orthogonal:
                ortho_fig = create_orthogonal_slices(data)
                st.plotly_chart(ortho_fig, use_container_width=True)

def render_eeg_analysis_content():
    
    if st.session_state.eeg_data is not None:
        raw = st.session_state.eeg_data
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("EEG Controls")
            
            channel = st.selectbox("Select Channel", raw.ch_names)
            
            time_range = st.slider(
                "Time Range (seconds)",
                min_value=0.0,
                max_value=float(raw.times[-1]),
                value=(0.0, min(10.0, float(raw.times[-1]))),
                step=0.1
            )
            
            show_spectrum = st.checkbox("Show Power Spectrum", value=False)
        
        with col2:
            eeg_fig = create_eeg_plot(raw, channel, time_range)
            st.plotly_chart(eeg_fig, use_container_width=True)

            if show_spectrum:
                try:
                    channel_idx = raw.ch_names.index(channel)
                    data, times = raw[channel_idx, :]
                    
                    from scipy import signal
                    freqs, psd = signal.welch(data[0], fs=raw.info['sfreq'], nperseg=1024)
                    
                    spectrum_fig = go.Figure()
                    spectrum_fig.add_trace(go.Scatter(x=freqs, y=psd, mode='lines'))
                    spectrum_fig.update_layout(
                        title=f'Power Spectral Density - {channel}',
                        xaxis_title='Frequency (Hz)',
                        yaxis_title='Power (μV²/Hz)',
                        height=400
                    )
                    
                    st.plotly_chart(spectrum_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error computing spectrum: {e}")

def render_statistics_content():
    
    if st.session_state.nifti_data is not None:
        data = st.session_state.nifti_data['data']
        file_path = st.session_state.nifti_data['file_path']
        
        st.subheader(f"Statistics for: {os.path.basename(file_path)}")
        
        stats = analyze_volume_statistics(data)
        
        stats_df = pd.DataFrame(list(stats.items()), columns=['Property', 'Value'])
        
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
            
            hist_fig = px.histogram(x=data.flatten(), 
                                   title='Distribution of All Voxel Values',
                                   nbins=100)
            hist_fig.update_layout(height=400)
            st.plotly_chart(hist_fig, use_container_width=True)
        
        st.subheader("Spatial Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mean_x = np.mean(data, axis=(1, 2))
            fig_x = px.line(y=mean_x, title='Mean along X-axis')
            st.plotly_chart(fig_x, use_container_width=True)
        
        with col2:
            mean_y = np.mean(data, axis=(0, 2))
            fig_y = px.line(y=mean_y, title='Mean along Y-axis')
            st.plotly_chart(fig_y, use_container_width=True)
        
        with col3:
            mean_z = np.mean(data, axis=(0, 1))
            fig_z = px.line(y=mean_z, title='Mean along Z-axis')
            st.plotly_chart(fig_z, use_container_width=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'data_dir' not in st.session_state:
        st.session_state.data_dir = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'nifti_data' not in st.session_state:
        st.session_state.nifti_data = None
    if 'eeg_data' not in st.session_state:
        st.session_state.eeg_data = None

def get_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def does_zip_have_nifti(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(('.nii.gz', '.nii')):
                    return True
        return False
    except:
        return False
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

def extract_zip(uploaded_file, extract_path):
    os.makedirs(extract_path, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    try:
        with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        return True
    except Exception as e:
        st.error(f"Error extracting zip: {e}")
        return False
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

def load_nifti_file(file_path):
    try:
        nii_img = nib.load(file_path)
        data = nii_img.get_fdata()
        header = nii_img.header
        affine = nii_img.affine
        return data, header, affine
    except Exception as e:
        st.error(f"Error loading NIfTI file: {e}")
        return None, None, None

def load_eeg_data(file_path):
    try:
        raw = mne.io.read_raw_edf(file_path, preload=True)
        return raw
    except Exception as e:
        st.error(f"Error loading EEG data: {e}")
        return None

def create_eeg_plot(raw, channel_name=None, time_range=None):
    if channel_name is None:
        channel_name = raw.ch_names[0]
    
    channel_idx = raw.ch_names.index(channel_name)
    data, times = raw[channel_idx, :]
    
    if time_range is not None:
        start_time, end_time = time_range
        start_idx = np.where(times >= start_time)[0][0]
        end_idx = np.where(times <= end_time)[0][-1]
        data = data[0, start_idx:end_idx]
        times = times[start_idx:end_idx]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=data[0], mode='lines', name=channel_name))
    
    fig.update_layout(
        title=f'EEG Signal - {channel_name}',
        xaxis_title='Time (s)',
        yaxis_title='Amplitude (μV)',
        height=400
    )
    
    return fig

def create_3d_surface_plot(data, isovalue=0.5, opacity=0.7):
    try:
        data_norm = (data - data.min()) / (data.max() - data.min())
        
        verts, faces, _, _ = measure.marching_cubes(data_norm, level=isovalue)
        
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
                zaxis_title='Z',
                aspectmode='data'
            ),
            title="3D Surface Visualization",
            showlegend=True
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating 3D surface: {e}")
        return None

def create_orthogonal_slices(data):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Axial', 'Coronal', 'Sagittal', '3D View'),
        specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}],
               [{'type': 'heatmap'}, {'type': 'scatter3d'}]]
    )
    
    # Axial slice
    axial_slice = data[:, :, data.shape[2]//2]
    fig.add_trace(go.Heatmap(z=axial_slice, colorscale='gray', showscale=False), row=1, col=1)
    
    # Coronal slice
    coronal_slice = data[:, data.shape[1]//2, :]
    fig.add_trace(go.Heatmap(z=coronal_slice, colorscale='gray', showscale=False), row=1, col=2)
    
    # Sagittal slice
    sagittal_slice = data[data.shape[0]//2, :, :]
    fig.add_trace(go.Heatmap(z=sagittal_slice, colorscale='gray', showscale=False), row=2, col=1)
    
    # 3D scatter (simplified)
    x, y, z = np.where(data > np.percentile(data, 95))
    fig.add_trace(go.Scatter3d(x=x[::100], y=y[::100], z=z[::100], 
                              mode='markers', marker=dict(size=2)), row=2, col=2)
    
    fig.update_layout(height=800, title_text="Orthogonal Views")
    return fig

def analyze_volume_statistics(data):
    """Анализирует статистики объемных данных"""
    stats = {
        'Shape': data.shape,
        'Data Type': data.dtype,
        'Min Value': float(data.min()),
        'Max Value': float(data.max()),
        'Mean Value': float(data.mean()),
        'Std Value': float(data.std()),
        'Non-zero Voxels': int(np.count_nonzero(data)),
        'Total Voxels': int(data.size),
        'Memory Usage (MB)': float(data.nbytes / (1024 * 1024))
    }
    return stats
