/* HEADER is N bytes
 * image size is  1344 * 1024 * 16/8
 */
#include <iostream>
#include <unistd.h>

short * getBufferFromFile(const char *filename, int offset, int* buffer);
short * getBufferFromFile(const char *filename, int offset, int* length)
{
	fprintf(stderr, "getBufferFromFile \n");

	// unsigned int length;
	int read_bytes;

	FILE *f = fopen(filename, "rb");
	if (!f) {
		fprintf(stderr, "failed to open file\n");
		return NULL;
	}

	fprintf(stderr, "getBufferFromFile 2 \n");
	(void)fseek(f, 0, SEEK_END);
	*length = (ftell(f) - offset);	/* substract header */
	if (*length < 1) {
		fprintf(stderr, "file to small or unreadable\n");
		fclose(f);
		return NULL;
	}

	fprintf(stderr, "getBufferFromFile, length: %i %i\n", *length, *length/sizeof(int)/1344);
	(void)fseek(f, offset, SEEK_SET);	/* offset for header */
	short * buffer = (short*)malloc(*length);
	if (!buffer) {
		fprintf(stderr, "failed to create buffer\n");
		free(buffer);
		fclose(f);
		return NULL;
	}

	fprintf(stderr, "getBufferFromFile 4 \n");
	read_bytes = fread(buffer, sizeof(short), *length, f);
	if (*length != read_bytes * sizeof(short)) {
		fprintf(stderr, "failed to read into buffer\n");
		free(buffer);
		fclose(f);
		return NULL;
	}

	if(buffer == NULL)
		fprintf(stderr, "getBufferFromFile is NULL\n");

	fprintf(stderr, "getBufferFromFile 5 \n");
	fclose(f);
	fprintf(stderr, "getBufferFromFile length %i \n", *length);

	return buffer;
}
