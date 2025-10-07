import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import streamlit as st
import sys
import tempfile
import shutil
from pathlib import Path

st.set_page_config(
    page_title="Advanced Medical Visualization Tool",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from pages import *
from advanced_features import run_advanced_features

def main():

    initialize_session_state()

    st.sidebar.title("🧠 Medical Visualization Tool")
    st.sidebar.markdown("---")

    page = st.sidebar.selectbox(
        "Navigate to:",
        [
            "🏠 Home - Data Upload & Overview",
            "🎨 3D Visualization", 
            "🔍 Slice Analysis",
            "🧠 EEG Analysis",
            "📊 Statistics",
            "🔬 Advanced Features"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 About")
    st.sidebar.markdown("""
    This tool provides comprehensive medical data visualization and analysis capabilities:
    
    **Features:**
    - NIfTI 3D visualization
    - Slice analysis
    - EEG processing
    - Statistical analysis
    - Advanced preprocessing
    - ROI analysis
    - Segmentation tools
    
    **Supported Formats:**
    - NIfTI (.nii, .nii.gz)
    - EDF (EEG data)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Data Status")
    
    data_status = []
    if st.session_state.get('data_dir') and os.path.exists(st.session_state.data_dir):
        data_status.append("✅ NIfTI Data")
    else:
        data_status.append("❌ No NIfTI Data")
    
    if st.session_state.get('eeg_data'):
        data_status.append("✅ EEG Data")
    else:
        data_status.append("❌ No EEG Data")
    
    for status in data_status:
        st.sidebar.markdown(status)
    
    if "Home" in page:
        render_home_page()
    elif "3D Visualization" in page:
        render_3d_visualization_page()
    elif "Slice Analysis" in page:
        render_slice_analysis_page()
    elif "EEG Analysis" in page:
        render_eeg_analysis_page()
    elif "Statistics" in page:
        render_statistics_page()
    elif "Advanced Features" in page:
        run_advanced_features()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>Advanced Medical Visualization Tool</strong></p>
        <p>Built with Streamlit, Plotly, Nibabel, MNE-Python, and Scikit-image</p>
        <p>© 2024 - Medical Data Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)

def render_home_page():
    """Render the home page with data upload functionality"""
    st.title("🏠 Home - Data Upload & Overview")
    st.markdown("### Welcome to the Advanced Medical Visualization Tool")
    
    render_upload_overview_page()

def render_3d_visualization_page():
    st.title("🎨 3D Visualization")
    
    if 'nifti_data' not in st.session_state or st.session_state.nifti_data is None:
        st.warning("⚠️ Please upload and load a NIfTI file first")
        st.info("Go to the Home page to upload your data")
        return

    render_3d_visualization_content()

def render_slice_analysis_page():
    st.title("🔍 Slice Analysis")
    
    if 'nifti_data' not in st.session_state or st.session_state.nifti_data is None:
        st.warning("⚠️ Please upload and load a NIfTI file first")
        st.info("Go to the Home page to upload your data")
        return
    
    render_slice_analysis_content()

def render_eeg_analysis_page():
    st.title("🧠 EEG Analysis")
    
    if 'eeg_data' not in st.session_state or st.session_state.eeg_data is None:
        st.warning("⚠️ Please upload an EEG file first")
        st.info("Go to the Home page to upload your data")
        return
    
    render_eeg_analysis_content()

def render_statistics_page():
    st.title("📊 Statistical Analysis")
    
    if 'nifti_data' not in st.session_state or st.session_state.nifti_data is None:
        st.warning("⚠️ Please upload and load a NIfTI file first")
        st.info("Go to the Home page to upload your data")
        return
    
    render_statistics_content()

def cleanup_temp_files():
    if 'data_dir' in st.session_state and st.session_state.data_dir:
        if os.path.exists(st.session_state.data_dir):
            shutil.rmtree(st.session_state.data_dir)
    
    temp_files = list(Path('.').glob('temp_*'))
    for temp_file in temp_files:
        if temp_file.is_file():
            temp_file.unlink()
        elif temp_file.is_dir():
            shutil.rmtree(temp_file)

import atexit
atexit.register(cleanup_temp_files)

if __name__ == "__main__":
    main()
