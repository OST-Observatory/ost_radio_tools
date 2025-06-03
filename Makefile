# Compiler settings
CC = gcc
CFLAGS = -O3 -Wall -Wextra
LDFLAGS = -lm -lfftw3f

# Source files
SRCS = calculate_amplitude_sum.c \
       calculate_power.c \
       calculate_power_spectrum.c \
       calculate_integrated_power_spectrum.c \
       calculate_spectrogram.c \
       calculate_amplitude.c

# Executables
EXECS = calculate_amplitude_sum \
        calculate_power \
        calculate_power_spectrum \
        calculate_integrated_power_spectrum \
        calculate_spectrogram \
        calculate_amplitude

all: $(EXECS)

# Compile rules
calculate_amplitude_sum: calculate_amplitude_sum.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

calculate_power: calculate_power.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

calculate_power_spectrum: calculate_power_spectrum.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

calculate_integrated_power_spectrum: calculate_integrated_power_spectrum.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

calculate_spectrogram: calculate_spectrogram.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

calculate_amplitude: calculate_amplitude.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f $(EXECS)

.PHONY: all clean 