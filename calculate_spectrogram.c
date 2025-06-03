#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include <fftw3.h>

#define MAX_FILENAME 256
#define MAX_OUTPUT_FILENAME 512  // Increased buffer size for output filename
#define M_PI 3.14159265358979323846

// Function to get base filename from path
char* get_basename(const char *path) {
    const char *last_slash = strrchr(path, '/');
    return last_slash ? (char*)(last_slash + 1) : (char*)path;
}

// Structure to hold FFTW plans and arrays
typedef struct {
    fftwf_complex *in;
    fftwf_complex *out;
    fftwf_plan p;
    float *window;
} fftw_data_t;

// Function to create and initialize FFTW data
fftw_data_t* init_fftw(int n) {
    fftw_data_t *data = (fftw_data_t*)malloc(sizeof(fftw_data_t));
    if (!data) {
        fprintf(stderr, "Error: Failed to allocate FFTW data structure\n");
        return NULL;
    }

    // Allocate arrays
    data->in = fftwf_alloc_complex(n);
    data->out = fftwf_alloc_complex(n);
    data->window = (float*)malloc(n * sizeof(float));
    
    if (!data->in || !data->out || !data->window) {
        fprintf(stderr, "Error: Failed to allocate FFTW arrays\n");
        free(data);
        return NULL;
    }

    // Create FFTW plan
    data->p = fftwf_plan_dft_1d(n, data->in, data->out, FFTW_FORWARD, FFTW_ESTIMATE);
    if (!data->p) {
        fprintf(stderr, "Error: Failed to create FFTW plan\n");
        free(data->in);
        free(data->out);
        free(data->window);
        free(data);
        return NULL;
    }

    // Create Hanning window
    for (int i = 0; i < n; i++) {
        data->window[i] = 0.5f * (1.0f - cosf(2.0f * M_PI * i / (n - 1)));
    }

    return data;
}

// Function to free FFTW data
void free_fftw(fftw_data_t *data) {
    if (data) {
        fftwf_destroy_plan(data->p);
        fftwf_free(data->in);
        fftwf_free(data->out);
        free(data->window);
        free(data);
    }
}

// Function to process a block of data
void process_block(fftw_data_t *data, float *block, int n, FILE *outfile) {
    // Apply window and copy to complex input array
    for (int i = 0; i < n; i++) {
        data->in[i] = block[i] * data->window[i];
    }

    // Execute FFT
    fftwf_execute(data->p);

    // Calculate power spectrum and write to file
    for (int i = 0; i < n/2 + 1; i++) {
        float real = crealf(data->out[i]);
        float imag = cimagf(data->out[i]);
        float power = real * real + imag * imag;
        float db = 10.0f * log10f(power + 1e-10f);  // Add small value to avoid log(0)
        fwrite(&db, sizeof(float), 1, outfile);
    }
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

    // Create output filename using only the base filename
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
    size_t required_length = strlen("spectrogram_") + strlen(filename_without_ext) + strlen(".f32") + 1;
    if (required_length > MAX_OUTPUT_FILENAME) {
        fprintf(stderr, "Error: Output filename would be too long (max %d characters)\n", MAX_OUTPUT_FILENAME - 1);
        return 1;
    }
    
    snprintf(outfile_name, MAX_OUTPUT_FILENAME, "spectrogram_%s.f32", filename_without_ext);
    FILE *outfile = fopen(outfile_name, "wb");
    if (!outfile) {
        fprintf(stderr, "Error: Could not open output file %s\n", outfile_name);
        fclose(infile);
        return 1;
    }

    // Write header information
    fwrite(&samples_per_block, sizeof(int), 1, outfile);

    // Initialize FFTW
    fftw_data_t *fftw_data = init_fftw(samples_per_block);
    if (!fftw_data) {
        fclose(infile);
        fclose(outfile);
        return 1;
    }

    // Process data in blocks
    float *block = (float*)malloc(samples_per_block * sizeof(float));
    if (!block) {
        fprintf(stderr, "Error: Failed to allocate block buffer\n");
        free_fftw(fftw_data);
        fclose(infile);
        fclose(outfile);
        return 1;
    }

    size_t num_blocks = 0;
    while (1) {
        // Read a block of data
        size_t read = fread(block, sizeof(float), samples_per_block, infile);
        if (read != samples_per_block) {
            break;
        }

        // Process the block
        process_block(fftw_data, block, samples_per_block, outfile);
        num_blocks++;

        if (num_blocks % 100 == 0) {
            printf("\rProcessed %zu blocks...", num_blocks);
            fflush(stdout);
        }
    }
    printf("\nProcessed %zu blocks total\n", num_blocks);

    // Cleanup
    free(block);
    free_fftw(fftw_data);
    fclose(infile);
    fclose(outfile);

    printf("Spectrogram data written to %s\n", outfile_name);
    return 0;
} 