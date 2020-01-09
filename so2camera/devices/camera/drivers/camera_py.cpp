#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "camera.h"

std::vector<short> getBuffer(sParameterStruct * vc);
std::vector<short> getBuffer(sParameterStruct * vc){
	// vc->stBufferSize = 2752512;
	fprintf(stderr, "vc->stBufferSize %i %c %i %i\n", vc->stBufferSize, vc->identifier, (int)vc->fBufferReady, sizeof(short));
	// fixme!
	return std::vector<short>(vc->stBuffer, vc->stBuffer + vc->stBufferSize/sizeof(short));
}

PYBIND11_MODULE(camera, m) {
    m.doc() = "Manage camera and abstract C nastyness.";

    m.def("init", &camera_init, "Initialize camera.");
		m.def("get", &camera_get, "Capture a frame from device and places stBuffer in camera.stBuffer");
		m.def("uninit", &camera_uninit, "Stop device and frees ressources.");
		m.def("abort", &camera_abort, "Abort capture.");
		m.def("setExposure", &camera_setExposure, "");
		m.def("autosetExposure", &camera_autosetExposure, "");

    pybind11::class_<sParameterStruct>(m, "camera")
        .def(pybind11::init<>())
				.def_property("width", [](sParameterStruct * vc) {return vc->width;}, []() {})
				.def_property("height", [](sParameterStruct * vc) {return vc->height;}, []() {})
				.def_property("buffer", &getBuffer, []() {})
				.def_property("exposuretime", [](sParameterStruct * vc) {return vc->exposuretime;}, [](sParameterStruct * vc, int exposuretime) {vc->exposuretime = exposuretime;})
				.def_property("identifier", [](sParameterStruct * vc) {return vc->identifier;}, [](sParameterStruct * vc, char identifier) {vc->identifier = identifier;})
				.def_property("dark", [](sParameterStruct * vc) {return vc->dark;}, []() {})
				.def_property("stBufferSize", [](sParameterStruct * vc) {return vc->stBufferSize;}, []() {})
		;
}
