doc:
	pydoc

flake8:
	flake8 --exclude pybind11,gps,webapp

pylint:
	cd gascamcontrol; pylint --ignore=pybind11,webapp gascamcontrol

pycodestyle:
	pycodestyle --exclude pybind11,webapp,gps .

pydocstyle:
	pydocstyle

cppcheck:
	cppcheck `find -name "*.cpp" -not -path "*/pybind11/*" -not -path "*/webapp/*"`

cpplint:
	cpplint `find -name "*.cpp" -not -path "*/pybind11/*" -not -path "*/CMakeFiles/*" -not -path "*/webapp/*"`

clang-tidy:
	clang-tidy `find -name "*.cpp" -not -path "*/pybind11/*" -not -path "*/webapp/*"`

doctest:
	python -m doctest -v gascamcontrol/*.py gascamcontrol/devices/*/*.py gascamcontrol/plugins/*.py

pytest:
	python -m pytest tests

coverage:
	cd gascamcontrol; pytest --cov=myproj --ignore-glob="*/pybind11/*" --ignore=webapp --ignore plugins/gps --ignore devices/spectrometer/drivers/oceanoptics/spectrometer.py --ignore devices/spectrometer/drivers/mock/spectrometer.py

coverage2:
	cd gascamcontrol; coverage run -m pytest --ignore-glob="*/pybind11/*" --ignore=webapp --ignore plugins/gps --ignore devices/spectrometer/drivers/oceanoptics/spectrometer.py --ignore devices/spectrometer/drivers/mock/spectrometer.py

lint: flake8 pylint pycodestyle pydocstyle cppcheck cpplint
test: doctest pytest
