#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "camerashutter.h"

PYBIND11_MODULE(camerashutter, m) {
    m.doc() = "Manage camera shutter and abstract C nastyness.";

    m.def("init", &camerashutter_init, "Initialize camera shutter.");
		m.def("setState", &camerashutter_setState, " ");
		m.def("uninit", &camerashutter_uninit, "Stop device and free ressources.");

    pybind11::class_<sCamerashutter>(m, "camerashutter")
        .def(pybind11::init<>())
        .def_property("state", [](sCamerashutter * vc) {return vc->state;}, []() {})
				.def_property("device", [](sCamerashutter * vc) {return vc->device;}, [](sCamerashutter * vc, char * device) {vc->device = device;})
		;
}
