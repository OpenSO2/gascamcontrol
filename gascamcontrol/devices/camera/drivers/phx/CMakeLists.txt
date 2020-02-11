cmake_minimum_required(VERSION 2.8)
project(camera)

if(CMAKE_COMPILER_IS_GNUCC)
	add_definitions("-pedantic")
	add_definitions("-Wall")
	add_definitions("-Wundef")
	add_definitions("-Wextra")
	add_definitions("-Wunused-parameter")
	add_definitions("-Wpointer-arith")
	add_definitions("-Wcast-qual")
	add_definitions("-Wno-missing-braces")
	add_definitions("-Wno-missing-field-initializers")
	add_definitions("-Wformat=2")
	add_definitions("-Wswitch-default")
	add_definitions("-Wswitch-enum")
	add_definitions("-Wcast-align")
	add_definitions("-Wstrict-overflow=5")
	add_definitions("-Winline")
	add_definitions("-Wunreachable-code")
	add_definitions("-Wlogical-op")
	add_definitions("-Wfloat-equal")
	add_definitions("-Wstrict-aliasing=2")
	add_definitions("-Wredundant-decls")
	add_definitions("-ggdb3")
	add_definitions("-O0")
	add_definitions("-fno-omit-frame-pointer")
	add_definitions("-ffloat-store")
	add_definitions("-fno-common")
	add_definitions("-fstrict-aliasing")
	add_definitions("-Wmissing-declarations")
endif()

add_subdirectory(pybind11)
pybind11_add_module(camera camera.cpp ../camera_py.cpp)

# FIXME?
add_library(camera2 camera.cpp)

add_definitions(-DPOSIX)
add_definitions(-D_PHX_LINUX)
add_definitions(-D_PHX_POSIX)

include_directories(/usr/local/active_silicon/phx_sdk-6.23/include)
link_directories(/usr/local/active_silicon/phx_sdk-6.23/lib/linux64)

add_definitions(-DPHX)
add_definitions(-DCAMERA_PCF_FILE="${CMAKE_CURRENT_SOURCE_DIR}/c8484.pcf")

find_library(M_LIB m)
target_link_libraries(camera ${M_LIB})

# link the libraries to the executable
target_link_libraries(camera phx pfw)
target_link_libraries(camera pthread)

# create executables
# add_executable(camera-cli camera-cli.cpp)
# target_link_libraries(camera-cli camera)

# find_package( OpenCV REQUIRED )
# include_directories( ${OpenCV_INCLUDE_DIRS} )
# target_link_libraries(camera-cli ${OpenCV_LIBS})
