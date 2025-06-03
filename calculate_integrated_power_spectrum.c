/**
 * calculate_integrated_power_spectrum.c
 *
 * This program calculates the integrated power spectrum of I/Q data.
 * It reads I/Q data from a binary file, calculates the power spectrum
 * using FFT, and integrates the spectrum over time.
 *
 * Usage:
 *     ./calculate_integrated_power_spectrum <input_file> [samples_per_block]
 *
 * Arguments:
 *     input_file: Path to the input I/Q data file
 *     samples_per_block (optional): Number of samples to process in each block
 *
 * The program will:
 * 1. Read I/Q data from the input file
 * 2. Calculate power spectrum using FFT
 * 3. Integrate the spectrum over time
 * 4. Write integrated spectrum values to a .dat file
 *
 * Example:
 *     ./calculate_integrated_power_spectrum gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include <fftw3.h>

#define MAX_LINE_LENGTH 1024

// Structure to hold FFT configuration
typedef struct {
    int samples_per_block;
    fftwf_complex *in;
    float *out;
    fftwf_plan plan;
} FFTConfig;

// Initialize FFT configuration
FFTConfig* init_fft(int samples_per_block) {
    FFTConfig *config = malloc(sizeof(FFTConfig));
    if (!config) {
        fprintf(stderr, "Error: Failed to allocate FFT configuration\n");
        return NULL;
    }

    config->samples_per_block = samples_per_block;
    config->in = fftwf_alloc_complex(samples_per_block);
    config->out = fftwf_alloc_real(samples_per_block);
    
    if (!config->in || !config->out) {
        fprintf(stderr, "Error: Failed to allocate FFT buffers\n");
        free(config->in);
        free(config->out);
        free(config);
        return NULL;
    }

    config->plan = fftwf_plan_dft_c2r_1d(samples_per_block, config->in, config->out, FFTW_ESTIMATE);
    if (!config->plan) {
        fprintf(stderr, "Error: Failed to create FFT plan\n");
        free(config->in);
        free(config->out);
        free(config);
        return NULL;
    }

    return config;
}

// Clean up FFT configuration
void cleanup_fft(FFTConfig *config) {
    if (config) {
        fftwf_destroy_plan(config->plan);
        fftwf_free(config->in);
        fftwf_free(config->out);
        free(config);
    }
}

// Process a single block of data
void process_block(FFTConfig *config, float *iq_data, float *power_spectrum) {
    // Copy I/Q data to complex input buffer
    for (int i = 0; i < config->samples_per_block; i++) {
        config->in[i] = iq_data[2*i] + I * iq_data[2*i + 1];
    }

    // Execute FFT
    fftwf_execute(config->plan);

    // Calculate power spectrum
    for (int i = 0; i < config->samples_per_block; i++) {
        float power = config->out[i] * config->out[i];
        power_spectrum[i] += power;  // Accumulate power
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file> [samples_per_block]\n", argv[0]);
        return 1;
    }

    const char *input_file = argv[1];
    int samples_per_block = 0;

    // Try to extract samples_per_block from filename
    const char *filename = strrchr(input_file, '/');
    filename = filename ? filename + 1 : input_file;
    
    const char *samples_str = strstr(filename, "_");
    if (samples_str) {
        samples_str = strstr(samples_str + 1, "_");
        if (samples_str) {
            samples_str = strstr(samples_str + 1, "_");
            if (samples_str) {
                samples_str = strstr(samples_str + 1, "_");
                if (samples_str) {
                    samples_per_block = atoi(samples_str + 1);
                }
            }
        }
    }

    // If not found in filename, use command line argument
    if (samples_per_block <= 0 && argc > 2) {
        samples_per_block = atoi(argv[2]);
    }

    if (samples_per_block <= 0) {
        fprintf(stderr, "Error: Invalid samples_per_block\n");
        return 1;
    }

    // Initialize FFT
    FFTConfig *fft_config = init_fft(samples_per_block);
    if (!fft_config) {
        return 1;
    }

    // Allocate buffers
    float *iq_data = malloc(2 * samples_per_block * sizeof(float));
    float *power_spectrum = calloc(samples_per_block, sizeof(float));
    if (!iq_data || !power_spectrum) {
        fprintf(stderr, "Error: Failed to allocate buffers\n");
        cleanup_fft(fft_config);
        free(iq_data);
        free(power_spectrum);
        return 1;
    }

    // Open input file
    FILE *fp = fopen(input_file, "rb");
    if (!fp) {
        fprintf(stderr, "Error: Could not open input file\n");
        cleanup_fft(fft_config);
        free(iq_data);
        free(power_spectrum);
        return 1;
    }

    // Generate output filename
    char output_file[1024];
    // Get base filename without path
    const char *base = strrchr(input_file, '/');
    base = base ? base + 1 : input_file;
    // Remove extension
    char base_noext[512];
    const char *dot = strrchr(base, '.');
    if (dot) {
        strncpy(base_noext, base, dot - base);
        base_noext[dot - base] = '\0';
    } else {
        strncpy(base_noext, base, sizeof(base_noext) - 1);
        base_noext[sizeof(base_noext) - 1] = '\0';
    }
    snprintf(output_file, sizeof(output_file), "integrated_power_spectrum_%s.dat", base_noext);

    // Process data
    size_t total_blocks = 0;
    const size_t samples_to_read = 2 * (size_t)samples_per_block;
    while (fread(iq_data, sizeof(float), samples_to_read, fp) == samples_to_read) {
        process_block(fft_config, iq_data, power_spectrum);
        total_blocks++;
    }

    // Calculate average power spectrum
    if (total_blocks > 0) {
        for (int i = 0; i < samples_per_block; i++) {
            power_spectrum[i] /= total_blocks;
        }
    }

    // Save results
    FILE *out_fp = fopen(output_file, "w");
    if (!out_fp) {
        fprintf(stderr, "Error: Could not open output file\n");
        cleanup_fft(fft_config);
        free(iq_data);
        free(power_spectrum);
        fclose(fp);
        return 1;
    }

    for (int i = 0; i < samples_per_block; i++) {
        fprintf(out_fp, "%d %e\n", i, power_spectrum[i]);
    }

    // Cleanup
    fclose(fp);
    fclose(out_fp);
    cleanup_fft(fft_config);
    free(iq_data);
    free(power_spectrum);

    printf("Processed %zu blocks\n", total_blocks);
    printf("Output saved to: %s\n", output_file);

    return 0;
} 