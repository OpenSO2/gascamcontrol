doc:
	pydoc

flake8:
	flake8 --exclude pybind11,gps,webapp,env

pylint:
	pylint --version
	cd gascamcontrol; pylint  *.py devices/*/*.py plugins/*.py

pycodestyle:
	pycodestyle --exclude pybind11,webapp,gps,env .

pydocstyle:
	pydocstyle

cppcheck:
	cd gascamcontrol; cppcheck `find -name "*.cpp" -not -path "*/pybind11/*" -not -path "*/webapp/*"`

cpplint:
	cd gascamcontrol; cpplint `find -name "*.cpp" -not -path "*/pybind11/*" -not -path "*/CMakeFiles/*" -not -path "*/webapp/*"`

clang-tidy:
	cd gascamcontrol; clang-tidy `find -name "*.cpp" -not -path "*/pybind11/*" -not -path "*/webapp/*"`

doctest: compile_drivers
	python -m doctest -v gascamcontrol/*.py gascamcontrol/devices/*/*.py gascamcontrol/plugins/*.py

pytest: compile_drivers
	python -m pytest tests

coverage: compile_drivers
	python -m pytest --doctest-modules tests gascamcontrol --ignore-glob=*/pybind11*/ --ignore gascamcontrol/plugins/gps --ignore gascamcontrol/devices/spectrometer/drivers/mock/spectrometer.py  --ignore gascamcontrol/devices/spectrometer/drivers/oceanoptics/spectrometer.py --cov=gascamcontrol

coverage_html: compile_drivers
	python -m pytest --doctest-modules tests gascamcontrol --ignore-glob=*/pybind11*/ --ignore gascamcontrol/plugins/gps --ignore gascamcontrol/devices/spectrometer/drivers/mock/spectrometer.py  --ignore gascamcontrol/devices/spectrometer/drivers/oceanoptics/spectrometer.py --cov=gascamcontrol --cov-report html:cov_html

compile_drivers:
	cd gascamcontrol/devices; ./make_all.sh

lint: flake8 pylint pycodestyle pydocstyle cppcheck cpplint
test: doctest pytest
