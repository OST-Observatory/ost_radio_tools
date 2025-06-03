/**
 * calculate_power.c
 *
 * This program calculates power from I/Q data.
 * It reads I/Q data from a binary file, calculates the power (I² + Q²)
 * for each sample, and optionally sums these values over blocks.
 *
 * Usage:
 *     ./calculate_power <input_file> [samples_per_block] [--output-type TYPE]
 *
 * Arguments:
 *     input_file: Path to the input I/Q data file
 *     samples_per_block (optional): Number of samples to process in each block
 *     --output-type TYPE: Type of output to generate (default: sum)
 *         sum: Only write summed power values to .dat file (default)
 *         raw: Only write raw power values to .f32 file
 *         both: Write both summed and raw power values
 *
 * The program will:
 * 1. Read I/Q data from the input file
 * 2. Calculate power (I² + Q²) for each sample
 * 3. Write power values according to the output type:
 *    - For 'raw' or 'both': Write raw power values to a .f32 file
 *    - For 'sum' or 'both': Write summed power values to a .dat file
 *
 * Example:
 *     ./calculate_power gqrx_20250404_084805_1419390700_1800000_fc_sun.raw 1800000
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>

#define MAX_FILENAME 256
#define MAX_OUTPUT_FILENAME 512

// Output type enumeration
typedef enum {
    OUTPUT_SUM,    // Only write summed power values
    OUTPUT_RAW,    // Only write raw power values
    OUTPUT_BOTH    // Write both summed and raw power values
} OutputType;

// Function to parse output type from string
OutputType parse_output_type(const char *type_str) {
    if (strcmp(type_str, "sum") == 0) return OUTPUT_SUM;
    if (strcmp(type_str, "raw") == 0) return OUTPUT_RAW;
    if (strcmp(type_str, "both") == 0) return OUTPUT_BOTH;
    return OUTPUT_SUM;  // Default to sum if invalid
}

// Function to get base filename from path
char* get_basename(const char *path) {
    const char *last_slash = strrchr(path, '/');
    return last_slash ? (char*)(last_slash + 1) : (char*)path;
}

int main(int argc, char *argv[]) {
    FILE *infile, *outfile = NULL, *sumfile = NULL;
    float *buffer;
    size_t samples_per_block = 0;
    size_t num_blocks = 0;
    OutputType output_type = OUTPUT_SUM;  // Default to sum output

    // Parse command line arguments
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_file> [samples_per_block] [--output-type TYPE]\n", argv[0]);
        fprintf(stderr, "Output types: sum, raw, both (default)\n");
        return 1;
    }

    // Parse output type if specified
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--output-type") == 0 && i + 1 < argc) {
            output_type = parse_output_type(argv[i + 1]);
            // Remove the processed arguments
            for (int j = i; j < argc - 2; j++) {
                argv[j] = argv[j + 2];
            }
            argc -= 2;
            break;
        }
    }

    // Open input file
    infile = fopen(argv[1], "rb");
    if (!infile) {
        fprintf(stderr, "Error: Could not open input file\n");
        return 1;
    }

    // Get samples_per_block from command line or filename
    if (argc > 2) {
        samples_per_block = atoi(argv[2]);
    } else {
        // Extract from filename
        const char *filename = strrchr(argv[1], '/');
        filename = filename ? filename + 1 : argv[1];
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
    }

    if (samples_per_block == 0) {
        fprintf(stderr, "Error: Invalid samples_per_block\n");
        fclose(infile);
        return 1;
    }

    // Allocate buffer
    buffer = malloc(2 * samples_per_block * sizeof(float));
    if (!buffer) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        fclose(infile);
        return 1;
    }

    // Generate output filenames
    char *base = strrchr(argv[1], '/');
    base = base ? base + 1 : argv[1];
    char *dot = strrchr(base, '.');
    char base_noext[256];
    if (dot) {
        strncpy(base_noext, base, dot - base);
        base_noext[dot - base] = '\0';
    } else {
        strncpy(base_noext, base, sizeof(base_noext) - 1);
        base_noext[sizeof(base_noext) - 1] = '\0';
    }

    // Open output files based on output type
    if (output_type == OUTPUT_RAW || output_type == OUTPUT_BOTH) {
        char out_filename[512];
        snprintf(out_filename, sizeof(out_filename), "power_%s.f32", base_noext);
        outfile = fopen(out_filename, "wb");
        if (!outfile) {
            fprintf(stderr, "Error: Could not open output file\n");
            free(buffer);
            fclose(infile);
            return 1;
        }
    }

    if (output_type == OUTPUT_SUM || output_type == OUTPUT_BOTH) {
        char sum_filename[512];
        snprintf(sum_filename, sizeof(sum_filename), "power_%s.dat", base_noext);
        sumfile = fopen(sum_filename, "w");
        if (!sumfile) {
            fprintf(stderr, "Error: Could not open sum file\n");
            if (outfile) fclose(outfile);
            free(buffer);
            fclose(infile);
            return 1;
        }
    }

    // Process data
    while (fread(buffer, sizeof(float), 2 * samples_per_block, infile) == 2 * samples_per_block) {
        float block_sum = 0.0f;

        for (size_t i = 0; i < samples_per_block; i++) {
            float i_val = buffer[2*i];
            float q_val = buffer[2*i + 1];
            float power = i_val * i_val + q_val * q_val;

            if (output_type == OUTPUT_RAW || output_type == OUTPUT_BOTH) {
                fwrite(&power, sizeof(float), 1, outfile);
            }
            if (output_type == OUTPUT_SUM || output_type == OUTPUT_BOTH) {
                block_sum += power;
            }
        }

        if (output_type == OUTPUT_SUM || output_type == OUTPUT_BOTH) {
            fprintf(sumfile, "%zu\t%f\n", num_blocks, block_sum);
        }

        num_blocks++;
    }

    // Cleanup
    fclose(infile);
    if (outfile) fclose(outfile);
    if (sumfile) fclose(sumfile);
    free(buffer);

    printf("Processed %zu blocks\n", num_blocks);
    if (output_type == OUTPUT_RAW || output_type == OUTPUT_BOTH) {
        printf("Raw power values written to: power_%s.f32\n", base_noext);
    }
    if (output_type == OUTPUT_SUM || output_type == OUTPUT_BOTH) {
        printf("Summed power values written to: power_%s.dat\n", base_noext);
    }

    return 0;
} 