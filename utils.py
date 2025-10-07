import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from skimage import measure, filters, morphology
import mne
from scipy import ndimage, signal
import tempfile
import os

def normalize_data(data, method='minmax'):
    if method == 'minmax':
        return (data - data.min()) / (data.max() - data.min())
    elif method == 'zscore':
        return (data - data.mean()) / data.std()
    elif method == 'robust':
        q75, q25 = np.percentile(data, [75, 25])
        iqr = q75 - q25
        median = np.median(data)
        return (data - median) / iqr
    else:
        return data

def apply_filters(data, filter_type='gaussian', **kwargs):

    if filter_type == 'gaussian':
        sigma = kwargs.get('sigma', 1.0)
        return filters.gaussian(data, sigma=sigma)
    elif filter_type == 'median':
        size = kwargs.get('size', 3)
        return filters.median(data, size=size)
    elif filter_type == 'bilateral':
        sigma_color = kwargs.get('sigma_color', 0.05)
        sigma_spatial = kwargs.get('sigma_spatial', 1.0)
        return filters.bilateral(data, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
    else:
        return data

def create_volume_rendering(data, opacity_function='linear', colormap='viridis'):

    data_norm = normalize_data(data)

    fig = go.Figure(data=go.Volume(
        x=np.arange(data.shape[0]),
        y=np.arange(data.shape[1]),
        z=np.arange(data.shape[2]),
        value=data_norm.flatten(),
        opacity=0.1,
        colorscale=colormap,
        slices_z=dict(show=True, locations=[data.shape[2]//2]),
        slices_y=dict(show=True, locations=[data.shape[1]//2]),
        slices_x=dict(show=True, locations=[data.shape[0]//2]),
        surface_count=20
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z'
        ),
        title="Volume Rendering"
    )
    
    return fig

def segment_regions(data, method='threshold', **kwargs):

    if method == 'threshold':
        threshold = kwargs.get('threshold', np.percentile(data, 90))
        return data > threshold
    elif method == 'watershed':
        from skimage.segmentation import watershed
        from skimage.feature import peak_local_maxima
        
        local_maxima = peak_local_maxima(data, min_distance=20, threshold_abs=np.percentile(data, 80))
        markers = np.zeros_like(data)
        for i, (x, y, z) in enumerate(local_maxima):
            markers[x, y, z] = i + 1
        
        return watershed(-data, markers)
    else:
        return data

def compute_statistics(data):
    stats = {
        'basic': {
            'shape': data.shape,
            'dtype': data.dtype,
            'size': data.size,
            'min': float(data.min()),
            'max': float(data.max()),
            'mean': float(data.mean()),
            'std': float(data.std()),
            'median': float(np.median(data)),
            'percentiles': {
                '25th': float(np.percentile(data, 25)),
                '75th': float(np.percentile(data, 75)),
                '90th': float(np.percentile(data, 90)),
                '95th': float(np.percentile(data, 95)),
                '99th': float(np.percentile(data, 99))
            }
        },
        'spatial': {
            'center_of_mass': ndimage.center_of_mass(data),
            'moment_of_inertia': ndimage.moment(data, order=2),
            'volume': np.count_nonzero(data),
            'surface_area': compute_surface_area(data)
        }
    }
    
    return stats

def compute_surface_area(data, threshold=None):
    if threshold is None:
        threshold = np.percentile(data, 90)
    
    binary_data = data > threshold
    verts, faces, _, _ = measure.marching_cubes(binary_data, level=0.5)

    surface_area = 0
    for face in faces:
        v1, v2, v3 = verts[face]
        area = 0.5 * np.linalg.norm(np.cross(v2 - v1, v3 - v1))
        surface_area += area
    
    return surface_area

def create_roi_analysis(data, roi_coords, roi_size=10):
    x, y, z = roi_coords

    roi_data = data[
        max(0, x-roi_size):min(data.shape[0], x+roi_size),
        max(0, y-roi_size):min(data.shape[1], y+roi_size),
        max(0, z-roi_size):min(data.shape[2], z+roi_size)
    ]
    
    roi_stats = {
        'mean': float(roi_data.mean()),
        'std': float(roi_data.std()),
        'min': float(roi_data.min()),
        'max': float(roi_data.max()),
        'volume': roi_data.size,
        'coordinates': roi_coords
    }
    
    return roi_stats, roi_data

def create_eeg_analysis(raw, channel_name, time_range=None):
    channel_idx = raw.ch_names.index(channel_name)
    
    if time_range is not None:
        start_time, end_time = time_range
        start_idx = raw.time_as_index(start_time)[0]
        end_idx = raw.time_as_index(end_time)[0]
        data = raw[channel_idx, start_idx:end_idx][0][0]
        times = raw.times[start_idx:end_idx]
    else:
        data = raw[channel_idx, :][0][0]
        times = raw.times
    
    stats = {
        'mean': float(np.mean(data)),
        'std': float(np.std(data)),
        'min': float(np.min(data)),
        'max': float(np.max(data)),
        'rms': float(np.sqrt(np.mean(data**2))),
        'peak_to_peak': float(np.max(data) - np.min(data))
    }

    freqs, psd = signal.welch(data, fs=raw.info['sfreq'], nperseg=1024)
    
    peak_indices = signal.find_peaks(psd, height=np.max(psd)*0.1)[0]
    dominant_freqs = freqs[peak_indices]
    dominant_powers = psd[peak_indices]

    rhythm_classification = classify_eeg_rhythms(freqs, psd)
    
    analysis_results = {
        'stats': stats,
        'spectrum': {
            'frequencies': freqs,
            'power': psd,
            'dominant_frequencies': dominant_freqs,
            'dominant_powers': dominant_powers
        },
        'rhythms': rhythm_classification,
        'channel': channel_name,
        'sampling_rate': raw.info['sfreq'],
        'duration': float(times[-1] - times[0])
    }
    
    return analysis_results

def classify_eeg_rhythms(freqs, psd):
    delta_mask = (freqs >= 0.5) & (freqs <= 4)
    theta_mask = (freqs > 4) & (freqs <= 8)
    alpha_mask = (freqs > 8) & (freqs <= 13)
    beta_mask = (freqs > 13) & (freqs <= 30)
    gamma_mask = (freqs > 30) & (freqs <= 100)
    
    rhythms = {
        'delta': {
            'freq_range': (0.5, 4),
            'power': float(np.sum(psd[delta_mask])),
            'peak_freq': float(freqs[delta_mask][np.argmax(psd[delta_mask])]) if np.any(delta_mask) else 0
        },
        'theta': {
            'freq_range': (4, 8),
            'power': float(np.sum(psd[theta_mask])),
            'peak_freq': float(freqs[theta_mask][np.argmax(psd[theta_mask])]) if np.any(theta_mask) else 0
        },
        'alpha': {
            'freq_range': (8, 13),
            'power': float(np.sum(psd[alpha_mask])),
            'peak_freq': float(freqs[alpha_mask][np.argmax(psd[alpha_mask])]) if np.any(alpha_mask) else 0
        },
        'beta': {
            'freq_range': (13, 30),
            'power': float(np.sum(psd[beta_mask])),
            'peak_freq': float(freqs[beta_mask][np.argmax(psd[beta_mask])]) if np.any(beta_mask) else 0
        },
        'gamma': {
            'freq_range': (30, 100),
            'power': float(np.sum(psd[gamma_mask])),
            'peak_freq': float(freqs[gamma_mask][np.argmax(psd[gamma_mask])]) if np.any(gamma_mask) else 0
        }
    }
    
    return rhythms

def export_visualization(fig, filename, format='html'):
    if format == 'html':
        fig.write_html(filename)
    elif format == 'png':
        fig.write_image(filename, width=1200, height=800)
    elif format == 'pdf':
        fig.write_image(filename, format='pdf', width=1200, height=800)
    
    return filename

def create_comparison_plot(data1, data2, title1="Dataset 1", title2="Dataset 2"):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(title1, title2),
        specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}]]
    )
    
    slice1 = data1[:, :, data1.shape[2]//2]
    slice2 = data2[:, :, data2.shape[2]//2]
    
    fig.add_trace(go.Heatmap(z=slice1, colorscale='gray', showscale=False), row=1, col=1)
    fig.add_trace(go.Heatmap(z=slice2, colorscale='gray', showscale=False), row=1, col=2)
    
    fig.update_layout(height=600, title_text="Data Comparison")
    
    return fig
