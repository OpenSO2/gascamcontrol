#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "camerashutter.h"

PYBIND11_MODULE(camerashutter, m) {
    m.doc() = "Manage camera shutter and abstract C nastyness.";

    m.def("init", &camerashutter_init, "Initialize camera shutter.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("setState", &camerashutter_setState, "Set camera shutter state (open or close)", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("uninit", &camerashutter_uninit, "Stop device and free ressources.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());

    pybind11::class_<sCamerashutter>(m, "camerashutter")
        .def(pybind11::init<>())
        .def_property("state", [](sCamerashutter * vc) {return vc->state;}, []() {})
				.def_property("device", [](sCamerashutter * vc) {return vc->device;}, [](sCamerashutter * vc, char * device) {vc->device = device;})
		;
}
