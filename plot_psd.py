#!/usr/bin/env python3
"""
Plot Power Spectral Density (PSD) from CSV data file.
This script visualizes the Power Spectral Density of a signal,
showing the power distribution per unit frequency.

Usage:
    ./plot_psd.py <input_file> [options]

The input file should be a CSV file containing two columns:
- First column: Frequency index
- Second column: Power value

Options:
    --output, -o: Output file for the plot (default: psd_plot_<input>.png)
    --sampling-rate, -s: Sampling rate in Hz (default: extracted from filename)
    --center-frequency, -f: Center frequency in Hz (default: extracted from filename)

The script will generate a plot showing the Power Spectral Density in dB/Hz.
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

# Configure matplotlib for large datasets
plt.rcParams['agg.path.chunksize'] = 1000
plt.rcParams['path.simplify_threshold'] = 0.5

def parse_filename(filename: str) -> Tuple[Optional[int], Optional[str], Optional[datetime]]:
    """Extract sampling rate, center frequency, and start time from filename.
    
    Args:
        filename: The name of the input file, which should follow the format:
                 gqrx_YYYYMMDD_HHMMSS_FREQUENCY_SAMPLINGRATE_fc_OBJECT.raw
    
    Returns:
        Tuple containing:
        - sampling_rate: The sampling rate in Hz, or None if not found
        - center_frequency: The center frequency in Hz, or None if not found
        - start_time: The start time as a datetime object, or None if not found
    """
    # Extract sampling rate and center frequency from filename
    # Example: gqrx_20250404_113633_1419390700_1800000_fc_Milky_Way.raw
    match = re.search(r'_(\d+)_fc_', filename)
    if match:
        sampling_rate = int(match.group(1))
    else:
        sampling_rate = None

    # Extract center frequency (the number before the sampling rate)
    match = re.search(r'_(\d+)_\d+_fc_', filename)
    if match:
        center_frequency = match.group(1)
    else:
        center_frequency = None

    # Extract start time from filename
    # Format: gqrx_YYYYMMDD_HHMMSS_...
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


def plot_psd(
    input_file: str,
    output_file: Optional[str] = None,
    sampling_rate: Optional[int] = None,
    center_frequency: Optional[str] = None
) -> None:
    """Plot Power Spectral Density (PSD) from processed I/Q data.
    
    Args:
        input_file: Path to the input file containing frequency and power data
        output_file: Path for the output plot file (default: psd_plot_<input>.png)
        sampling_rate: Sampling rate in Hz (default: extracted from filename)
        center_frequency: Center frequency in Hz (default: extracted from filename)
    
    The function will:
    1. Load the power spectrum data from the input file
    2. Calculate the Power Spectral Density in dB/Hz
    3. Create a plot with frequency on x-axis and PSD on y-axis
    4. Add appropriate labels, title, and grid
    5. Save the plot to the output file
    """
    # Load data
    data = np.loadtxt(input_file)
    freq_index = data[:, 0]
    power = data[:, 1]

    # If sampling_rate not provided, try to get it from filename
    if sampling_rate is None:
        sampling_rate, _, _ = parse_filename(input_file)
        if sampling_rate is None:
            print("Warning: Could not determine sampling rate from filename. Using default value of 1 Hz.")
            sampling_rate = 1

    # Calculate frequency values
    freq = (freq_index - len(freq_index)/2) * sampling_rate / len(freq_index)

    # Calculate PSD (power per Hz)
    psd = power - 10 * np.log10(sampling_rate)

    # Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(freq, psd)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density (dB/Hz)')
    
    # Add center frequency to title if available
    if center_frequency is None:
        _, center_frequency, _ = parse_filename(input_file)
    
    if center_frequency:
        plt.title(f'Power Spectral Density (Center Frequency: {center_frequency})')
    else:
        plt.title('Power Spectral Density')

    plt.grid(True)

    # Save plot
    if output_file is None:
        output_file = f'psd_plot_{os.path.basename(input_file)}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def main() -> None:
    """Main function to parse command line arguments and create the plot.
    
    Command line arguments:
        input_file: Path to the input file containing frequency and power data
        --output, -o: Output file for the plot (default: psd_plot_<input>.png)
        --sampling-rate, -s: Sampling rate in Hz (default: extracted from filename)
        --center-frequency, -f: Center frequency in Hz (default: extracted from filename)
    """
    parser = argparse.ArgumentParser(description='Plot Power Spectral Density from processed I/Q data')
    parser.add_argument('input_file', help='Input file containing frequency and power data')
    parser.add_argument('--output', '-o', help='Output file for the plot (default: psd_plot_<input>.png)')
    parser.add_argument('--sampling-rate', '-s', type=int, help='Sampling rate in Hz (default: extracted from filename)')
    parser.add_argument('--center-frequency', '-f', help='Center frequency in Hz (default: extracted from filename)')
    
    args = parser.parse_args()
    plot_psd(args.input_file, args.output, args.sampling_rate, args.center_frequency)


if __name__ == '__main__':
    main() 