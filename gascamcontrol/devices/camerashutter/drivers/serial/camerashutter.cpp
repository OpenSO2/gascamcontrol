#include <unistd.h>               /* usleep */
#include <stdio.h>		/* Standard input/output definitions */
#include "../camerashutter.h"

#include <string.h>		/* String function definitions */
#include <fcntl.h>		/* File control definitions */
#include <errno.h>		/* Error number definitions */
#include <termios.h>		/* POSIX terminal control definitions */
#include <iostream>

static int fd = -1;		/* File descriptor for the port */

int camerashutter_init(sCamerashutter * camerashutter)
{
	fd = open(camerashutter->device, O_RDWR | O_NOCTTY | O_NDELAY);
	return fd == -1 ? 1 : 0;
}

int camerashutter_setState(sCamerashutter * camerashutter, char * state)
{
	camerashutter_send(strcmp(state, "open") ? 1 : 2);
}

/* position: o c */
int camerashutter_send(int position)
{
	int i;
	int bytes_to_send = 1;
	char buffer[80] = "";

	std::cout << "write to camerashutter: " << position;
	write(fd, &position, bytes_to_send);
	for (i = 0;; i++) {
		usleep(1000*100);
		read(fd, buffer, 80);

		if (strstr(buffer, "done") != NULL) {
			std::cout << "waited " << i << " cycles per 100ms for camerashutter";
			return 0;
		}
	}
	return 0;
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
int camerashutter_uninit(sCamerashutter * camerashutter)
{
	if (fd != -1)
		return close(fd);
	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"
