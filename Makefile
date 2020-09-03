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

test: compile_drivers
	python -m pytest --doctest-modules \
		--ignore-glob=*/pybind11*/ \
		--ignore gascamcontrol/plugins/gps \
		--ignore gascamcontrol/devices/spectrometer/drivers/mock/spectrometer.py \
		--ignore gascamcontrol/devices/spectrometer/drivers/oceanoptics/spectrometer.py

coverage: compile_drivers
	python -m pytest --doctest-modules \
		--ignore-glob=*/pybind11*/ \
		--ignore gascamcontrol/plugins/gps \
		--ignore gascamcontrol/devices/spectrometer/drivers/mock/spectrometer.py \
		--ignore gascamcontrol/devices/spectrometer/drivers/oceanoptics/spectrometer.py \
		--cov=gascamcontrol

coverage_html: compile_drivers
	python -m pytest --doctest-modules tests gascamcontrol --ignore-glob=*/pybind11*/ --ignore gascamcontrol/plugins/gps --ignore gascamcontrol/devices/spectrometer/drivers/mock/spectrometer.py  --ignore gascamcontrol/devices/spectrometer/drivers/oceanoptics/spectrometer.py --cov=gascamcontrol --cov-report html:cov_html

compile_drivers:
	cd gascamcontrol/devices; ./make_all.sh

conda_package:
#	conda activate conda-build
	conda build . -c conda-forge

create_environment:
	conda env create -f environment.yml -n gascamcontrol-env
	conda activate gascamcontrol-env

conda_local_install: conda_package
	conda install -c conda-forge --use-local gascamcontrol

conda_upload:
	anaconda login
	anaconda upload

remove_environment:
	conda env remove -n gascamcontrol-env

test_environment: create_environment remove_environment

lint: flake8 pylint pycodestyle pydocstyle cppcheck cpplint
