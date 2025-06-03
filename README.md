# OST Radio Signal Analysis Tools

This repository contains a collection of tools for analyzing data from small radio telescopes, particularly I/Q data from SDR (Software Defined Radio) recordings. The tools include C programs for data processing and Python scripts for visualization.These tools are still in the development stage and may contain significant bugs.

## Analysis Tools

### Amplitude Analysis

#### Calculate Amplitude Sum (`calculate_amplitude_sum`)

This program calculates the amplitude sum from I/Q data.

Usage:
```bash
./calculate_amplitude_sum <input_file> [samples_per_block]
```

Arguments:
- `input_file`: Path to the input I/Q data file
- `samples_per_block` (optional): Number of samples to process in each block

The program will:
1. Read I/Q data from the input file
2. Calculate amplitude (√(I² + Q²)) for each sample
3. Write amplitude values to a .dat file

Example:
```bash
./calculate_amplitude_sum gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
```

#### Calculate Amplitude (`calculate_amplitude`)

This program calculates the amplitude from I/Q data.

Usage:
```bash
./calculate_amplitude <input_file> [samples_per_block]
```

Arguments:
- `input_file`: Path to the input I/Q data file
- `samples_per_block` (optional): Number of samples to process in each block

The program will:
1. Read I/Q data from the input file
2. Calculate amplitude (√(I² + Q²)) for each sample
3. Write amplitude values to a .f32 file

Features:
- Direct amplitude calculation from I/Q samples
- Memory-efficient processing of large files
- Automatic extraction of samples_per_block from filename
- Progress reporting during processing
- Output in linear scale (not dB)

Example:
```bash
./calculate_amplitude gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
```

#### Plot Amplitude Sum vs Time (`plot_amplitude_sum_vs_time.py`)

This script visualizes amplitude sum over time.

Usage:
```bash
./plot_amplitude_sum_vs_time.py <input_file> [options]
```

Arguments:
- `input_file`: Path to the input file containing time and amplitude data

Options:
- `--output`, `-o`: Output file for the plot (default: amplitude_sum_plot_<input>.png)
- `--sampling-rate`, `-s`: Sampling rate in Hz (default: extracted from filename)
- `--center-frequency`, `-f`: Center frequency (default: extracted from filename)
- `--start-time`, `-t`: Start time in format YYYYMMDD_HHMMSS (default: extracted from filename)
- `--linear`, `-l`: Display amplitude in linear scale instead of dB

Features:
- Plots amplitude sum values over time
- Time display in either datetime or seconds
- Amplitude display in linear or dB scale
- Center frequency and start time in title if available
- Grid for better readability
- High-resolution output (300 DPI)

Example:
```bash
./plot_amplitude_sum_vs_time.py amplitude_gqrx_20250404_084805_1419390700_1800000_fc_sun.dat --linear
```

### Power Analysis

#### Calculate Power (`calculate_power`)

This program calculates power from I/Q data and can optionally sum power values over blocks.

Usage:
```bash
./calculate_power <input_file> [samples_per_block] [--output-type TYPE]
```

Arguments:
- `input_file`: Path to the input I/Q data file
- `samples_per_block` (optional): Number of samples to process in each block
- `--output-type TYPE`: Type of output to generate (default: sum)
  - `sum`: Only write summed power values to .dat file (default)
  - `raw`: Only write raw power values to .f32 file
  - `both`: Write both summed and raw power values

The program will:
1. Read I/Q data from the input file
2. Calculate power (I² + Q²) for each sample
3. Write power values according to the output type:
   - For 'raw' or 'both': Write raw power values to a .f32 file
   - For 'sum' or 'both': Write summed power values to a .dat file

Example:
```bash
# Write only summed power values (default)
./calculate_power gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000

# Write only raw power values
./calculate_power gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000 --output-type raw

# Write both raw and summed power values
./calculate_power gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000 --output-type both
```

#### Plot Power Sum vs Time (`plot_power_sum_vs_time.py`)

This script visualizes power sum over time with various statistical measures.

Usage:
```bash
./plot_power_sum_vs_time.py <input_file> [options]
```

Arguments:
- `input_file`: Path to the input file containing time and power data

Options:
- `--output`, `-o`: Output file for the plot (default: power_sum_plot_<input>.png)
- `--sampling-rate`, `-s`: Sampling rate in Hz (default: extracted from filename)
- `--center-frequency`, `-f`: Center frequency (default: extracted from filename)
- `--start-time`, `-t`: Start time in format YYYYMMDD_HHMMSS (default: extracted from filename)
- `--linear`, `-l`: Display power in linear scale instead of dB
- `--fit-gaussian`, `-g`: Fit and plot a Gaussian curve to the data
- `--background`, `-b`: Background power level for normalization
- `--calibration`, `-c`: Calibration power level for normalization
- `--seconds`, `-S`: Display time in seconds even if start_time is available
- `--declination`, `-d`: Declination of the object in degrees for FWHM correction (applies cos(declination) correction to angular FWHM)

Features:
- Plots power sum values over time
- Shows mean, median, and median of top 20 values
- Optional Gaussian curve fitting with FWHM calculation
- Power normalization using background and calibration values
- Time display in either datetime or seconds
- Console output of statistical measures
- High-resolution output (300 DPI)
- Grid for better readability
- Center frequency and start time in title if available
- Optional declination correction for angular FWHM calculation

The script will output statistical measures to the console:
```
Power Statistics:
Mean: xxx.xxx
Median: xxx.xxx
Median (top 20): xxx.xxx
```

Example:
```bash
# Basic usage
./plot_power_sum_vs_time.py data.csv

# With Gaussian fit and declination correction
./plot_power_sum_vs_time.py data.csv --fit-gaussian --declination 45

# With power normalization
./plot_power_sum_vs_time.py data.csv --background 1.0 --calibration 2.0
```

### Spectrum Analysis

#### Calculate Power Spectrum (`calculate_power_spectrum`)

This program calculates the power spectrum of I/Q data.

Usage:
```bash
./calculate_power_spectrum <input_file> [samples_per_block]
```

Arguments:
- `input_file`: Path to the input I/Q data file
- `samples_per_block` (optional): Number of samples to process in each block

The program will:
1. Read I/Q data from the input file
2. Calculate power spectrum using FFT
3. Write spectrum values to a .f32 file in binary format

Features:
- Uses FFTW3 for efficient FFT calculations
- Processes data in blocks for memory efficiency
- Outputs raw power values in linear scale
- Stores complete spectrum (all frequency bins)
- No window function applied

Example:
```bash
./calculate_power_spectrum gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
```

### Integrated Spectrum

#### Calculate Integrated Power Spectrum (`calculate_integrated_power_spectrum`)

This program calculates the integrated power spectrum of I/Q data.

Usage:
```bash
./calculate_integrated_power_spectrum <input_file> [samples_per_block]
```

Arguments:
- `input_file`: Path to the input I/Q data file
- `samples_per_block` (optional): Number of samples to process in each block

The program will:
1. Read I/Q data from the input file
2. Calculate integrated power spectrum using FFT
3. Write integrated spectrum values to a .dat file

Features:
- Efficient FFT calculation using FFTW3
- Memory-efficient processing of large files
- Automatic extraction of samples_per_block from filename
- Progress reporting during processing

Example:
```bash
./calculate_integrated_power_spectrum gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
```

#### Plot Integrated Power Spectrum (`plot_integrated_power_spectrum.py`)

This script visualizes the integrated power spectrum.

Usage:
```bash
./plot_integrated_power_spectrum.py <input_file> [options]
```

Arguments:
- `input_file`: Path to the input file containing integrated spectrum data

Options:
- `--output`, `-o`: Output file for the plot (default: integrated_power_spectrum_plot_<input>.png)
- `--sampling-rate`, `-s`: Sampling rate in Hz (default: extracted from filename)
- `--center-frequency`, `-f`: Center frequency (default: extracted from filename)

Features:
- Plots integrated power spectrum in dB scale
- Frequency in Hz on x-axis
- Power in dB on y-axis
- Center frequency in title if available
- Grid for better readability
- High-resolution output (300 DPI)

Example:
```bash
./plot_integrated_power_spectrum.py integrated_power_spectrum_gqrx_20250404_084805_1419390700_1800000_fc_sun.dat
```

#### Plot PSD (`plot_psd.py`)

This script calculates and visualizes the Power Spectral Density.

Usage:
```bash
./plot_psd.py <input_file> [options]
```

Arguments:
- `input_file`: Path to the input file containing power spectrum data

Options:
- `--output`, `-o`: Output file for the plot (default: psd_plot_<input>.png)
- `--sampling-rate`, `-s`: Sampling rate in Hz (default: extracted from filename)
- `--center-frequency`, `-f`: Center frequency (default: extracted from filename)

Features:
- Calculates and plots PSD in dB/Hz scale
- Frequency in Hz on x-axis
- Power Spectral Density in dB/Hz on y-axis
- Center frequency in title if available
- Grid for better readability
- High-resolution output (300 DPI)

Example:
```bash
./plot_psd.py power_spectrum_gqrx_20250404_084805_1419390700_1800000_fc_sun.dat
```

### Spectrogram

#### Calculate Spectrogram (`calculate_spectrogram`)

This program calculates the spectrogram of I/Q data.

Usage:
```bash
./calculate_spectrogram <input_file> [samples_per_block]
```

Arguments:
- `input_file`: Path to the input I/Q data file
- `samples_per_block` (optional): Number of samples to process in each block

The program will:
1. Read I/Q data from the input file
2. Calculate spectrogram using FFT
3. Write spectrogram values to a .f32 file

Features:
- Uses FFTW3 for efficient FFT calculations
- Applies Hanning window to reduce spectral leakage
- Outputs power values in dB scale (10 * log10(power))
- Stores only positive frequencies (n/2 + 1 bins)
- Includes block size in output file header
- Optimized for visualization purposes

Example:
```bash
./calculate_spectrogram gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
```

#### Plot Spectrogram (`plot_spectrogram_data.py`)

This script visualizes the spectrogram.

Usage:
```bash
./plot_spectrogram_data.py <input_file> [options]
```

Arguments:
- `input_file`: Path to the input file containing spectrogram data

Options:
- `--output`, `-o`: Output file for the plot (default: spectrogram_plot_<input>.png)
- `--sampling-rate`, `-s`: Sampling rate in Hz (default: extracted from filename)
- `--center-frequency`, `-f`: Center frequency (default: extracted from filename)

Features:
- Plots spectrogram with time on x-axis and frequency on y-axis
- Color represents power in dB
- Center frequency in title if available
- Colorbar showing power scale
- High-resolution output (300 DPI)

Example:
```bash
./plot_spectrogram_data.py spectrogram_gqrx_20250404_084805_1419390700_1800000_fc_sun.f32
```

### Waterfall Plot

#### Plot Waterfall (`plot_waterfall.py`)

This script creates a waterfall plot from amplitude, power, or power spectrum data, showing how the signal power varies across different frequencies over time.

Usage:
```bash
./plot_waterfall.py <input_file> [options]
```

Arguments:
- `input_file`: Path to the input file containing amplitude, power, power spectrum data (binary .f32 format)

Options:
- `--output`, `-o`: Output file for the plot (default: waterfall_plot_<input>.png)
- `--sampling-rate`, `-s`: Sampling rate in Hz (default: extracted from filename)
- `--center-frequency`, `-f`: Center frequency (default: extracted from filename)
- `--normalize`, `-n`: Normalization method for the data
  - `none`: No normalization (default)
  - `global`: Normalize to global min/max
  - `row`: Normalize each time step independently
  - `column`: Normalize each frequency bin independently
  - `zscore`: Z-score normalization
- `--colormap`, `-c`: Colormap for the plot (default: 'viridis')
- `--vmin`, `-v`: Minimum value for color scaling
- `--vmax`, `-V`: Maximum value for color scaling
- `--log`, `-l`: Use logarithmic scaling
- `--input-type`, `-t`: Type of input data
  - `amplitude`: Input data represents amplitudes
  - `power`: Input data represents power values (default)
- `--show-power`, `-p`: Convert amplitude data to power (only relevant for amplitude input)

Features:
- Creates waterfall plot with frequency on x-axis and time on y-axis
- Color represents signal power/amplitude
- Automatic extraction of sampling rate and center frequency from filename
- Various normalization options for better visualization
- Logarithmic scaling option for wide dynamic range
- Support for both amplitude and power input data
- Optional conversion of amplitude data to power
- Customizable colormap and color scaling
- High-resolution output (300 DPI)
- Grid for better readability
- Center frequency in title if available

Examples:
```bash
# Basic usage with power data
./plot_waterfall.py power_spectrum.f32

# Amplitude data with logarithmic scaling
./plot_waterfall.py amplitude_data.f32 -t amplitude -l

# Amplitude data converted to power
./plot_waterfall.py amplitude_data.f32 -t amplitude -p

# Custom normalization and colormap
./plot_waterfall.py data.f32 -n row -c plasma

# Manual color scaling
./plot_waterfall.py data.f32 -v -10 -V 10

# Full combination of options
./plot_waterfall.py data.f32 -t amplitude -p -l -n row -c plasma -v -20 -V 0
```

### Calibration

#### Calculate Calibration (`calculate_calibration.py`)

This script calculates system temperature (T_sys) and optionally object temperature (T_obj) using calibration measurements.

Usage:
```bash
./calculate_calibration.py --t-cal T_CAL --p-cal P_CAL --p-sky P_SKY [--p-obj P_OBJ] [--beam-size BEAM_SIZE --sa-obj SA_OBJ]
```

Arguments:
- `--t-cal`: Calibration temperature in Kelvin
- `--p-cal`: Calibration power
- `--p-sky`: Sky power
- `--p-obj`: Object power (optional)
- `--beam-size`: Beam size in square degrees (optional, required for solid angle correction)
- `--sa-obj`: Source solid angle in square degrees (optional, required for solid angle correction)

Features:
- Calculates system temperature (T_sys) using the formula: T_sys = T_cal / (p_cal/p_sky - 1)
- Optionally calculates object temperature (T_obj) using the formula: T_obj = (p_obj-p_sky)/(p_cal-p_sky)*T_cal * (beam_size/sa_obj)^2
- Includes solid angle correction for extended sources
- Provides detailed output of all input parameters and calculated values

Example:
```bash
./calculate_calibration.py --t-cal 300 --p-cal 1.5 --p-sky 1.0 --p-obj 1.2 --beam-size 0.1 --sa-obj 0.05
```

## File Naming Convention

The tools expect input files to follow this naming convention:
```
gqrx_YYYYMMDD_HHMMSS_FREQUENCY_SAMPLINGRATE_fc_OBJECT.raw
```
Where:
- YYYYMMDD: Date (YYYY=year, MM=month, DD=day)
- HHMMSS: Time (HH=hour, MM=minute, SS=second)
- FREQUENCY: Center frequency in Hz
- SAMPLINGRATE: Sampling rate in Hz
- OBJECT: Name of the observed object

Example:
```
gqrx_20250404_113633_1419390700_1800000_fc_Milky_Way.raw
```

## Program Dependencies

1. Amplitude Analysis:
   - C Programs: 
     - `calculate_amplitude_sum` → Python Script: `plot_amplitude_sum_vs_time.py`
       - Processes raw I/Q data into amplitude values and optionally sums them over blocks
       - Visualizes amplitude values over time
     - `calculate_amplitude` → Python Script: `plot_waterfall.py`
       - Calculates amplitude from I/Q data
       - Visualizes the amplitude data as a waterfall plot

2. Power Analysis:
   - C Program: `calculate_power` → Python Script: `plot_power_sum_vs_time.py` or `plot_waterfall.py`
   - The C program calculates power from I/Q data
   - The Python script visualizes power over time with statistical measures

3. Power Spectrum Analysis:
   - C Program: `calculate_power_spectrum` → Python Script: `plot_waterfall.py`
   - The C program calculates the power spectrum from I/Q data
   - The Python script visualizes the power spectrum

4. Integrated Power Spectrum Analysis:
   - C Program: `calculate_integrated_power_spectrum` → Python Script: `plot_integrated_power_spectrum.py`
   - The C program calculates the integrated power spectrum from I/Q data
   - The Python script visualizes the integrated power spectrum

5. Power Spectral Density (PSD) Analysis:
   - C Program: `calculate_integrated_power_spectrum` → Python Script: `plot_psd.py`
   - Uses the same input as power spectrum analysis
   - The Python script calculates and visualizes the PSD

6. Spectrogram Analysis:
   - C Program: `calculate_spectrogram` → Python Script: `plot_spectrogram_data.py`
   - The C program calculates the spectrogram from I/Q data
   - The Python script visualizes the spectrogram with frequency vs time

## Dependencies

- C Programs:
  - FFTW3 library (for FFT calculations)
  - Standard C libraries

- Python Scripts:
  - NumPy (for numerical computations)
  - Matplotlib (for plotting)
  - Standard Python libraries

## Python Environment Setup

### Option 1: Using venv (Recommended)

1. Create a new virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. When you're done, you can deactivate the virtual environment:
```bash
deactivate
```

### Option 2: Using conda

1. Create a new conda environment:
```bash
conda create -n radio_tools python=3.9
```

2. Activate the conda environment:
```bash
conda activate radio_tools
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. When you're done, you can deactivate the conda environment:
```bash
conda deactivate
```

## Building

1. Install dependencies:
```bash
sudo apt-get install libfftw3-dev
```

2. Build C programs:
```bash
make
```

3. Make Python scripts executable:
```bash
chmod +x *.py
```

## License

This project is licensed under the GPT License - see the LICENSE file for details.