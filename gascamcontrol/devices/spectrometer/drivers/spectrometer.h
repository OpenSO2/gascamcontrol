#if !defined(spectrometerh)
#define spectrometerh 1

typedef struct {
	double *wavelengths;
	double *lastSpectrum;
	double *electronic_offset;
	double *dark_current;
	double max;
	int integration_time_micros;
	int spectrum_length;
	int scans;
} sSpectrometerStruct;

int spectrometer_init(sSpectrometerStruct *);
int spectrometer_get(sSpectrometerStruct *);
int spectrometer_uninit(sSpectrometerStruct *);

#endif
