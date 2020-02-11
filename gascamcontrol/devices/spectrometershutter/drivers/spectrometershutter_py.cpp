#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "spectrometershutter.h"
#include <iostream>

PYBIND11_MODULE(spectrometershutter, m) {
    m.doc() = "Manage spectrometer shutter and abstract C nastyness.";

    m.def("init", &spectrometershutter_init, "Initialize spectrometer shutter.");
		m.def("set_state", &spectrometershutter_setState, " ");
		m.def("uninit", &spectrometershutter_uninit, "Stop device and free ressources.");

    pybind11::class_<sSpectrometershutter>(m, "spectrometershutter")
        .def(pybind11::init<>())
        .def_property("state", [](sSpectrometershutter * vc) {return vc->state;}, []() {})
        .def_property("device", [](sSpectrometershutter * vc) {return vc->device;}, [](sSpectrometershutter * vc, char * device) {
        std::cout << "My favorite device is\n";
        std::cout << device;
        std::cout << "\n device \n";
          vc->device = device;

          std::cout << "device is still\n";
          std::cout << vc->device;
          std::cout << "\n device \n";


        })

				.def_property("channel", [](sSpectrometershutter * vc) {return vc->channel;}, [](sSpectrometershutter * vc, int channel) {vc->channel = channel;})
		;
}
