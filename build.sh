#!/bin/bash
# ***************************************************************************
# * @File:       build.sh
# *
# * @Brief:      Applies patch, builds data generator binaries
# *
# * @Author:     Milan Ganai
# * 
# * @Creation:   Dec 2017
# ***************************************************************************
ROOT=$PWD
tar -xzf external/fastjet-3.3.0.tgz
tar -xzf external/pythia8226.tgz 
cp --backup patch/07-subtraction.cc fastjet-3.3.0/example/07-subtraction.cc
cp --backup patch/pythia8226_examples_Makefile pythia8226/examples/Makefile
cp patch/pythia8226_examples_mymain.cc pythia8226/examples/mymain.cc
cd fastjet-3.3.0; ./configure --prefix=$ROOT/pythia8226/fastjet_install; make; make install; cd ..
cd pythia8226; ./configure --with-fastjet3=$ROOT/pythia8226/fastjet_install; make; cd examples; make mymain; cd ../..



