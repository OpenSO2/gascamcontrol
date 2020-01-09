#include <unistd.h>               /* usleep */
#include "../camerashutter.h"

#pragma GCC diagnostic ignored "-Wunused-parameter"
int camerashutter_init(sCamerashutter * camerashutter)
{
	return 0;
}

int camerashutter_setState(sCamerashutter * camerashutter, char * state)
{
	camerashutter_send(1);
}

int camerashutter_send(int position)
{
	usleep(1000*2000);
	// sleepMs(2000);
	return 0;
}

int camerashutter_uninit(sCamerashutter * camerashutter)
{
	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"
