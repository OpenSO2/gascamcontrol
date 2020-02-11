#ifndef _spectrometer_shutter_
#define _spectrometer_shutter_

typedef struct {
	char *state;
  char *device;
	int channel;
} sSpectrometershutter;

int spectrometershutter_init(sSpectrometershutter *);
int spectrometershutter_setState(sSpectrometershutter *, char * state);
int spectrometershutter_uninit(sSpectrometershutter *);
#endif
