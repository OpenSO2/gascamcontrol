/*
 * mock for camera
 *
 */

/* ignore unused parameters in this file */
#pragma GCC diagnostic ignored "-Wunused-parameter"

#include <iostream>
#include <unistd.h>

#ifdef WIN
#include<windows.h>
#else
#include<pthread.h>
#endif

#include<string.h>
#include<stdio.h>
#include<stdlib.h>
#include "../camera.h"

#include "getBufferFromFile.cpp"

/* local vars and prototypes */
static int bufferSetA;
static int bufferSetB;
struct data_struct {
    void (*callback)(sParameterStruct * sSO2Parameters);
    sParameterStruct *sSO2Parameters;
};

struct data_struct *g_data_struct_a;
struct data_struct *g_data_struct_b;
#ifdef WIN
HANDLE thread;
#else
pthread_t thread_id_a = 0;
pthread_t thread_id_b = 0;
#endif

/* public */
int camera_init(sParameterStruct * sSO2Parameters)
{
    bufferSetA = 0;
    bufferSetB = 0;
    if (sSO2Parameters->identifier == 'a') {
        g_data_struct_a = (struct data_struct *)calloc(1, sizeof(*g_data_struct_a));
    } else {
        g_data_struct_b = (struct data_struct *)calloc(1, sizeof(*g_data_struct_b));
    }

    return 0;
}

int camera_abort(sParameterStruct * sSO2Parameters)
{
#ifdef POSIX
    void *res;

    if (thread_id_a) {
        pthread_cancel(thread_id_a);
        pthread_join(thread_id_a, &res);
    }

    if (thread_id_b) {
        pthread_cancel(thread_id_b);
        pthread_join(thread_id_b, &res);
    }
#endif
    return 0;
}

int camera_uninit(sParameterStruct * sSO2Parameters)
{
    if (sSO2Parameters->identifier == 'a') {
         free(g_data_struct_a);
    } else {
        free(g_data_struct_b);
    }
    return 0;
}

int camera_get(sParameterStruct * sSO2Parameters, int waiter)
{
    std::cout << "! Mocking camera ! No real measurements are taken\n";
    const char *filename;
    short *stBuffer = NULL;
    int bufferSet = 0;
    int stBufferSize = 0;

    if (sSO2Parameters->identifier == 'a') {
        bufferSet = bufferSetA;
        bufferSetA = 1;
        filename = sSO2Parameters->dark ? CAMERA_MOCK_A_RAW_DARK : CAMERA_MOCK_A_RAW;
    } else {
        bufferSet = bufferSetB;
        bufferSetB = 1;
        filename = sSO2Parameters->dark ? CAMERA_MOCK_B_RAW_DARK : CAMERA_MOCK_B_RAW;
    }

    if (bufferSet == 1)
        free(sSO2Parameters->stBuffer);

    stBuffer = getBufferFromFile(filename, 0, &stBufferSize);

    // FIXME: Handle Error
    // if (stBufferSize) {
    if (stBuffer) {
        sSO2Parameters->stBufferSize = stBufferSize;
        sSO2Parameters->stBuffer = stBuffer;
        sSO2Parameters->fBufferReady = 1;
        sSO2Parameters->width = 1344;
        sSO2Parameters->height = 1024;
        sSO2Parameters->depth = 12;

        return 0;
    }
    if (stBuffer == NULL) {
        std::cout << "Failed to fill image buffer (size " << stBufferSize << ")\n";
    }
    return 1;
}

int camera_autosetExposure(sParameterStruct * sSO2Parameters)
{
    return 0;
}

int camera_setExposure(sParameterStruct * sSO2Parameters)
{
    return 0;
}

int camera_config(sParameterStruct * sSO2Parameters)
{
    return 0;
}
