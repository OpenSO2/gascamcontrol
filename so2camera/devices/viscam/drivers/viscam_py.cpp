#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "viscam.h"

std::vector<uint8_t> getBuffer(sVisCamStruct * vc);
std::vector<uint8_t> getBuffer(sVisCamStruct * vc){
	return std::vector<uint8_t>(vc->buffer, vc->buffer + vc->bufferSize);
}

PYBIND11_MODULE(viscam, m) {
    m.doc() = "Manage viscam (eg. webcam).";

    m.def("init", &viscam_init, "Initialize viscam.");
		m.def("get", &viscam_get, "Capture a frame from device and places buffer in viscam.buffer");
		m.def("uninit", &viscam_uninit, "Stop device and frees ressources.");

    pybind11::class_<sVisCamStruct>(m, "viscam")
        .def(pybind11::init<>())
				.def_property("width", [](sVisCamStruct * vc) {return vc->width;}, []() {})
				.def_property("height", [](sVisCamStruct * vc) {return vc->height;}, []() {})
				.def_property("buffer", &getBuffer, []() {})
		;
}
