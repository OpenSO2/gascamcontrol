#ifndef _camerashutter_
#define _camerashutter_

#define camerashutter_CLOSED_A 1
#define camerashutter_CLOSED_B 1
#define camerashutter_OPENED_A 2
#define camerashutter_OPENED_B 2

typedef struct {
	char *state;
	char *device;
} sCamerashutter;

int camerashutter_init(sCamerashutter *);
int camerashutter_send(int);
int camerashutter_setState(sCamerashutter *, char *);
int camerashutter_uninit(sCamerashutter *);


#endif
