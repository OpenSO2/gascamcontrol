/*
 * This file provides support for the Silicon Active framegrabber and
 * the Hamamatsu C8484-C16 camera via the PHX SDK, which is not part of
 * this program and has to be acquired and installed separately.
 *
 * The C8484-16C actually supports two modes for exposure:
 * frame blanking
 *   exposure time = n * 83.7ms   n = 1..12                =>  83.7 .. 1004.4ms
 *   n = exposure time / 83700
 * electronic shutter
 *   exposure time = 12.4us + (n-1)*79.275us, n = 1..1055  =>  0.0124 .. 83.7268ms
 *   n = (exposure time - 12.4)/79.275 + 1
 */
#include<phx_api.h>
#include<phx_os.h>
#include"../camera.h"

/* prototypes for private functions */
int set_mode_speed(tHandle, char, char[9]);
int calc_mode_speed(double, double *, char *, char[9]);

#include"exposure.c"

void internalCallback(tHandle hCamera, ui32 dwInterruptMask, void *params);
static int sendMessage(tHandle hCamera, ui8 * inputBuffer);
int setup_camera(sParameterStruct * sSO2Parameters);

int camera_abort(sParameterStruct * sSO2Parameters)
{
	tHandle hCamera = sSO2Parameters->hCamera;
	return PHX_Acquire(hCamera, PHX_ABORT, NULL);
}

int camera_uninit(sParameterStruct * sSO2Parameters)
{
	tHandle hCamera = sSO2Parameters->hCamera;
	return PHX_CameraRelease(&hCamera);
}

int camera_get(sParameterStruct * sSO2Parameters, int waiter = 1)
{
	sSO2Parameters->fBufferReady = (1 == 0);
#pragma GCC diagnostic ignored "-Wpedantic"
	PHX_Acquire(sSO2Parameters->hCamera, PHX_START, (void *)internalCallback);
#pragma GCC diagnostic warning "-Wpedantic"

	if (waiter) {
		/* if theres no callback, this function will work synchronously
		 * and wait for the return of the image buffer
		 */
		while (!sSO2Parameters->fBufferReady) {
			usleep(1000);
		}

		sSO2Parameters->dBufferlength = 1376256; // FIXME, thats just weird
		sSO2Parameters->stBufferSize = 1376256*2;
		sSO2Parameters->width = 1344;
		sSO2Parameters->height = 1024;

		camera_abort(sSO2Parameters);
	}

	return 0;
}

int camera_autosetExposure(sParameterStruct * sSO2Parameters)
{
	int status = 0;
  sSO2Parameters->dExposureTime = sSO2Parameters->exposuretime;  // FIXME: thats stupid. dont be stupid.
	status = getExposureTime(sSO2Parameters);
	if (status) {
		std:cerr << "exposure time couldn't be retrieved\n";
		return status;
	}

	status = camera_setExposure(sSO2Parameters);
	if (status) {
		std:cerr << "exposure time wasn't set\n";
		return status;
	}

	return status;
}

int camera_setExposure(sParameterStruct * sSO2Parameters)
{
	double actualExposureTime;
	double exposureTime = sSO2Parameters->dExposureTime;
	int eStat = PHX_OK;
	char speed[9];
	char m;

	/* before doing anything check if exposure time is within the limits */
	if (exposureTime < 2.4 || exposureTime > 1004400.) {
		std:cerr << "Exposure time declared in Configfile is out of range: 2.4us < Exposure Time > 1004.4ms";
		return PHX_ERROR_OUT_OF_RANGE;
	}
	calc_mode_speed(exposureTime, &actualExposureTime, &m, speed);
	sSO2Parameters->dExposureTime = actualExposureTime;	/* update struct to the actual exposure time */
	if (m == 'S') {
		std:cerr << "Camera " << sSO2Parameters->identifier << " uses electronic shutter. Exposure was set to approx. " << exposureTime << " us which calculates to " << actualExposureTime << "\n";
	} else {
		std:cerr << "Camera " << sSO2Parameters->identifier << " uses frameblanking. Exposure was set to approx. " << exposureTime << " us which calculates to " << actualExposureTime  << "\n";
	}

	eStat = set_mode_speed(sSO2Parameters->hCamera, m, speed);
	return eStat;
}

int calc_mode_speed(double exposureTime, double *actualExposureTime, char *m, char speed[9])
{
	int n = 1;
	/* S Shutter, F frameblanking */
	if (exposureTime <= 83560.) {
		/* ELECTRONIC SHUTTER, Shutter speed: 1 - 1055 */
		n = round((exposureTime - 12.4) / 79.275 + 1);
		sprintf(speed, "SHT %d\r", n);
		*m = 'S';
		*actualExposureTime = 12.4 + (n - 1) * 79.275, n;
	} else {
		/* FRAME BLANKING, number of frames: 1 - 12 */
		n = round(exposureTime / 83700.);
		sprintf(speed, "FBL %d\r", n);
		*m = 'F';
		*actualExposureTime = n * 83700, n;
	}
	return 0;
}

int set_mode_speed(tHandle hCamera, char m, char speed[9])
{
	int eStat = PHX_OK;
	char mode[8];
	sprintf(mode, "NMD %c\r", m);

	eStat = sendMessage(hCamera, (ui8 *) mode);
	if (PHX_OK != eStat) {
		std:cerr << "Setting camera mode failed\n";
		return eStat;
	}

	eStat = sendMessage(hCamera, (ui8 *) speed);
	if (PHX_OK != eStat) {
		std:cerr << "setting shutter to " << speed << " failed\n";
		return eStat;
	}
	return eStat;
}

int camera_init(sParameterStruct * sSO2Parameters)
{
	etStat eStat = PHX_OK;
	int channel = sSO2Parameters->identifier == 'a' ? PHX_CHANNEL_A : PHX_CHANNEL_B;

	/* Load the framegrabber with the phoenix configuration file. This function sets the necessary camera handles */
	eStat = PHX_CameraConfigLoad(&sSO2Parameters->hCamera,
		CAMERA_PCF_FILE,
		(etCamConfigLoad) channel,
		// (etCamConfigLoad) PHX_BOARD_AUTO | PHX_DIGITAL | channel | PHX_NO_RECONFIGURE | 1,
		&PHX_ErrHandlerDefault);
	if (PHX_OK != eStat) {
		std::cerr << "loading camera config failed\n";
		return eStat;
	}

	/* Setup our own event context */
	eStat = PHX_ParameterSet(sSO2Parameters->hCamera, PHX_EVENT_CONTEXT, (void *)sSO2Parameters);
	if (PHX_OK != eStat) {
		std::cerr << "Setup the control flags structure failed\n";
		return eStat;
	}

	std:cout << "configuring of the frame grabber was successful\n";

	return setup_camera(sSO2Parameters);
}

/*
 * The following functions are phx specific and not exposed
 */

int setup_camera(sParameterStruct * sSO2Parameters)
{
	int eStat = PHX_OK;
	tHandle hCamera = sSO2Parameters->hCamera;

	/* initialize default values */
	eStat = sendMessage(hCamera, (ui8 *) "INI\r");
	if (PHX_OK != eStat) {
		std::cerr << "sending INI to camera was unsuccessful\n";
		return eStat;
	}
	/* freerunning or external control mode: */
	/* N freerun mode, E external */
	eStat = sendMessage(hCamera, (ui8 *) "AMD N\r");
	if (PHX_OK != eStat) {
		std::cerr << "sending AMD N to camera was unsuccessful\n";
		return eStat;
	}
	/* scanning mode: N Normal, S superpixel */
	eStat = sendMessage(hCamera, (ui8 *) "SMD N\r");
	if (PHX_OK != eStat) {
		std::cerr << "sending SMD N to camera was unsuccessful\n";
		return eStat;
	}
	/* horizontal pixel output: M = 1344 */
	eStat = sendMessage(hCamera, (ui8 *) "SHA M\r");
	if (PHX_OK != eStat) {
		std::cerr << "sending SHA M to camera was unsuccessful\n";
		return eStat;
	}
	/* contrast enhancement gain: low */
	/* CEG L CONTRAST ENHANCEMENT GAIN  (CEG L: 0dB) (CEG H: 14dB) */
	std::cout << "set contrast enhancement gain to LOW\n");
	eStat = sendMessage(hCamera, (ui8 *) "CEG L\r");
	if (PHX_OK != eStat) {
		std::cerr << "sending CEG L to camera was unsuccessful\n";
		return eStat;
	}

	std::cout << "configuration of camera was successful\n";
	return eStat;
}

void internalCallback(tHandle hCamera, ui32 dwInterruptMask, void *params)
{
	stImageBuff buffythevampireslayer;
	etStat eStat;
	sParameterStruct *sSO2Parameters = (sParameterStruct *) params;

	/* Fifo Overflow */
	if (PHX_INTRPT_FIFO_OVERFLOW & dwInterruptMask) {
		std::cerr << "a fifo overflow occured.\n";
	}

	/* Handle the Buffer Ready event */
	if (PHX_INTRPT_BUFFER_READY & dwInterruptMask) {
		eStat = PHX_Acquire(hCamera, PHX_BUFFER_GET, &buffythevampireslayer);
		if (PHX_OK != eStat) {
			std::cerr << "frame couldn't be aquired\n";
		}

		sSO2Parameters->stBuffer = (short int*)buffythevampireslayer.pvAddress;
		sSO2Parameters->hCamera = hCamera;
		sSO2Parameters->fBufferReady = (1 == 1);
	} else {
		std::cerr << "phx callback called but frame was not aquired\n";
	}
}

static int sendMessage(tHandle hCamera, ui8 * msg)
{
	bool eStat = !PHX_OK;
	int i;
	int sleepCycleCounter = 1;
	int timeout = 500;
	ui8 recv[256];
	ui32 j, recvLength;
	ui32 msgLength = strlen((const char *)msg);

	/* 3 tries before the sending of of the message is considered failed */
	for (i = 0; i < 3; i++) {
		/* Transmit the serial data to the camera */
		eStat = PHX_CommsTransmit(hCamera, msg, &msgLength, timeout);
		if (PHX_OK != eStat) {
			std::cerr << "PHX_CommsTransmit() failed\n";
			continue;	/* short circuit */
		}

		/* if transmitting was successful program waits for incoming messages
		 * 0.5s is a good compromise between speed and reliability
		 */
		do {
			_PHX_SleepMs(timeout / 50);
			sleepCycleCounter++;
			/* Check how many characters are waiting to be read */
			eStat = PHX_ParameterGet(hCamera, PHX_COMMS_INCOMING, &recvLength);
			/* create a timeout signal if 0.5s are over and no data was received */
			if (sleepCycleCounter > (timeout / 10))
				eStat = PHX_WARNING_TIMEOUT;
		} while (0 == recvLength && PHX_OK == eStat);

		if (PHX_OK != eStat) {
			std::cerr << "nothing was received from camera\n";
			continue;	/* short circuit */
		}

		/* if data is received, download the data */
		eStat = PHX_CommsReceive(hCamera, recv, &recvLength, timeout);
		if (PHX_OK != eStat) {
			std::cerr << "nothing was received from camera\n";
			continue;	/* short circuit */
		}

		/* if cameras answer equals input string, exit successful */
		if (strncmp((const char *)msg, (const char *)msg, msgLength)) {
			std::cerr << "String send and string received were not equal.\n";
			continue;	/* short circuit */
		}
		/* remove carriage return character from string for logging */
		for (j = 0; j < recvLength; j++)
			recv[j] = recv[j] == '\r' ? ' ' : recv[j];
		// printf("send message: %s was successful\n", recv);
		return 0;	/* here return of SUCCESS */
	}

	std::cerr << "sending message failed 3 times\n";
	return -1;
}
