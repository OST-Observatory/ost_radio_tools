#!/usr/bin/env python3
"""
Plot spectrogram from binary data file.
This script visualizes the spectrogram of a signal,
showing how the power spectrum changes over time.

Usage:
    ./plot_spectrogram_data.py <input_file> [options]

The input file should be a binary file containing float32 data in the format:
- First 4 bytes: samples_per_block (int32)
- Remaining data: power values in dB scale (float32)

Options:
    --output, -o: Output file for the plot (default: spectrogram_plot_<input>.png)
    --sampling-rate, -s: Sampling rate in Hz (default: extracted from filename)
    --center-frequency, -f: Center frequency in Hz (default: extracted from filename)
    --time-bins, -t: Number of time bins for downsampling (default: 1000)
    --freq-bins, -b: Number of frequency bins for downsampling (default: 1000)

The script will generate a plot showing the spectrogram with time on x-axis,
frequency on y-axis, and power represented by color intensity.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime
import argparse
import os
import re
from scipy import stats


def parse_filename(filename: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """Extract sampling rate, center frequency, and start time from filename.
    
    Args:
        filename: Name of the file to parse
        
    Returns:
        Tuple of (sampling_rate, center_frequency, start_time)
    """
    # Extract sampling rate and center frequency from filename
    # Format: gqrx_'start_date'_'start_time'_'frequency'_samples-per-block'_fc_'object'.raw
    match = re.search(r'gqrx_(\d{8})_(\d{6})_(\d+)_(\d+)_fc_', filename)
    if match:
        start_date = match.group(1)
        start_time = match.group(2)
        center_frequency = match.group(3)
        sampling_rate = int(match.group(4))
        return sampling_rate, center_frequency, f"{start_date}_{start_time}"
    return None, None, None


def plot_spectrogram(
    input_file: str,
    output_file: Optional[str] = None,
    sampling_rate: Optional[int] = None,
    center_frequency: Optional[str] = None,
    time_bins: int = 1000,
    freq_bins: int = 1000
) -> None:
    """Plot spectrogram from binary data file.
    
    Args:
        input_file: Path to the input file containing spectrogram data
        output_file: Path for the output plot file (default: spectrogram_plot_<input>.png)
        sampling_rate: Sampling rate in Hz (default: extracted from filename)
        center_frequency: Center frequency in Hz (default: extracted from filename)
        time_bins: Number of time bins for downsampling
        freq_bins: Number of frequency bins for downsampling
    """
    # Read the samples_per_block from the header
    with open(input_file, 'rb') as f:
        samples_per_block = np.fromfile(f, dtype=np.int32, count=1)[0]
        # Read the rest of the data
        data = np.fromfile(f, dtype=np.float32)
    
    # Calculate number of time steps
    freq_bins_per_block = samples_per_block // 2 + 1
    num_time_steps = len(data) // freq_bins_per_block
    
    # Reshape data into 2D array (time x frequency)
    spectrogram = data.reshape(num_time_steps, freq_bins_per_block)

    # If sampling_rate not provided, try to get it from filename
    if sampling_rate is None:
        sampling_rate, _, _ = parse_filename(input_file)
        if sampling_rate is None:
            print("Warning: Could not determine sampling rate from filename. Using default value of 1 Hz.")
            sampling_rate = 1

    # Get center frequency
    if center_frequency is None:
        _, center_frequency, _ = parse_filename(input_file)
    
    if center_frequency is None:
        print("Warning: Could not determine center frequency. Using 0 Hz.")
        center_frequency = "0"
    
    center_freq = float(center_frequency)

    # Calculate time values in seconds
    time_values = np.arange(num_time_steps) * samples_per_block / sampling_rate

    # Calculate frequency values relative to center frequency
    freq = center_freq + np.linspace(0, sampling_rate, freq_bins_per_block)

    # Create plot
    plt.figure(figsize=(12, 6))
    plt.pcolormesh(time_values, freq, spectrogram.T, shading='auto', cmap='viridis')
    plt.colorbar(label='Power (dB)')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    
    if center_frequency:
        plt.title(f'Spectrogram (Center Frequency: {center_frequency} Hz)')
    else:
        plt.title('Spectrogram')

    # Save plot
    if output_file is None:
        output_file = f'spectrogram_plot_{os.path.basename(input_file)}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def main() -> None:
    """Main function to parse command line arguments and create the plot."""
    parser = argparse.ArgumentParser(description='Plot spectrogram from binary data file')
    parser.add_argument('input_file', help='Input file containing spectrogram data in binary format')
    parser.add_argument('--output', '-o', help='Output file for the plot (default: spectrogram_plot_<input>.png)')
    parser.add_argument('--sampling-rate', '-s', type=int, help='Sampling rate in Hz (default: extracted from filename)')
    parser.add_argument('--center-frequency', '-f', help='Center frequency in Hz (default: extracted from filename)')
    parser.add_argument('--time-bins', '-t', type=int, default=1000, help='Number of time bins for downsampling (default: 1000)')
    parser.add_argument('--freq-bins', '-b', type=int, default=1000, help='Number of frequency bins for downsampling (default: 1000)')
    
    args = parser.parse_args()
    plot_spectrogram(
        args.input_file,
        args.output,
        args.sampling_rate,
        args.center_frequency,
        args.time_bins,
        args.freq_bins
    )


if __name__ == '__main__':
    main() 