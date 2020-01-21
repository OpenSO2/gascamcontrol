#include <iostream>
#include <unistd.h>
#include "../viscam.h"

using namespace std;

static char *buffer;

#pragma GCC diagnostic ignored "-Wunused-parameter"
int viscam_init(sVisCamStruct * viscam)
{
	int stat = 0;
	int fsize = 0;

	/* open mock image */
	FILE *fid = fopen(VISCAM_MOCK_RAW, "rb");
	if (!fid) {
		std::cerr << "image " << VISCAM_MOCK_RAW << " could not be opened\n";
		return -1;
	}

	/* get filesize */
	fseek(fid, 0, SEEK_END);
	fsize = ftell(fid);
	rewind(fid);

	/* allocate buffer */
	buffer = (char *)malloc(sizeof(char) * fsize);
	if (buffer == NULL) {
		std::cerr << "error allocating enough memory \n";
		return -1;
	}

	stat = fread(buffer, 1, fsize, fid);
	if (stat != fsize) {
		std::cerr << "couldn't read mock viscam image\n";
		return -1;
	}
	fclose(fid);

	viscam->bufferSize = fsize;
	viscam->height = 720;
	viscam->width = 1280;

	return 0;
}

#pragma GCC diagnostic warning "-Wunused-parameter"

int viscam_get(sVisCamStruct * viscam)
{
	viscam->buffer = buffer;
	sleep(1);
	return 0;
}

#pragma GCC diagnostic ignored "-Wunused-parameter"
int viscam_uninit(sVisCamStruct * viscam)
{
	if (buffer != NULL) {
		free(buffer);
	}

	return 0;
}
#pragma GCC diagnostic warning "-Wunused-parameter"
