#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/extract.hpp>
#include <string>
#include <sstream>
#include <vector>
#include <iostream>
#include "camera.h"
#include "configurations.h"

using namespace std;

sParameterStruct sSO2Parameters;
sConfigStruct config;

// typedef struct sConfigStruct sConfigStruct;


// config.dBufferlength = 1376256;
// config.dFixTime = 0;
// config.dExposureTime_a = 250000;
// config.dExposureTime_b = 250000;
// config_init_sParameterStruct(&sSO2Parameters, &config, 'A');
//
// struct movies_t {
//   string title;
//   int year;
// };
//
// movies_t mine;
//
// struct Person {
//    char name[20];
//    int  age;
//    float salary;
//    //std::string names;
//    std::string names() { return "a"; }
// };

// int test()
// {
//   Person tom = {"Tom", 25, 40000.50};
//   cout << "My favorite person is: ";
//   cout << tom.name;
//   mine.year = 12;
// }
//
//
// int main ()
// {
//   test();
// }
// mine.title = "2001 A Space Odyssey";
//
// struct World
// {
//     void set(std::string msg) { mMsg = msg; }
//     void many(boost::python::list msgs) {
//         long l = len(msgs);
//         std::stringstream ss;
//         for (long i = 0; i<l; ++i) {
//             if (i>0) ss << ", ";
//             std::string s = boost::python::extract<std::string>(msgs[i]);
//             ss << s;
//         }
//         mMsg = ss.str();
//     }
//     std::string greet() { return mMsg; }
//     std::string mMsg;
// };


// struct tag {};
// tag make_tag()
// {
//   return tag();
// }
//
// struct tag_to_noddy
// {
//   static PyObject* convert(tag const& x)
//   {
//     return PyObject_New(noddy_NoddyObject, &noddy_NoddyType);
//   }
// };

/* to-python convert to QStrings */
// struct short_to_python_int
// {
//     static PyObject* convert(short* s)
//     {
//         return boost::python::object(
//             static_cast<unsigned int*>(static_cast<void*>(s))
//         );
//     }
// };

using namespace boost::python;

namespace bp = boost::python;
// namespace bn = boost::python::numpy;

struct short_to_python_int
{
    static PyObject* convert(short s)
    {
        return incref(object((int)s).ptr());
    }
};

struct int_to_python_int
{
    static PyObject* convert(int s)
    {
        return incref(object((int)s).ptr());
    }
};


struct short_ptr_to_python_int_ptr
{
//  static bp::list convert(short * s)
    static PyObject* convert(short * s)
    {
        // bp::list a;
        // a.append(1);
        // a.append(2);
        // return a;
        return incref(object(static_cast<int*>(static_cast<void*>(s))).ptr());
    }
};

int getBuffer(sParameterStruct f, int index) {
    return f.stBuffer[index];
}


struct unsigned_long_to_python_int
{
    static PyObject* convert(unsigned long s)
    {
        return incref(object((int)s).ptr());
    }
};


boost::python::list wrap_arr(short * s);

boost::python::list wrap_arr(short * s) {
    bp::list a;

    a.append(1);
    a.append(1);

    // for (int i = 0; i < 10; ++i) {
    //     a.append((int)s[i]);
    // }
    return a;
}


BOOST_PYTHON_MODULE(camera_py)
{
    to_python_converter<short*, short_ptr_to_python_int_ptr>();
    to_python_converter<short, short_to_python_int>();
    to_python_converter<int, int_to_python_int>();
    to_python_converter<unsigned long, unsigned_long_to_python_int>();





    class_<sParameterStruct>("sSO2Parameters")
        .add_property("hCamera", &sParameterStruct::hCamera)
        .add_property("timestampBefore", &sParameterStruct::timestampBefore)
        .add_property("timestampAfter", &sParameterStruct::timestampAfter)
        .add_property("dExposureTime", &sParameterStruct::dExposureTime, &sParameterStruct::dExposureTime)
        .add_property("stBuffer", &sParameterStruct::stBuffer)
        // .add_property("stBuffer", wrap_arr)
        .add_property("fBufferReady", &sParameterStruct::fBufferReady)
        .add_property("fFifoOverFlow", &sParameterStruct::fFifoOverFlow)
        .add_property("identifier", &sParameterStruct::identifier, &sParameterStruct::identifier)
        .add_property("dark", &sParameterStruct::dark, &sParameterStruct::dark)
        .def("getBuffer", &getBuffer)
     ;

     class_<sConfigStruct>("config")
     	.add_property("processing", &sConfigStruct::processing, &sConfigStruct::processing)
     	.add_property("debug", &sConfigStruct::debug, &sConfigStruct::debug)
     	.add_property("noofimages", &sConfigStruct::noofimages, &sConfigStruct::noofimages)
     	.add_property("dBufferlength", &sConfigStruct::dBufferlength, &sConfigStruct::dBufferlength)
     	.add_property("dExposureTime_a", &sConfigStruct::dExposureTime_a, &sConfigStruct::dExposureTime_a)
     	.add_property("dExposureTime_b", &sConfigStruct::dExposureTime_b, &sConfigStruct::dExposureTime_b)
     	.add_property("dImageCounter", &sConfigStruct::dImageCounter, &sConfigStruct::dImageCounter)
     	.add_property("dInterFrameDelay", &sConfigStruct::dInterFrameDelay, &sConfigStruct::dInterFrameDelay)
     	.add_property("cConfigFileName", &sConfigStruct::cConfigFileName, &sConfigStruct::cConfigFileName)
     	.add_property("cFileNamePrefix", &sConfigStruct::cFileNamePrefix, &sConfigStruct::cFileNamePrefix)
     	.add_property("cImagePath", &sConfigStruct::cImagePath, &sConfigStruct::cImagePath)
     	.add_property("createsubfolders", &sConfigStruct::createsubfolders, &sConfigStruct::createsubfolders)
     	.add_property("dFixTime", &sConfigStruct::dFixTime, &sConfigStruct::dFixTime)
     	.add_property("filterwheel_device", &sConfigStruct::filterwheel_device, &sConfigStruct::filterwheel_device)
     	.add_property("darkframeintervall", &sConfigStruct::darkframeintervall, &sConfigStruct::darkframeintervall)
     	.add_property("spectrometer_shutter_device", &sConfigStruct::spectrometer_shutter_device, &sConfigStruct::spectrometer_shutter_device)
     	.add_property("spectrometer_shutter_channel", &sConfigStruct::spectrometer_shutter_channel, &sConfigStruct::spectrometer_shutter_channel)
     	.add_property("spectrometer_calibrate_intervall", &sConfigStruct::spectrometer_calibrate_intervall, &sConfigStruct::spectrometer_calibrate_intervall)
     	.add_property("spectroscopy_roi_upper", &sConfigStruct::spectroscopy_roi_upper, &sConfigStruct::spectroscopy_roi_upper)
     	.add_property("spectroscopy_roi_lower", &sConfigStruct::spectroscopy_roi_lower, &sConfigStruct::spectroscopy_roi_lower)
     	.add_property("comm_port", &sConfigStruct::comm_port, &sConfigStruct::comm_port)
     	.add_property("enableWebcam", &sConfigStruct::enableWebcam, &sConfigStruct::enableWebcam)
     	.add_property("enableSpectroscopy", &sConfigStruct::enableSpectroscopy, &sConfigStruct::enableSpectroscopy)
     	.add_property("rotate_a", &sConfigStruct::rotate_a, &sConfigStruct::rotate_a)
     	.add_property("rotate_b", &sConfigStruct::rotate_b, &sConfigStruct::rotate_b)
     	.add_property("rotate_webcam", &sConfigStruct::rotate_webcam, &sConfigStruct::rotate_webcam)
      ;

   def("camera_init", &camera_init);
   def("camera_get", &camera_get);
   def("camera_abort", &camera_abort);
   def("camera_setExposure", &camera_setExposure);
   def("camera_autosetExposure", &camera_autosetExposure);
   def("camera_config", &camera_config);
   def("camera_uninit", &camera_uninit);
}
