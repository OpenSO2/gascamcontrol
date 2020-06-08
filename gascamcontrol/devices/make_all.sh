#/bin/bash

for d in */drivers/*/; do
    cd $d
    pwd
    cmake -DPYTHON_EXECUTABLE:FILEPATH=`which python` .
    make
    cd -
done
