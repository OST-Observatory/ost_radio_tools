/**
 * calculate_power_spectrum.c
 * 
 * This program calculates the power spectrum of I/Q data from a binary file.
 * It uses FFTW3 for efficient FFT calculations and processes the data in blocks
 * to handle large files efficiently.
 *
 * Usage:
 *     ./calculate_power_spectrum <input_file> [samples_per_block]
 *
 * Arguments:
 *     input_file: Path to the input I/Q data file
 *     samples_per_block: Number of samples to process in each block (optional)
 *
 * The program will:
 * 1. Read I/Q data from the input file
 * 2. Calculate power spectrum using FFT
 * 3. Write spectrum values to a .f32 file in binary format
 *
 * Example:
 *     ./calculate_power_spectrum gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <fftw3.h>

/**
 * Main function to process raw I/Q data and perform frequency analysis
 * 
 * @param argc Number of command line arguments
 * @param argv Array of command line arguments
 * @return 0 on success
 */
int main(int argc, char *argv[])
{ 
    // File pointers for input and output
    FILE *input_file;
    FILE *output_file;
    
    // Variables for data processing
    float *sample_buffer;           // Buffer for reading I/Q samples
    int samples_per_block;          // Number of samples to process in each block
    long total_file_size;           // Total size of input file in bytes
    long number_of_blocks;          // Total number of blocks to process
    size_t read_result;             // Result of fread operation
    
    // FFT variables
    fftw_complex *fft_input;        // Input buffer for FFT
    fftw_complex *fft_output;       // Output buffer for FFT
    fftw_plan plan;                 // FFTW plan
    
    // Variables for filename handling
    char *input_filename;
    char *dot_position;
    char output_filename[280];      // Buffer for output filename
    char *token;                    // For parsing filename
    char filename_copy[256];        // Copy of filename for parsing
    
    // Check command line arguments
    if (argc < 2 || argc > 3) {
        printf("Usage: %s <input_file> [samples_per_block]\n", argv[0]);
        return 1;
    }
    
    // Extract filename from input path
    input_filename = strrchr(argv[1], '/');
    if (input_filename == NULL) {
        input_filename = argv[1];
    } else {
        input_filename++;  // Skip the '/'
    }
    
    // Make a copy of the filename for parsing
    strncpy(filename_copy, input_filename, sizeof(filename_copy) - 1);
    filename_copy[sizeof(filename_copy) - 1] = '\0';
    
    // Get samples_per_block from command line or filename
    if (argc == 3) {
        samples_per_block = atoi(argv[2]);
    } else {
        // Parse filename to extract samples_per_block
        // Format: gqrx_'start_date'_'start_time'_'frequency'_samples-per-block'_fc_'object'.raw
        token = strtok(filename_copy, "_");
        int field_count = 0;
        while (token != NULL) {
            field_count++;
            if (field_count == 5) {  // samples-per-block is the 5th field
                samples_per_block = atoi(token);
                break;
            }
            token = strtok(NULL, "_");
        }
        
        if (field_count < 5) {
            printf("Error: Could not extract samples_per_block from filename\n");
            return 1;
        }
    }
    
    // Make a copy of the filename for output filename creation
    strncpy(filename_copy, input_filename, sizeof(filename_copy) - 1);
    
    // Remove .raw extension if present
    dot_position = strrchr(filename_copy, '.');
    if (dot_position != NULL && strcmp(dot_position, ".raw") == 0) {
        *dot_position = '\0';  // Terminate string at the dot
    }
    
    // Create output filename
    snprintf(output_filename, sizeof(output_filename), "power_spectrum_%s.f32", filename_copy);
    
    // Allocate memory for sample buffer
    sample_buffer = malloc(sizeof(float) * samples_per_block * 2);
    if (sample_buffer == NULL) {
        printf("Error: Memory allocation failed for sample buffer\n");
        return 1;
    }
    
    // Allocate memory for FFT
    fft_input = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * samples_per_block);
    fft_output = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * samples_per_block);
    if (fft_input == NULL || fft_output == NULL) {
        printf("Error: Memory allocation failed for FFT buffers\n");
        free(sample_buffer);
        return 1;
    }
    
    // Create FFTW plan
    plan = fftw_plan_dft_1d(samples_per_block, fft_input, fft_output, FFTW_FORWARD, FFTW_ESTIMATE);
    
    // Open input file
    input_file = fopen(argv[1], "rb");
    if (input_file == NULL) {
        printf("Error: Could not open input file\n");
        fftw_free(fft_input);
        fftw_free(fft_output);
        fftw_destroy_plan(plan);
        free(sample_buffer);
        return 1;
    }
    
    // Calculate file size and number of blocks
    fseek(input_file, 0L, SEEK_END);
    total_file_size = ftell(input_file);
    number_of_blocks = total_file_size / sizeof(float) / samples_per_block / 2;
    rewind(input_file);
    
    printf("File size: %ld bytes, Number of blocks: %ld, Samples per block: %d\n", 
           total_file_size, number_of_blocks, samples_per_block);
    
    // Open output file in binary write mode
    output_file = fopen(output_filename, "wb");
    if (output_file == NULL) {
        printf("Error: Could not open output file '%s'\n", output_filename);
        fclose(input_file);
        fftw_free(fft_input);
        fftw_free(fft_output);
        fftw_destroy_plan(plan);
        free(sample_buffer);
        return 1;
    }
    
    printf("Writing output to: %s\n", output_filename);
    
    // Write header information
    // fwrite(&samples_per_block, sizeof(int), 1, output_file);

    // Process each block of samples
    for (int current_block = 0; current_block < number_of_blocks; current_block++) {
        // Read a block of samples and check for errors
        read_result = fread(sample_buffer, sizeof(float) * samples_per_block * 2, 1, input_file);
        if (read_result != 1) {
            printf("\nError: Failed to read block %d\n", current_block);
            fclose(output_file);
            fclose(input_file);
            fftw_free(fft_input);
            fftw_free(fft_output);
            fftw_destroy_plan(plan);
            free(sample_buffer);
            return 1;
        }
        
        // Convert I/Q samples to complex numbers
        for (int i = 0; i < samples_per_block; i++) {
            fft_input[i][0] = sample_buffer[i * 2];     // Real part (I)
            fft_input[i][1] = sample_buffer[i * 2 + 1]; // Imaginary part (Q)
        }
        
        // Perform FFT
        fftw_execute(plan);
        
        // Calculate power spectrum and write to file in binary format
        for (int i = 0; i < samples_per_block; i++) {
            float power = fft_output[i][0] * fft_output[i][0] + 
                         fft_output[i][1] * fft_output[i][1];
            fwrite(&power, sizeof(float), 1, output_file);
        }
        
        // Show progress every 20 blocks
        if (current_block % 20 == 0) {
            printf("\r%.1f%% done.", (float)current_block / number_of_blocks * 100.0);
            fflush(stdout);
        }
    }
    
    // Cleanup
    fclose(output_file);
    fclose(input_file);
    fftw_free(fft_input);
    fftw_free(fft_output);
    fftw_destroy_plan(plan);
    free(sample_buffer);
    
    return 0;
} 