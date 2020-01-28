#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <iostream>
#include "../spectrometer.h"

static double *wavelengths = NULL;
static double *spectrum = NULL;

int spectrometer_init(sSpectrometerStruct * spectro)
{
	int i;
	int number_of_lines = 0;
	char line[512];

	FILE *f = fopen(SPECTROMETER_MOCK_WAVELENGTHS, "r");
	if (!f) {
		std::cerr << "failed to open file\n";
		return 1;
	}

	while (fgets(line, 512, f) != NULL) {
		number_of_lines++;
	}

	wavelengths = (double *)calloc(number_of_lines, sizeof(double));
	spectrum = (double *)calloc(number_of_lines, sizeof(double));

	spectro->spectrum_length = number_of_lines;
	spectro->max = 4096;

	/* rewind file */
	fseek(f, 0, SEEK_SET);

	i = 0;
	while (fgets(line, 512, f) != NULL) {
		wavelengths[i++] = atof(line);
	}

	fclose(f);

	f = fopen(SPECTROMETER_MOCK_SPECTRUM, "r");
	if (!f) {
		std::cerr << "failed to open file\n";
		return 1;
	}

	i = 0;
	while (fgets(line, 512, f) != NULL) {
		spectrum[i++] = atof(line);
	}

	fclose(f);

	return 0;
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
int spectrometer_uninit(sSpectrometerStruct * spectro)
{
	free(wavelengths);
	free(spectrum);
	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"

#pragma GCC diagnostic ignored "-Wunused-parameter"
int spectrometer_get(sSpectrometerStruct * spectro)
{
	sleep(spectro->integration_time_micros / 1000000);
	spectro->lastSpectrum = spectrum;
	spectro->wavelengths = wavelengths;

	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"
