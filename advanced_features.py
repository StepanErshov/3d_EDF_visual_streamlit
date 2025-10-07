import streamlit as st
import numpy as np
import nibabel as nib
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import mne
from scipy import ndimage, signal
import pandas as pd
from utils import *

def render_advanced_features():
    """Render advanced features page"""
    
    st.header("🔬 Advanced Analysis Features")
    
    # Сайдбар для выбора функций
    st.sidebar.subheader("Advanced Tools")
    feature = st.sidebar.selectbox(
        "Select Feature",
        [
            "Data Preprocessing",
            "Segmentation Analysis", 
            "ROI Analysis",
            "Multi-Modal Fusion",
            "EEG Advanced Analysis",
            "Export & Report"
        ]
    )
    
    if feature == "Data Preprocessing":
        render_data_preprocessing()
    elif feature == "Segmentation Analysis":
        render_segmentation_analysis()
    elif feature == "ROI Analysis":
        render_roi_analysis()
    elif feature == "Multi-Modal Fusion":
        render_multimodal_fusion()
    elif feature == "EEG Advanced Analysis":
        render_eeg_advanced_analysis()
    elif feature == "Export & Report":
        render_export_report()

def render_data_preprocessing():
    """Data preprocessing interface"""
    st.subheader("🛠️ Data Preprocessing")
    
    if 'nifti_data' not in st.session_state or st.session_state.nifti_data is None:
        st.warning("⚠️ Please load NIfTI data first")
        return
    
    data = st.session_state.nifti_data['data'].copy()
    original_data = st.session_state.nifti_data['data'].copy()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Preprocessing Options")
        
        # Нормализация
        normalize = st.checkbox("Apply Normalization", value=False)
        if normalize:
            norm_method = st.selectbox("Normalization Method", 
                                     ["minmax", "zscore", "robust"])
        
        # Фильтрация
        apply_filter = st.checkbox("Apply Filter", value=False)
        if apply_filter:
            filter_type = st.selectbox("Filter Type", 
                                     ["gaussian", "median", "bilateral"])
            
            if filter_type == "gaussian":
                sigma = st.slider("Gaussian Sigma", 0.1, 5.0, 1.0, 0.1)
            elif filter_type == "median":
                size = st.slider("Median Filter Size", 3, 15, 3, 2)
        
        # Морфологические операции
        morphology = st.checkbox("Apply Morphology", value=False)
        if morphology:
            morph_op = st.selectbox("Morphology Operation", 
                                  ["erosion", "dilation", "opening", "closing"])
            morph_size = st.slider("Structure Size", 1, 10, 3)
        
        if st.button("Apply Preprocessing"):
            # Применяем нормализацию
            if normalize:
                data = normalize_data(data, norm_method)
            
            # Применяем фильтр
            if apply_filter:
                if filter_type == "gaussian":
                    data = apply_filters(data, filter_type, sigma=sigma)
                elif filter_type == "median":
                    data = apply_filters(data, filter_type, size=size)
                else:
                    data = apply_filters(data, filter_type)
            
            # Применяем морфологические операции
            if morphology:
                if morph_op == "erosion":
                    data = ndimage.binary_erosion(data, structure=np.ones((morph_size,)*3))
                elif morph_op == "dilation":
                    data = ndimage.binary_dilation(data, structure=np.ones((morph_size,)*3))
                elif morph_op == "opening":
                    data = ndimage.binary_opening(data, structure=np.ones((morph_size,)*3))
                elif morph_op == "closing":
                    data = ndimage.binary_closing(data, structure=np.ones((morph_size,)*3))
            
            # Сохраняем обработанные данные
            st.session_state.processed_data = data
            st.success("✅ Preprocessing applied successfully!")
    
    with col2:
        if 'processed_data' in st.session_state:
            data = st.session_state.processed_data
        
        # Сравнение до и после
        st.subheader("Preprocessing Results")
        
        # Выбираем срез для отображения
        slice_type = st.selectbox("Slice Type", ["axial", "coronal", "sagittal"])
        
        if slice_type == "axial":
            slice_num = data.shape[2] // 2
            original_slice = original_data[:, :, slice_num]
            processed_slice = data[:, :, slice_num]
        elif slice_type == "coronal":
            slice_num = data.shape[1] // 2
            original_slice = original_data[:, slice_num, :]
            processed_slice = data[:, slice_num, :]
        else:  # sagittal
            slice_num = data.shape[0] // 2
            original_slice = original_data[slice_num, :, :]
            processed_slice = data[slice_num, :, :]
        
        # Создаем сравнение
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Original", "Processed"),
            specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}]]
        )
        
        fig.add_trace(go.Heatmap(z=original_slice, colorscale='gray', showscale=False), row=1, col=1)
        fig.add_trace(go.Heatmap(z=processed_slice, colorscale='gray', showscale=False), row=1, col=2)
        
        fig.update_layout(height=400, title_text="Preprocessing Comparison")
        st.plotly_chart(fig, use_container_width=True)

def render_segmentation_analysis():
    """Segmentation analysis interface"""
    st.subheader("🎯 Segmentation Analysis")
    
    if 'nifti_data' not in st.session_state or st.session_state.nifti_data is None:
        st.warning("⚠️ Please load NIfTI data first")
        return
    
    data = st.session_state.nifti_data['data']
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Segmentation Parameters")
        
        method = st.selectbox("Segmentation Method", 
                            ["threshold", "watershed", "region_growing"])
        
        if method == "threshold":
            threshold = st.slider("Threshold Value", 
                                float(data.min()), float(data.max()), 
                                float(np.percentile(data, 90)))
        
        if st.button("Perform Segmentation"):
            if method == "threshold":
                segmented = segment_regions(data, method, threshold=threshold)
            else:
                segmented = segment_regions(data, method)
            
            st.session_state.segmented_data = segmented
            st.success("✅ Segmentation completed!")
    
    with col2:
        if 'segmented_data' in st.session_state:
            segmented = st.session_state.segmented_data
            
            # Визуализация сегментации
            st.subheader("Segmentation Results")
            
            # Создаем 3D визуализацию сегментации
            fig = create_3d_surface_plot(segmented.astype(float), isovalue=0.5, opacity=0.8)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Статистики сегментации
            unique_labels = np.unique(segmented)
            st.subheader("Segmentation Statistics")
            
            stats_data = []
            for label in unique_labels:
                if label > 0:  # Исключаем фон
                    mask = segmented == label
                    volume = np.sum(mask)
                    stats_data.append({
                        'Label': int(label),
                        'Volume (voxels)': volume,
                        'Volume (mm³)': volume * 1.0,  # Предполагаем 1mm³ на воксель
                        'Percentage': volume / segmented.size * 100
                    })
            
            if stats_data:
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True)

def render_roi_analysis():
    """ROI analysis interface"""
    st.subheader("📍 Region of Interest (ROI) Analysis")
    
    if 'nifti_data' not in st.session_state or st.session_state.nifti_data is None:
        st.warning("⚠️ Please load NIfTI data first")
        return
    
    data = st.session_state.nifti_data['data']
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("ROI Selection")
        
        # Выбор координат ROI
        x_coord = st.slider("X Coordinate", 0, data.shape[0]-1, data.shape[0]//2)
        y_coord = st.slider("Y Coordinate", 0, data.shape[1]-1, data.shape[1]//2)
        z_coord = st.slider("Z Coordinate", 0, data.shape[2]-1, data.shape[2]//2)
        
        roi_size = st.slider("ROI Size", 5, 50, 10)
        
        if st.button("Analyze ROI"):
            roi_coords = (x_coord, y_coord, z_coord)
            roi_stats, roi_data = create_roi_analysis(data, roi_coords, roi_size)
            
            st.session_state.roi_stats = roi_stats
            st.session_state.roi_data = roi_data
            st.session_state.roi_coords = roi_coords
            
            st.success("✅ ROI analysis completed!")
    
    with col2:
        if 'roi_stats' in st.session_state:
            st.subheader("ROI Analysis Results")
            
            # Отображаем статистики ROI
            stats = st.session_state.roi_stats
            roi_data = st.session_state.roi_data
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Mean Value", f"{stats['mean']:.3f}")
                st.metric("Standard Deviation", f"{stats['std']:.3f}")
                st.metric("Min Value", f"{stats['min']:.3f}")
                st.metric("Max Value", f"{stats['max']:.3f}")
            
            with col_b:
                st.metric("ROI Volume", f"{stats['volume']} voxels")
                st.metric("Coordinates", f"({stats['coordinates'][0]}, {stats['coordinates'][1]}, {stats['coordinates'][2]})")
            
            # Визуализация ROI
            fig = px.imshow(roi_data[roi_data.shape[0]//2, :, :], 
                           color_continuous_scale='viridis',
                           title="ROI Slice View")
            st.plotly_chart(fig, use_container_width=True)

def render_multimodal_fusion():
    """Multi-modal data fusion interface"""
    st.subheader("🔗 Multi-Modal Data Fusion")
    
    if ('nifti_data' not in st.session_state or st.session_state.nifti_data is None or
        'eeg_data' not in st.session_state or st.session_state.eeg_data is None):
        st.warning("⚠️ Please load both NIfTI and EEG data")
        return
    
    st.info("💡 Multi-modal fusion features are under development")
    
    # Здесь можно добавить функционал для объединения данных разных модальностей
    # Например, корреляционный анализ между ЭЭГ и структурными данными

def render_eeg_advanced_analysis():
    """Advanced EEG analysis interface"""
    st.subheader("🧠 Advanced EEG Analysis")
    
    if 'eeg_data' not in st.session_state or st.session_state.eeg_data is None:
        st.warning("⚠️ Please load EEG data first")
        return
    
    raw = st.session_state.eeg_data
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Analysis Parameters")
        
        channel = st.selectbox("Select Channel", raw.ch_names)
        
        time_range = st.slider(
            "Analysis Time Range (seconds)",
            min_value=0.0,
            max_value=float(raw.times[-1]),
            value=(0.0, min(30.0, float(raw.times[-1]))),
            step=0.1
        )
        
        analysis_type = st.selectbox("Analysis Type",
                                   ["Spectral Analysis", "Time-Frequency Analysis", 
                                    "Connectivity Analysis", "Artifact Detection"])
        
        if st.button("Perform Analysis"):
            analysis_results = create_eeg_analysis(raw, channel, time_range)
            st.session_state.eeg_analysis = analysis_results
            st.success("✅ Analysis completed!")
    
    with col2:
        if 'eeg_analysis' in st.session_state:
            analysis = st.session_state.eeg_analysis
            
            st.subheader("EEG Analysis Results")
            
            # Статистики
            stats = analysis['stats']
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("Mean Amplitude", f"{stats['mean']:.3f} μV")
                st.metric("RMS", f"{stats['rms']:.3f} μV")
                st.metric("Peak-to-Peak", f"{stats['peak_to_peak']:.3f} μV")
            
            with col_b:
                st.metric("Standard Deviation", f"{stats['std']:.3f} μV")
                st.metric("Min Value", f"{stats['min']:.3f} μV")
                st.metric("Max Value", f"{stats['max']:.3f} μV")
            
            # Спектральный анализ
            st.subheader("Power Spectral Density")
            
            spectrum = analysis['spectrum']
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=spectrum['frequencies'], 
                y=spectrum['power'],
                mode='lines',
                name='PSD'
            ))
            
            fig.update_layout(
                title=f'Power Spectral Density - {channel}',
                xaxis_title='Frequency (Hz)',
                yaxis_title='Power (μV²/Hz)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Классификация ритмов
            st.subheader("EEG Rhythm Classification")
            
            rhythms = analysis['rhythms']
            rhythm_data = []
            for rhythm_name, rhythm_info in rhythms.items():
                if rhythm_info['power'] > 0:
                    rhythm_data.append({
                        'Rhythm': rhythm_name.upper(),
                        'Frequency Range': f"{rhythm_info['freq_range'][0]}-{rhythm_info['freq_range'][1]} Hz",
                        'Power': f"{rhythm_info['power']:.3f}",
                        'Peak Frequency': f"{rhythm_info['peak_freq']:.1f} Hz"
                    })
            
            if rhythm_data:
                rhythm_df = pd.DataFrame(rhythm_data)
                st.dataframe(rhythm_df, use_container_width=True)

def render_export_report():
    """Export and report generation interface"""
    st.subheader("📊 Export & Report Generation")
    
    if ('nifti_data' not in st.session_state or st.session_state.nifti_data is None):
        st.warning("⚠️ Please load data first")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Options")
        
        export_format = st.selectbox("Export Format", 
                                   ["PNG", "HTML", "PDF", "CSV"])
        
        include_statistics = st.checkbox("Include Statistics", value=True)
        include_visualizations = st.checkbox("Include Visualizations", value=True)
        
        if st.button("Generate Report"):
            st.success("✅ Report generation started!")
    
    with col2:
        st.subheader("Available Data for Export")
        
        available_data = []
        
        if 'nifti_data' in st.session_state:
            available_data.append("NIfTI Data")
        
        if 'processed_data' in st.session_state:
            available_data.append("Processed Data")
        
        if 'segmented_data' in st.session_state:
            available_data.append("Segmented Data")
        
        if 'roi_stats' in st.session_state:
            available_data.append("ROI Statistics")
        
        if 'eeg_data' in st.session_state:
            available_data.append("EEG Data")
        
        if 'eeg_analysis' in st.session_state:
            available_data.append("EEG Analysis")
        
        if available_data:
            for data_type in available_data:
                st.write(f"✅ {data_type}")
        else:
            st.write("No data available for export")

# Функция для запуска расширенных функций
def run_advanced_features():
    """Main function to run advanced features"""
    render_advanced_features()
