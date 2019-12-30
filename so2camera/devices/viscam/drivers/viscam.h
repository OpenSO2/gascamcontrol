#ifndef _VISCAM_H_
#define _VISCAM_H_

#ifdef __cplusplus
extern "C" {
#endif


/* Viscam parameters */
typedef struct {
	/* Pointer to image buffer x*y*24 RAW */
	char *buffer;

	/* Size of buffer in bytes */
	int bufferSize;

	/* Image height */
	int height;

	/* Image width */
	int width;
} sVisCamStruct;

int viscam_init(sVisCamStruct *);
int viscam_get(sVisCamStruct *);
int viscam_uninit(sVisCamStruct *);

#ifdef __cplusplus
}
#endif
#endif
