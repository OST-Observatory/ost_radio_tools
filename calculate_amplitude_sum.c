/**
 * calculate_amplitude_sum.c
 *
 * This program calculates the amplitude sum from I/Q data.
 * It reads I/Q data from a binary file, calculates the amplitude (√(I² + Q²))
 * for each sample, and writes these values to a .f32 file.
 *
 * Usage:
 *     ./calculate_amplitude_sum <input_file> [samples_per_block]
 *
 * Arguments:
 *     input_file: Path to the input I/Q data file
 *     samples_per_block (optional): Number of samples to process in each block
 *
 * The program will:
 * 1. Read I/Q data from the input file
 * 2. Calculate amplitude (√(I² + Q²)) for each sample
 * 3. Write amplitude values to a .f32 file
 *
 * Example:
 *     ./calculate_amplitude_sum gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#include <math.h>
#include <complex.h>

/**
 * Main function to process raw I/Q data
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
    float in_phase, quadrature;     // I and Q components of the signal
    long total_file_size;           // Total size of input file in bytes
    long number_of_blocks;          // Total number of blocks to process
    size_t read_result;             // Result of fread operation
    
    // Variables for filename handling
    char *input_filename;
    char *dot_position;
    char output_filename[270];      // Buffer for output filename
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
    snprintf(output_filename, sizeof(output_filename), "amplitude_%s.dat", filename_copy);
    
    // Allocate memory for sample buffer
    sample_buffer = malloc(sizeof(float) * samples_per_block * 2);
    if (sample_buffer == NULL) {
        printf("Error: Memory allocation failed\n");
        return 1;
    }
    
    // Open input file
    input_file = fopen(argv[1], "rb");
    if (input_file == NULL) {
        printf("Error: Could not open input file\n");
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
    
    // Open output file
    output_file = fopen(output_filename, "w");
    if (output_file == NULL) {
        printf("Error: Could not open output file '%s'\n", output_filename);
        fclose(input_file);
        free(sample_buffer);
        return 1;
    }
    
    printf("Writing output to: %s\n", output_filename);
    
    // Process each block of samples
    for (int current_block = 0; current_block < number_of_blocks; current_block++) {
        double block_amplitude_sum = 0;
        
        // Read a block of samples and check for errors
        read_result = fread(sample_buffer, sizeof(float) * samples_per_block * 2, 1, input_file);
        if (read_result != 1) {
            printf("\nError: Failed to read block %d\n", current_block);
            fclose(output_file);
            fclose(input_file);
            free(sample_buffer);
            return 1;
        }
        
        // Calculate RMS amplitude for each sample in the block
        for (int sample_index = 0; sample_index < samples_per_block; sample_index++) {
            in_phase = sample_buffer[sample_index * 2 + 0];     // I component
            quadrature = sample_buffer[sample_index * 2 + 1];   // Q component
            block_amplitude_sum += sqrt(in_phase * in_phase + quadrature * quadrature);
        }
        
        // Write average amplitude to output file
        fprintf(output_file, "%d %f\n", current_block, block_amplitude_sum / samples_per_block);
        
        // Show progress every 20 blocks
        if (current_block % 20 == 0) {
            printf("\r%.1f%% done.", (float)current_block / number_of_blocks * 100.0);
            fflush(stdout);
        }
    }
    
    // Cleanup
    fclose(output_file);
    fclose(input_file);
    free(sample_buffer);
    
    return 0;
}
