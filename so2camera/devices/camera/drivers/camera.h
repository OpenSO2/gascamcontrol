/*
 * This implements the actual camera/framegrabber interface and will
 * mostly be a framegrabber SDK wrapper to allow for the undelying
 * SDK to be changed. This can also be used to mock the hardware
 * functions for unit/integration testing.
 * To support other framegrabbers, this file will have to be reimplemented.
 *
 *
 * A typical life cycle would be
 *
 * camera_init
 * camera_config
 * camera_setExposure
 *
 * camera_trigger
 * camera_get
 *
 * camera_abort
 * camera_uninit
 */
#ifndef _CAMERA_
#define _CAMERA_

// #ifdef __cplusplus
// extern "C" {
// #endif

/* Camera parameters */
typedef struct {
	/* A handle to identify the camera */
	unsigned long hCamera;

	/* contains the Exposuretime in [ms] */
	double exposuretime;

	int width;
	int height;

	/* Pointer to image buffer */
	short *stBuffer;

  /* Size of image buffer */
	int stBufferSize;

	/* ~Callback stuff~ */

	/* Event Flags */
	volatile unsigned long fBufferReady;

	/* Control Flags */
	volatile unsigned long fFifoOverFlow;

	/* Camera identifier */
	char identifier;

	/* flag to indicate that the current image is a dark image */
	int dark;

	/*
 	 * A switch to set the exposuretime fix to the value given in
 	 * the config file
 	 */
	 int dFixTime;

	/* Number of pixels in 1 Image */
	int dBufferlength;

	/* exposure time in [us] */
	double dExposureTime_a;
	double dExposureTime_b;

	/* contains the Exposuretime in [ms] */
	double dExposureTime;

	/* flag. If falseish, debugging output is suppressed */
	int debug;

} sParameterStruct;


/**
 * inits the camera/framegrabber
 */
int camera_init(sParameterStruct *);

/**
 * stops (uninits) the camera/framegrabber and does neccesarry clean up
 */
int camera_uninit(sParameterStruct *);

/**
 * aquires one image/frame from the camera/framegrabber
 */
int camera_get(sParameterStruct *, int);

/**
 * abort the current aquisition
 */
int camera_abort(sParameterStruct *);

int camera_setExposure(sParameterStruct *);
int camera_autosetExposure(sParameterStruct *);
// int camera_config(sParameterStruct *);

// #ifdef __cplusplus
// }
// #endif
#endif
