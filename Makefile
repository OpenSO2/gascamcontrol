doc:
	pydoc

flake8:
	flake8 --exclude pybind11,gps

pylint:
	cd gascamcontrol; pylint --ignore=pybind11 gascamcontrol; cd -

pydocstyle:
	pydocstyle

cppcheck:
	cppcheck `find -name "*.cpp" -not -path "*/pybind11/*"`

cpplint:
	cpplint `find -name "*.cpp" -not -path "*/pybind11/*"`

clang-tidy:
	clang-tidy `find -name "*.cpp" -not -path "*/pybind11/*"`

doctest:
	python -m doctest -v gascamcontrol/*.py gascamcontrol/devices/*/*.py gascamcontrol/plugins/*.py

lint: flake8 pylint pydocstyle cppcheck cpplint
test: doctest