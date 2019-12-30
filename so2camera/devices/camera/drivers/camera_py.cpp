#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "camera.h"

std::vector<uint8_t> getBuffer(sParameterStruct * vc);
std::vector<uint8_t> getBuffer(sParameterStruct * vc){
	return std::vector<uint8_t>(vc->stBuffer, vc->stBuffer + vc->stBufferSize);
}

PYBIND11_MODULE(camera, m) {
    m.doc() = "Manage camera and abstract C nastyness.";

    m.def("init", &camera_init, "Initialize camera.");
		m.def("get", &camera_get, "Capture a frame from device and places stBuffer in camera.stBuffer");
		m.def("uninit", &camera_uninit, "Stop device and frees ressources.");
		m.def("abort", &camera_uninit, "Abort capture.");
		m.def("setExposure", &camera_uninit, "");
		m.def("autosetExposure", &camera_uninit, "");
		m.def("config", &camera_config, "");

    pybind11::class_<sParameterStruct>(m, "camera")
        .def(pybind11::init<>())
				.def_property("width", [](sParameterStruct * vc) {return vc->width;}, []() {})
				.def_property("height", [](sParameterStruct * vc) {return vc->height;}, []() {})
				.def_property("buffer", &getBuffer, []() {})
				.def_property("exposuretime", [](sParameterStruct * vc) {return vc->exposuretime;}, []() {})
				.def_property("identifier", [](sParameterStruct * vc) {return vc->identifier;}, []() {})
				.def_property("dark", [](sParameterStruct * vc) {return vc->dark;}, []() {})
		;
}
