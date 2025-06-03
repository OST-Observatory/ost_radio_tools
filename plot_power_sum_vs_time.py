#!/usr/bin/env python3
"""
Plot Power Sum vs Time

This script visualizes power sum values over time with various statistical measures.
It reads time and power data from a CSV file and generates a plot showing the power
sum values along with mean, median, and other statistical measures.

Usage:
    ./plot_power_sum_vs_time.py <input_file> [options]

Arguments:
    input_file: Path to the input file containing time and power data

Options:
    --output, -o: Output file for the plot (default: power_sum_plot_<input>.png)
    --sampling-rate, -s: Sampling rate in Hz (default: extracted from filename)
    --center-frequency, -f: Center frequency (default: extracted from filename)
    --start-time, -t: Start time in format YYYYMMDD_HHMMSS (default: extracted from filename)
    --linear, -l: Display power in linear scale instead of dB
    --fit-gaussian, -g: Fit and plot a Gaussian curve to the data
    --background, -b: Background power level for normalization
    --calibration, -c: Calibration power level for normalization
    --seconds, -S: Display time in seconds even if start_time is available
    --declination, -d: Declination of the object in degrees for FWHM correction

Example:
    ./plot_power_sum_vs_time.py data.csv --fit-gaussian --declination 45
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime, timedelta
import argparse
import os
import re
from scipy.optimize import curve_fit


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

def gaussian(x, amplitude, mean, sigma):
    """Gaussian function for fitting"""
    return amplitude * np.exp(-(x - mean)**2 / (2 * sigma**2))

def fit_gaussian(time, power):
    """Fit a Gaussian curve to the power data"""
    # Initial guess for parameters [amplitude, mean, sigma]
    p0 = [np.max(power), np.mean(time), np.std(time)]
    
    # Fit the Gaussian
    popt, pcov = curve_fit(gaussian, time, power, p0=p0)
    
    # Calculate FWHM (Full Width at Half Maximum)
    fwhm = 2.355 * popt[2]  # FWHM = 2.355 * sigma
    
    return popt, pcov, fwhm

def plot_power_vs_time(
    input_file: str,
    output_file: Optional[str] = None,
    sampling_rate: Optional[int] = None,
    center_frequency: Optional[str] = None,
    start_time: Optional[datetime] = None,
    linear: bool = False,
    fit_gaussian_curve: bool = False,
    linear_background: Optional[float] = None,
    linear_calibration: Optional[float] = None,
    use_seconds: bool = False,
    declination: Optional[float] = None
) -> None:
    """Plot power vs time from processed I/Q data.
    
    Args:
        input_file: Path to the input file containing time and power data
        output_file: Path for the output plot file (default: power_plot_<input>.png)
        sampling_rate: Sampling rate in Hz (default: extracted from filename)
        center_frequency: Center frequency in Hz (default: extracted from filename)
        start_time: Start time as datetime object (default: extracted from filename)
        linear: If True, display power in linear scale instead of dB
        fit_gaussian_curve: If True, fit and plot a Gaussian curve to the data
        linear_background: Background power level for normalization
        linear_calibration: Calibration power level for normalization
        use_seconds: If True, display time in seconds even if start_time is available
        declination: Declination of the object in degrees for FWHM correction
    """
    # Load data
    data = np.loadtxt(input_file)
    time = data[:, 0]
    power = data[:, 1]

    # If sampling_rate not provided, try to get it from filename
    if sampling_rate is None:
        sampling_rate, _, _ = parse_filename(input_file)
        if sampling_rate is None:
            print("Warning: Could not determine sampling rate from filename. Using default value of 1 Hz.")
            sampling_rate = 1

    # If start_time not provided, try to get it from filename
    if start_time is None:
        _, _, start_time = parse_filename(input_file)

    # Create plot
    plt.figure(figsize=(12, 6))

    # Normalize power if background and calibration values are provided
    if linear_background is not None and linear_calibration is not None:
        power = (power - linear_background) / (linear_calibration - linear_background)
        print(f"Power normalized using background={linear_background} and calibration={linear_calibration}")

    # Convert power to dB if linear is False
    if not linear:
        power = 10 * np.log10(power)  # Note: 10 instead of 20 for power
    
    # Plot the data
    if start_time and not use_seconds:
        # Convert time indices to datetime objects
        time_dt = [start_time + timedelta(seconds=int(t)) for t in time]
        plt.plot(time_dt, power, '.', color='#3498DB', label='Measured Power', alpha=0.6)
        plt.xlabel('Time')
        plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
    else:
        plt.plot(time, power, '.', color='#3498DB', label='Measured Power', alpha=0.6)
        plt.xlabel('Time (s)')
    
    # Calculate and plot mean and median
    mean_power = np.mean(power)
    median_power = np.median(power)
    
    # Calculate median of top 20 values
    top_20_median = np.median(np.sort(power)[-20:])
    
    # Print statistics to console
    print("\nPower Statistics:")
    print(f"Mean: {mean_power:.3f}")
    print(f"Median: {median_power:.3f}")
    print(f"Median (top 20): {top_20_median:.3f}")
    
    # Plot mean and median lines
    if start_time and not use_seconds:
        plt.axhline(y=mean_power, color='#E74C3C', alpha=0.6, linestyle='--', label=f'Mean: {mean_power:.3f}')
        plt.axhline(y=median_power, color='#2ECC71', alpha=0.6, linestyle='--', label=f'Median: {median_power:.3f}')
        plt.axhline(y=top_20_median, color='#9B59B6', alpha=0.6, linestyle='--', label=f'Median (top 20): {top_20_median:.3f}')
    else:
        plt.axhline(y=mean_power, color='#E74C3C', alpha=0.6, linestyle='--', label=f'Mean: {mean_power:.3f}')
        plt.axhline(y=median_power, color='#2ECC71', alpha=0.6, linestyle='--', label=f'Median: {median_power:.3f}')
        plt.axhline(y=top_20_median, color='#9B59B6', alpha=0.6, linestyle='--', label=f'Median (top 20): {top_20_median:.3f}')
    
    # Fit and plot Gaussian if requested
    if fit_gaussian_curve:
        popt, pcov, fwhm = fit_gaussian(time, power)
        
        # Plot fitted Gaussian
        x_fit = np.linspace(min(time), max(time), 1000)
        y_fit = gaussian(x_fit, *popt)
        
        if start_time and not use_seconds:
            x_fit_dt = [start_time + timedelta(seconds=int(t)) for t in x_fit]
            plt.plot(x_fit_dt, y_fit, color='#F39C12', label='Gaussian Fit')
            # Add FWHM lines
            fwhm_time1 = start_time + timedelta(seconds=int(popt[1] - fwhm/2))
            fwhm_time2 = start_time + timedelta(seconds=int(popt[1] + fwhm/2))
            plt.axvline(x=fwhm_time1, color='#F39C12', linestyle='--', alpha=0.4)
            plt.axvline(x=fwhm_time2, color='#F39C12', linestyle='--', alpha=0.4)
        else:
            plt.plot(x_fit, y_fit, color='#F39C12', label='Gaussian Fit')
            plt.axvline(x=popt[1] - fwhm/2, color='#F39C12', linestyle='--', alpha=0.4)
            plt.axvline(x=popt[1] + fwhm/2, color='#F39C12', linestyle='--', alpha=0.4)
        
        # Add FWHM to title
        if declination is not None:
            title_fwhm = f'\nHPBW = {fwhm:.2f}s' + r'$\equiv$' + f'{fwhm/3600*15*np.cos(np.radians(declination)):.2f}' + r'$\degree$'
        else:
            title_fwhm = f'\nHPBW = {fwhm:.2f}s' + r'$\equiv$' + f'{fwhm/3600*15:.2f}' + r'$\degree$'
    else:
        title_fwhm = ''
    
    plt.ylabel('Power' if linear else 'Power (dB)')
    
    # Add center frequency and start time to title if available
    if center_frequency is None:
        _, center_frequency, _ = parse_filename(input_file)
    
    if center_frequency and not start_time:
        plt.title(f'Power vs. Time (Center Frequency: {center_frequency}){title_fwhm}')
    elif start_time and not center_frequency:
        plt.title(f'Power vs. Time (Start Time: {start_time}){title_fwhm}')
    elif center_frequency and start_time:
        plt.title(f'Power vs. Time (Center Frequency: {center_frequency}, Start Time: {start_time}){title_fwhm}')
    else:
        plt.title(f'Power vs. Time{title_fwhm}')

    plt.legend()
    plt.grid(True)

    # Save plot
    if output_file is None:
        output_file = f'power_sum_plot_{os.path.splitext(os.path.basename(input_file))[0]}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

def main() -> None:
    """Main function to parse command line arguments and create the plot.
    
    Command line arguments:
        input_file: Path to the input file containing time and power data
        --output, -o: Output file for the plot (default: power_sum_plot_<input>.png)
        --sampling-rate, -s: Sampling rate in Hz (default: extracted from filename)
        --center-frequency, -f: Center frequency (default: extracted from filename)
        --start-time, -t: Start time in format YYYYMMDD_HHMMSS (default: extracted from filename)
        --linear, -l: Display power in linear scale instead of dB
        --fit-gaussian, -g: Fit and plot a Gaussian curve to the data
        --background, -b: Background power level for normalization
        --calibration, -c: Calibration power level for normalization
        --seconds, -S: Display time in seconds even if start_time is available
        --declination, -d: Declination of the object in degrees for FWHM correction
    """
    parser = argparse.ArgumentParser(description='Plot power vs time from processed I/Q data')
    parser.add_argument('input_file', help='Input file containing time and power data')
    parser.add_argument('--output', '-o', help='Output file for the plot (default: power_sum_plot_<input>.png)')
    parser.add_argument('--sampling-rate', '-s', type=int, help='Sampling rate in Hz (default: extracted from filename)')
    parser.add_argument('--center-frequency', '-f', help='Center frequency (default: extracted from filename)')
    parser.add_argument('--start-time', '-t', help='Start time in format YYYYMMDD_HHMMSS (default: extracted from filename)')
    parser.add_argument('--linear', '-l', action='store_true', help='Display power in linear scale instead of dB')
    parser.add_argument('--fit-gaussian', '-g', action='store_true', help='Fit and plot a Gaussian curve to the data')
    parser.add_argument('--background', '-b', type=float, help='Background power level for normalization')
    parser.add_argument('--calibration', '-c', type=float, help='Calibration power level for normalization')
    parser.add_argument('--seconds', '-S', action='store_true', help='Display time in seconds even if start_time is available')
    parser.add_argument('--declination', '-d', type=float, help='Declination of the object in degrees for FWHM correction')
    
    args = parser.parse_args()
    
    # Parse start time if provided
    start_time = None
    if args.start_time:
        try:
            start_time = datetime.strptime(args.start_time, "%Y%m%d_%H%M%S")
        except ValueError:
            print("Warning: Invalid start time format. Using time from filename or seconds.")
    
    plot_power_vs_time(
        args.input_file, 
        args.output, 
        args.sampling_rate, 
        args.center_frequency, 
        start_time, 
        args.linear,
        args.fit_gaussian,
        args.background,
        args.calibration,
        args.seconds,
        args.declination
    )

if __name__ == '__main__':
    main() 