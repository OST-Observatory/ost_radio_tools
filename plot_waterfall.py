#!/usr/bin/env python3
"""
Plot waterfall diagram from binary data file.
This script visualizes the frequency spectrum over time,
showing how the signal power varies across different frequencies.

Usage:
    ./plot_waterfall.py <input_file> [options]

The input file should be a binary file containing power spectrum data.

Options:
    --output, -o: Output file for the plot (default: waterfall_plot_<input>.png)
    --sampling-rate, -s: Sampling rate in Hz (default: extracted from filename)
    --center-frequency, -f: Center frequency (default: extracted from filename)
    --normalize, -n: Normalization method for the data (default: none)
        Options:
        - 'none': No normalization
        - 'global': Normalize to global min/max
        - 'row': Normalize each time step (row) independently
        - 'column': Normalize each frequency bin (column) independently
        - 'zscore': Z-score normalization (subtract mean, divide by std)
    --colormap, -c: Colormap for the plot (default: 'viridis')
    --vmin, -v: Minimum value for color scaling (default: auto)
    --vmax, -V: Maximum value for color scaling (default: auto)
    --log, -l: Use logarithmic scaling (default: False)
    --input-type, -t: Type of input data (default: 'power')
        Options:
        - 'amplitude': Input data represents amplitudes
        - 'power': Input data represents power values
    --show-power, -p: Convert amplitude data to power (only relevant for amplitude input)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional
import argparse
import os
import re
from datetime import datetime

def parse_filename(filename: str) -> Tuple[Optional[int], Optional[str], Optional[datetime]]:
    """Extract sampling rate, center frequency, and start time from filename."""
    match = re.search(r'_(\d+)_fc_', filename)
    if match:
        sampling_rate = int(match.group(1))
    else:
        sampling_rate = None

    match = re.search(r'_(\d+)_\d+_fc_', filename)
    if match:
        center_frequency = match.group(1)
    else:
        center_frequency = None

    match = re.search(r'gqrx_(\d{8})_(\d{6})', filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        try:
            start_time = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
        except ValueError:
            start_time = None
    else:
        start_time = None

    return sampling_rate, center_frequency, start_time

def normalize_data(data: np.ndarray, method: str) -> np.ndarray:
    """Normalize the data using the specified method.
    
    Args:
        data: Input data array
        method: Normalization method ('none', 'global', 'row', 'column', 'zscore')
    
    Returns:
        Normalized data array
    """
    if method == 'none':
        return data
    elif method == 'global':
        return (data - np.min(data)) / (np.max(data) - np.min(data))
    elif method == 'row':
        # Normalize each time step (row) independently
        row_mins = np.min(data, axis=1, keepdims=True)
        row_maxs = np.max(data, axis=1, keepdims=True)
        return (data - row_mins) / (row_maxs - row_mins)
    elif method == 'column':
        # Normalize each frequency bin (column) independently
        col_mins = np.min(data, axis=0, keepdims=True)
        col_maxs = np.max(data, axis=0, keepdims=True)
        return (data - col_mins) / (col_maxs - col_mins)
    elif method == 'zscore':
        # Z-score normalization
        mean = np.mean(data)
        std = np.std(data)
        return (data - mean) / std
    else:
        raise ValueError(f"Unknown normalization method: {method}")

def process_data(data: np.ndarray, input_type: str, use_log: bool, show_power: bool) -> Tuple[np.ndarray, str]:
    """Process the data based on input type and scaling.
    
    Args:
        data: Input data array
        input_type: Type of input data ('amplitude' or 'power')
        use_log: Whether to use logarithmic scaling
        show_power: Whether to convert amplitude to power
    
    Returns:
        Tuple of (processed data array, unit label)
    """
    unit = 'Power'
    
    # Convert amplitude to power if necessary
    if input_type == 'amplitude' and show_power:
        data = np.square(data)
        unit = 'Power'
    elif input_type == 'amplitude':
        unit = 'Amplitude'
    
    # Apply logarithmic scaling if requested
    if use_log:
        # Add small offset to avoid log(0)
        data = np.log10(data + 1e-10)
        unit += ' (dB)'
    
    return data, unit

def plot_waterfall(
    input_file: str,
    output_file: Optional[str] = None,
    sampling_rate: Optional[int] = None,
    center_frequency: Optional[str] = None,
    normalize: str = 'none',
    colormap: str = 'viridis',
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    use_log: bool = False,
    input_type: str = 'power',
    show_power: bool = False
) -> None:
    """Plot waterfall diagram from binary data file.
    
    Args:
        input_file: Path to the input file containing power spectrum data
        output_file: Path for the output plot file (default: waterfall_plot_<input>.png)
        sampling_rate: Sampling rate in Hz (default: extracted from filename)
        center_frequency: Center frequency in Hz (default: extracted from filename)
        normalize: Normalization method for the data
        colormap: Colormap for the plot
        vmin: Minimum value for color scaling
        vmax: Maximum value for color scaling
        use_log: Whether to use logarithmic scaling
        input_type: Type of input data ('amplitude' or 'power')
        show_power: Whether to convert amplitude to power
    """
    # Load data
    data = np.fromfile(input_file, dtype=np.float32)
    
    # If sampling_rate not provided, try to get it from filename
    if sampling_rate is None:
        sampling_rate, _, _ = parse_filename(input_file)
        if sampling_rate is None:
            print("Warning: Could not determine sampling rate from filename. Using default value of 1 Hz.")
            sampling_rate = 1
            
    # Reshape data into 2D array (time vs frequency)
    n_freq_bins = sampling_rate
    n_time_steps = len(data) // n_freq_bins
    data = data[:len(data)].reshape(n_time_steps, n_freq_bins)

    # Process data (convert amplitude to power if needed, apply log scaling)
    data, unit = process_data(data, input_type, use_log, show_power)

    # Normalize data
    data = normalize_data(data, normalize)

    # Create plot
    plt.figure(figsize=(12, 8))
    
    # If center frequency not provided, try to get it from filename
    if center_frequency is None:
        _, center_frequency, _ = parse_filename(input_file)
        if center_frequency is None:
            print("Warning: Could not determine center frequency from filename. Using default value of 1 Hz.")
            center_frequency = None

    # Calculate frequency axis
    freq_axis = np.linspace(-sampling_rate/2, sampling_rate/2, n_freq_bins)
    if center_frequency:
        freq_axis += int(center_frequency)
    
    # Plot waterfall
    plt.imshow(data, 
              aspect='auto',
              origin='lower',
              extent=[freq_axis[0], freq_axis[-1], 0, n_time_steps],
              cmap=colormap,
              vmin=vmin,
              vmax=vmax)
    
    plt.colorbar(label=unit)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Time (s)')
    
    # Add center frequency and scaling info to title
    title_parts = ['Waterfall Plot']
    if center_frequency:
        title_parts.append(f'Center Frequency: {center_frequency} Hz')
    if use_log:
        title_parts.append('Logarithmic Scale')
    if input_type == 'amplitude':
        if show_power:
            title_parts.append('Amplitude Input (Converted to Power)')
        else:
            title_parts.append('Amplitude Input')
    plt.title(' | '.join(title_parts))

    # Save plot
    if output_file is None:
        output_file = f'waterfall_plot_{os.path.splitext(os.path.basename(input_file))[0]}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

def main() -> None:
    """Main function to parse command line arguments and create the plot."""
    parser = argparse.ArgumentParser(description='Plot waterfall diagram from binary data file')
    parser.add_argument('input_file', help='Input file containing power spectrum data')
    parser.add_argument('--output', '-o', help='Output file for the plot (default: waterfall_plot_<input>.png)')
    parser.add_argument('--sampling-rate', '-s', type=int, help='Sampling rate in Hz (default: extracted from filename)')
    parser.add_argument('--center-frequency', '-f', help='Center frequency (default: extracted from filename)')
    parser.add_argument('--normalize', '-n', choices=['none', 'global', 'row', 'column', 'zscore'],
                      default='none', help='Normalization method for the data')
    parser.add_argument('--colormap', '-c', default='viridis', help='Colormap for the plot')
    parser.add_argument('--vmin', '-v', type=float, help='Minimum value for color scaling')
    parser.add_argument('--vmax', '-V', type=float, help='Maximum value for color scaling')
    parser.add_argument('--log', '-l', action='store_true', help='Use logarithmic scaling')
    parser.add_argument('--input-type', '-t', choices=['amplitude', 'power'],
                      default='power', help='Type of input data')
    parser.add_argument('--show-power', '-p', action='store_true',
                      help='Convert amplitude data to power (only relevant for amplitude input)')
    
    args = parser.parse_args()
    
    plot_waterfall(
        args.input_file,
        args.output,
        args.sampling_rate,
        args.center_frequency,
        args.normalize,
        args.colormap,
        args.vmin,
        args.vmax,
        args.log,
        args.input_type,
        args.show_power
    )

if __name__ == '__main__':
    main() 