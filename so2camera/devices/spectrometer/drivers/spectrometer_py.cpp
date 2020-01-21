#include <pybind11/pybind11.h>
#include <pybind11/iostream.h>
#include <pybind11/stl.h>
#include "spectrometer.h"
#include <iostream>

std::vector<double> getWavelengths(sSpectrometerStruct * vc);
std::vector<double> getWavelengths(sSpectrometerStruct * vc){
	return std::vector<double>(vc->wavelengths, vc->wavelengths + vc->spectrum_length);
}

std::vector<double> getLastSpectrum(sSpectrometerStruct * vc);
std::vector<double> getLastSpectrum(sSpectrometerStruct * vc){
	return std::vector<double>(vc->lastSpectrum, vc->lastSpectrum + vc->spectrum_length);
}

std::vector<double> getElectronicOffset(sSpectrometerStruct * vc);
std::vector<double> getElectronicOffset(sSpectrometerStruct * vc){
	return std::vector<double>(vc->electronic_offset, vc->electronic_offset + vc->spectrum_length);
}

std::vector<double> getDarkCurrent(sSpectrometerStruct * vc);
std::vector<double> getDarkCurrent(sSpectrometerStruct * vc){
	return std::vector<double>(vc->dark_current, vc->dark_current + vc->spectrum_length);
}

PYBIND11_MODULE(spectrometer, m) {
    m.doc() = "Manage spectrometer and abstract C nastyness.";

    m.def("init", &spectrometer_init, "Initialize spectrometer.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("get", &spectrometer_get, "Get spectrum.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());
		m.def("uninit", &spectrometer_uninit, "Stop device and free ressources.", pybind11::call_guard<pybind11::scoped_ostream_redirect, pybind11::scoped_estream_redirect>());

    pybind11::class_<sSpectrometerStruct>(m, "spectrometer")
        .def(pybind11::init<>())
      	.def_property("wavelengths", &getWavelengths, []() {})
      	.def_property("lastSpectrum", &getLastSpectrum, []() {})
      	.def_property("electronic_offset", &getElectronicOffset, []() {})
        .def_property("dark_current", &getDarkCurrent, []() {})
      	.def_property("max", [](sSpectrometerStruct * vc) {return vc->max;}, []() {})
      	.def_property("integration_time_micros", [](sSpectrometerStruct * vc) {return vc->integration_time_micros;}, [](sSpectrometerStruct * vc, int integration_time_micros) {vc->integration_time_micros = integration_time_micros;})
      	.def_property("spectrum_length", [](sSpectrometerStruct * vc) {return vc->spectrum_length;}, []() {})
      	.def_property("scans", [](sSpectrometerStruct * vc) {return vc->scans;}, [](sSpectrometerStruct * vc, int scans) {vc->scans = scans;})
		;
}
