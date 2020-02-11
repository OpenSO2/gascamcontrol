#include "../camera.h"
#include "opencv/highgui.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[])
{
	int stat = 0;
	char filename[256];
	FILE *fid;
	char *type;
	int generate_png = 1;
	static sParameterStruct sSO2Parameters;

	if (argc < 2) {
		printf("usage: %s <a|b>\n", argv[0]);
		return 1;
	}

	sSO2Parameters.dBufferlength = 1376256; // fixme this should be autoset
	sSO2Parameters.dFixTime = 0;
	sSO2Parameters.dExposureTime_a = 250000;
	sSO2Parameters.dExposureTime_b = 250000;
	sSO2Parameters.dExposureTime = 250000;
	sSO2Parameters.identifier = (char)argv[1][0];

	/* testing functions */
	printf("init:\n");
	stat = camera_init(&sSO2Parameters);
	if (stat) {
		printf("failed to init camera\n");
		return -1;
	}
  printf("init complete\n");

	/* autoset exposure */
	stat = camera_autosetExposure(&sSO2Parameters);
	if (stat) {
		printf("failed to find exposure\n");
		return -1;
	}

	/* trigger image and wait for result */
	stat = camera_get(&sSO2Parameters, 1);
	if (stat) {
		printf("failed to get image from camera\n");
		return -1;
	}

	if (argc == 3) {
		stat = sprintf(filename, "%s", argv[2]);
	} else {
		type = generate_png ? (char *)"png" : (char *)"raw";

		/* saving image */
		stat = sprintf(filename, "outfile.%s", type);
	}
	if (stat < 0) {
		return -1;
	}

	if (generate_png) {
		/* create new image to hold the loaded data */
		std::vector<short> vec;
		vec = std::vector<short>(sSO2Parameters.stBuffer, sSO2Parameters.stBuffer + sSO2Parameters.stBufferSize/sizeof(short));

    cv::Mat m = cv::Mat(1024, 1344, CV_16U);
		memcpy(m.data, vec.data(), vec.size()*sizeof(short));
		/* upsample image to use full 16bit range (the image will be very dark otherwise) */
		m = m * 16;
		cv::imwrite(filename, m);

	} else {
		fid = fopen(filename, "wb");
		stat = fwrite(sSO2Parameters.stBuffer, sizeof(char), 1344 * 1024, fid);
		if (stat != 1344 * 1024) {
			printf("failed to save image\n");
			printf("fwrite stat = %d\n", stat);
		} else {
			printf("IMAGE: %s saved successful\n", filename);
		}

		fclose(fid);
	}

	stat = camera_uninit(&sSO2Parameters);
	printf("end test programm\n");

	return 0;
}
