/**
 * Calculate Amplitude from I/Q Data
 * 
 * This program calculates the amplitude from I/Q data by computing √(I² + Q²) for each sample.
 * The amplitude values are written to a binary .f32 file for visualization.
 * 
 * Usage:
 *     ./calculate_amplitude <input_file> [samples_per_block]
 * 
 * Arguments:
 *     input_file: Path to the input I/Q data file
 *     samples_per_block: Optional number of samples to process in each block
 *                        If not provided, will be extracted from filename
 * 
 * Input Format:
 *     - Binary file containing interleaved I/Q samples as float32 values
 *     - Filename format: gqrx_YYYYMMDD_HHMMSS_FREQUENCY_SAMPLINGRATE_fc_OBJECT.raw
 * 
 * Output Format:
 *     - Binary file containing amplitude values as float32
 *     - Output filename: waterfall_<input_basename>.f32
 * 
 * Features:
 *     - Direct amplitude calculation from I/Q samples
 *     - Memory-efficient processing of large files
 *     - Automatic extraction of samples_per_block from filename
 *     - Progress reporting during processing
 *     - Output in linear scale (not dB)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>

#define MAX_FILENAME 256
#define MAX_OUTPUT_FILENAME 512

// Function to get base filename from path
char* get_basename(const char *path) {
    const char *last_slash = strrchr(path, '/');
    return last_slash ? (char*)(last_slash + 1) : (char*)path;
}

int main(int argc, char *argv[]) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s <input_file> [samples_per_block]\n", argv[0]);
        return 1;
    }

    // Get input filename and samples_per_block
    const char *input_file = argv[1];
    size_t samples_per_block;
    
    // Get samples_per_block from command line or filename
    if (argc == 3) {
        samples_per_block = atoi(argv[2]);
    } else {
        // Parse filename to extract samples_per_block
        // Format: gqrx_'start_date'_'start_time'_'frequency'_samples-per-block'_fc_'object'.raw
        const char *base_filename = get_basename(input_file);
        char filename_copy[256];  // Buffer for filename copy
        strncpy(filename_copy, base_filename, sizeof(filename_copy) - 1);
        filename_copy[sizeof(filename_copy) - 1] = '\0';  // Ensure null termination
        
        char *token = strtok(filename_copy, "_");
        int field_count = 0;
        while (token != NULL) {
            field_count++;
            if (field_count == 5) {  // samples-per-block is the 5th field
                samples_per_block = atoi(token);
                printf("Samples per block: %zu\n", samples_per_block);
                break;
            }
            token = strtok(NULL, "_");
        }
        
        if (field_count < 5) {
            printf("Error: Could not extract samples_per_block from filename\n");
            return 1;
        }
    }

    if (samples_per_block < 2) {
        fprintf(stderr, "Error: samples_per_block must be at least 2\n");
        return 1;
    }

    // Open input file
    FILE *infile = fopen(input_file, "rb");
    if (!infile) {
        fprintf(stderr, "Error: Could not open input file %s\n", input_file);
        return 1;
    }

    // Create output filename
    char outfile_name[MAX_OUTPUT_FILENAME];
    const char *base_filename = get_basename(input_file);
    
    // Remove .raw extension if present
    char filename_without_ext[MAX_FILENAME];
    strncpy(filename_without_ext, base_filename, sizeof(filename_without_ext) - 1);
    filename_without_ext[sizeof(filename_without_ext) - 1] = '\0';
    char *dot_position = strrchr(filename_without_ext, '.');
    if (dot_position != NULL && strcmp(dot_position, ".raw") == 0) {
        *dot_position = '\0';  // Terminate string at the dot
    }
    
    // Check if the output filename would be too long
    size_t required_length = strlen("waterfall_") + strlen(filename_without_ext) + strlen(".f32") + 1;
    if (required_length > MAX_OUTPUT_FILENAME) {
        fprintf(stderr, "Error: Output filename would be too long (max %d characters)\n", MAX_OUTPUT_FILENAME - 1);
        return 1;
    }
    
    snprintf(outfile_name, MAX_OUTPUT_FILENAME, "waterfall_%s.f32", filename_without_ext);
    FILE *outfile = fopen(outfile_name, "wb");
    if (!outfile) {
        fprintf(stderr, "Error: Could not open output file %s\n", outfile_name);
        fclose(infile);
        return 1;
    }

    // Write header information
    // fwrite(&samples_per_block, sizeof(int), 1, outfile);

    // Process data in blocks
    float *block = (float*)malloc(samples_per_block * 2 * sizeof(float));  // *2 for I and Q
    if (!block) {
        fprintf(stderr, "Error: Failed to allocate block buffer\n");
        fclose(infile);
        fclose(outfile);
        return 1;
    }

    size_t num_blocks = 0;
    while (1) {
        // Read a block of I/Q data
        size_t read = fread(block, sizeof(float), samples_per_block * 2, infile);
        if (read != samples_per_block * 2) {
            break;
        }

        // Calculate amplitude for each I/Q pair and write to output file
        for (size_t i = 0; i < samples_per_block; i++) {
            float in_phase = block[i * 2];
            float quadrature = block[i * 2 + 1];
            float amplitude = sqrtf(in_phase * in_phase + quadrature * quadrature);
            fwrite(&amplitude, sizeof(float), 1, outfile);
        }

        num_blocks++;

        if (num_blocks % 100 == 0) {
            printf("\rProcessed %zu blocks...", num_blocks);
            fflush(stdout);
        }
    }
    printf("\nProcessed %zu blocks total\n", num_blocks);

    // Cleanup
    free(block);
    fclose(infile);
    fclose(outfile);

    printf("Waterfall data written to %s\n", outfile_name);
    return 0;
}