#include "../spectrometershutter.h"
#include <cstdio>
#include <iostream>

#pragma GCC diagnostic ignored "-Wunused-parameter"
int spectrometershutter_init(sSpectrometershutter * config)
{
	return 0;
}

int spectrometershutter_setState(sSpectrometershutter * config, char * state)
{
	std::cout << "mock spectrometer shutter: " << state;
	return 0;
}

int spectrometershutter_uninit(sSpectrometershutter * config)
{
	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"
