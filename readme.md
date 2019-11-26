boost-jam
boost-python3
boost-python3-devel
boost-python2-devel
boost-python2
g++ -Wall -Wextra -shared -I/usr/include/python3.7m -lboost_python37 mantid.c -o mantid.so -fPIC
python -c "import mantid; mantid.sayHello()"
