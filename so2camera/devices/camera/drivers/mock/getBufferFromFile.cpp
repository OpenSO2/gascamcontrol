/* HEADER is N bytes
 * image size is  1344 * 1024 * 16/8
 */
#include <iostream>
#include <unistd.h>

short * getBufferFromFile(const char *filename, int offset, int* buffer);
short * getBufferFromFile(const char *filename, int offset, int* length)
{
	// unsigned int length;
	int read_bytes;

	FILE *f = fopen(filename, "rb");
	if (!f) {
		std::cerr << "failed to open file\n";
		return NULL;
	}

	(void)fseek(f, 0, SEEK_END);
	*length = (ftell(f) - offset);	/* substract header */
	if (*length < 1) {
		std::cerr << "file to small or unreadable\n";
		fclose(f);
		return NULL;
	}

	(void)fseek(f, offset, SEEK_SET);	/* offset for header */
	short * buffer = (short*)malloc(*length);
	if (!buffer) {
		std::cerr << "failed to create buffer\n";
		free(buffer);
		fclose(f);
		return NULL;
	}

	read_bytes = fread(buffer, sizeof(short), *length, f);
	if (*length != read_bytes * sizeof(short)) {
		std::cerr << "failed to read into buffer\n";
		free(buffer);
		fclose(f);
		return NULL;
	}

	if(buffer == NULL)
		std::cerr << "getBufferFromFile is NULL\n";

	fclose(f);

	return buffer;
}
