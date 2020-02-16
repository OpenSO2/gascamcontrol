#include <unistd.h>               /* usleep */
#include <string.h>		/* String function definitions */
#include "../spectrometershutter.h"

#include <fcntl.h>
#include <stdio.h>
#include <termios.h>
#include <iostream>

#define SPECTROMETER_SHUTTER_OPEN 7100
#define SPECTROMETER_SHUTTER_CLOSED 5400

static int fd = -1;

/*
 * Sets the target of a Maestro channel.
 * See the "Serial Servo Commands" section of the user's guide.
 * The units of 'target' are quarter-microseconds.
 */
int maestroSetTarget(int channel, unsigned short target);
int maestroSetTarget(int channel, unsigned short target)
{
	unsigned char command[] = { 0x84, channel, target & 0x7F, target >> 7 & 0x7F };
	if (write(fd, command, sizeof(command)) == -1) {
		std::cout << "error sending command to spectrometer shutter\n";
		return -1;
	}
	return 0;
}

int spectrometershutter_init(sSpectrometershutter * config)
{
	struct termios options;

	if (config->channel > 5 || config->channel < 0) {
		std::cout << "spectrometer_shutter channel insane\n";
		return 2;
	}
	std::cout << "opening device " << config->device << " on channel " << config->channel << "\n";

	fd = open(config->device, O_RDWR | O_NOCTTY);
	if (fd == -1) {
		std::cerr << "could not open spectrometer_shutter device\n";
		return 1;
	}

	tcgetattr(fd, &options);
	options.c_iflag &= ~(INLCR | IGNCR | ICRNL | IXON | IXOFF);
	options.c_oflag &= ~(ONLCR | OCRNL);
	options.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
	tcsetattr(fd, TCSANOW, &options);

	return 0;
}

int spectrometershutter_setState(sSpectrometershutter * config, char * state)
{
	int setting = strcmp(state, "open") ? SPECTROMETER_SHUTTER_OPEN : SPECTROMETER_SHUTTER_CLOSED;
	return maestroSetTarget(config->channel, setting);
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
int spectrometershutter_uninit(sSpectrometershutter * config)
{
	if (fd != -1)
		return close(fd);
	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"
