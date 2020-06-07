doc:
	pydoc

flake8:
	flake8 --exclude pybind11,gps,webapp,env

pylint:
	cd gascamcontrol; pylint --ignore=pybind11,webapp gascamcontrol

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

doctest:
	python -m doctest -v gascamcontrol/*.py gascamcontrol/devices/*/*.py gascamcontrol/plugins/*.py

pytest:
	python -m pytest tests

coverage:
	python -m pytest --doctest-modules tests gascamcontrol --ignore gascamcontrol/plugins/gps --ignore gascamcontrol/devices/spectrometer/drivers/mock/spectrometer.py  --ignore gascamcontrol/devices/spectrometer/drivers/oceanoptics/spectrometer.py --cov=gascamcontrol

lint: flake8 pylint pycodestyle pydocstyle cppcheck cpplint
test: doctest pytest
