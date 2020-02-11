#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "camera.h"

std::vector<short> getBuffer(sParameterStruct * vc);
std::vector<short> getBuffer(sParameterStruct * vc){
	// fixme!
	return std::vector<short>(vc->stBuffer, vc->stBuffer + vc->stBufferSize/sizeof(short));
}

PYBIND11_MODULE(camera, m) {
    m.doc() = "Manage camera and abstract C nastyness.";

    m.def("init", &camera_init, "Initialize camera.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("get", &camera_get, "Capture a frame from device and places stBuffer in camera.stBuffer", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("uninit", &camera_uninit, "Stop device and frees ressources.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("abort", &camera_abort, "Abort capture.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("setExposure", &camera_setExposure, "", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("autosetExposure", &camera_autosetExposure, "", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());

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
