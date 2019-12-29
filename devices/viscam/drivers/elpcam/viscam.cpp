#include <opencv/highgui.h>
#include <time.h>
#include "../viscam.h"

static CvCapture *cam;
long mean_exposure = 0;



/* Structures */
typedef struct {
	int milli;		/* milliseconds after second */
	int sec;		/* seconds after the minute */
	int min;		/* minutes after the hour */
	int hour;		/* hours since midnight */
	int day;		/* day of the month */
	int mon;		/* month of the year */
	int year;		/* years since year 0 */
} timeStruct;

/* POSIX VERSION */
int getTime(timeStruct * pTS);
int getTime(timeStruct * pTS)
{
	time_t seconds;
	long milliseconds;
	struct tm *tm;
	struct timespec spec;
	int stat;

	stat = clock_gettime(CLOCK_REALTIME, &spec);
	if (stat != 0) {
		fprintf(stderr, "clock_gettime failed. (posix) \n");
		return 1;
	}

	milliseconds = round(spec.tv_nsec / 1.0e6);
	seconds = spec.tv_sec;
	tm = gmtime(&seconds);

	pTS->year = tm->tm_year + 1900;
	pTS->mon = tm->tm_mon + 1;
	pTS->day = tm->tm_mday;
	pTS->hour = tm->tm_hour;
	pTS->min = tm->tm_min;
	pTS->sec = tm->tm_sec;
	pTS->milli = milliseconds;
	return 0;
}

long getTimeStamp(void);
long getTimeStamp(void)
{
	long mills = 0;
	timeStruct time;
	getTime(&time);

	mills = time.milli
		+ time.sec  * 1000
		+ time.min  * 1000 * 60
		+ time.hour * 1000 * 60 * 60
		+ time.day  * 1000 * 60 * 60 * 24
		+ time.mon  * 1000 * 60 * 60 * 24 * 30
		+ time.year * 1000 * 60 * 60 * 24 * 365
	;
	return mills;
}

int viscam_init(sVisCamStruct * viscam)
{
	int i;
	long noofmeanframes;
	long start = 0;
	/* open camera */
	cam = cvCaptureFromCAM(CV_CAP_ANY);
	if (!cam) {
		fprintf(stderr, "couldn't open viscam device\n");
		return -1;
	}

	/*
	 * Set viscam to the highest possible resolution by setting the
	 * resolution to some unreasonable high value which will be reduced
	 * to the max value by the device
	 */
	cvSetCaptureProperty(cam, CV_CAP_PROP_FRAME_WIDTH, 100000);
	cvSetCaptureProperty(cam, CV_CAP_PROP_FRAME_HEIGHT, 100000);
	viscam->width = cvGetCaptureProperty(cam, CV_CAP_PROP_FRAME_WIDTH);
	viscam->height = cvGetCaptureProperty(cam, CV_CAP_PROP_FRAME_HEIGHT);
	printf("set viscam to resolution %i x %i\n", viscam->width, viscam->height);

	// viscam->timestampBefore = (timeStruct *) malloc(sizeof(timeStruct));
	// viscam->timestampAfter = (timeStruct *) malloc(sizeof(timeStruct));

	/*
	 * Unfortunately, both the camera device and the v4l driver have
	 * frame buffers and since we can't reliably flush these buffers, we
	 * are not guaranteed to receive the actual current scene. In my
	 * measurements, this amounted to sometimes more than 13s lag which
	 * is unacceptable. To work around the issue we can measure the time
	 * it takes to request a frame and compare that to the exposure time
	 * of the image. Annoyingly, opencv cannot determine the exposure
	 * time for v4l viscams. The workaround to this is to measure a mean
	 * return of several consecutive frames and use that as the norm to
	 * compare to.
	 */

	/* throw away the first few buffers to force a clean buffer */
	for (i = 0; i < 10; i++) {
		cvQueryFrame(cam);
	}

	/* use some frames to get a mean return time */
	noofmeanframes = 5;
	for (i = 0; i < noofmeanframes; i++) {
		start = getTimeStamp();
		cvQueryFrame(cam);
		mean_exposure += (getTimeStamp() - start) / noofmeanframes;
	}

	printf("viscam mean exposure is %lu \n", mean_exposure);

	return 0;
}

int viscam_get(sVisCamStruct * viscam)
{
	IplImage *frame;
	// int stat = 0;
	long start, diff = 0;
	int i;

	/* if the time it takes to get a frame is a lot shorter than previously, there is something fishy going on; retry. */
	for (i = 0; i < 8 && diff < mean_exposure * .75; i++) {
		// stat = getTime(viscam->timestampBefore);
		// if (stat) {
		// 	fprintf(stderr, "couldn't get the time before requesting a viscam frame\n");
		// 	return -1;
		// }

		/* download image from camera */
		start = getTimeStamp();
		frame = cvQueryFrame(cam);
		if (!frame) {
			fprintf(stderr, "couldn't get a viscam frame\n");
			return -2;
		}
		diff = getTimeStamp() - start;

		printf("time to get viscam image: %lu \n", diff);
	}
	printf("discarded %i viscam frames \n", i);

	// stat = getTime(viscam->timestampAfter);
	// if (stat) {
	// 	fprintf(stderr, "couldn't get the time after requesting a viscam frame \n");
	// 	return -1;
	// }

	/* put image information into structure */
	viscam->buffer = frame->imageData;
	viscam->bufferSize = frame->imageSize;

	return 0;
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
int viscam_uninit(sVisCamStruct * viscam)
{
	cvReleaseCapture(&cam);
	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"
