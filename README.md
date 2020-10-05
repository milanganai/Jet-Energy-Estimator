#Achieving Improved Accuracy for Jet Energy Measurements using Machine Learning

*Description*
This work was presented here: https://indico.cern.ch/event/649482/contributions/3007443/
Energy measurements of jets produced by hadronization of quarks and gluons help to search for important rare physics processes beyond the Standard Model. However, the pileup interactions cause inaccuracies in the measurements of jet mass and transverse momentum. Pileup correction approaches based on simplified analytical models are inadequate. This approach is an unbiased pileup mitigation technique for jet energy measurements using TensorFlow-based deep machine learning. Like area-based pileup mitigation technique, this approach is unbiased, i.e., (a) it does not differentiate between charged and neutral particles, (b) it does not remove low energy particles, or (c) reject fake-jet before jet reconstruction. Twelve most influencing parameters having first-order and second-order effects on jet measurements were investigated and were used as inputs in learning the regression model. The training set comprises ~350K full jets (with pileup) and hard jets (without pileup), generated using PYTHIA+FastJet software. Overall, this approach performed orders-of-magnitude faster than the area-based approach, and also showed better accuracy (i.e., low mean and low dispersion) for the measurements of jet transverse momentum and mass.

*Requirements*
fastjet: 3.3.0 website: http://fastjet.fr
tensorflow: 1.3.0
python: 2.7.12

*Folder Description*
external: pythia (tested: 8.226), fastjet (tested: 3.3.0) packages
datasets.gold: data, eval data (pregenerated)
patch: patch files to pythia, fastjet
tensor: build, train, eval (tested: 1.3.0)

*Scripts*
clean.sh: clean for a fresh start
build.sh: script to apply patch, configure, build (pythia, fastjet)
datagen.sh: script to generate data
tensor/all.sh: wrapper script to train, mine data
tensor/train_eval.py: load and train and estimate
tensor/importsJE.py: load JE data


*Steps:*
`1> $ ./build.sh` builds all needed binaries
`2> $ ./datagen.sh datasets/data 100 50` generates data for training
`3> $ ./datagen.sh datasets/eval 10 50` generates data for prediction

_Note: To test steps 2-3, try_
`$ ./datagen.sh mydata 1 2`

`4> $ cd tensor; ./all.sh --outdir odir --datasets ../datasets`

_Note: To test steps 4, try_
`$ cd tensor; ./all.sh --try --outdir odir --datasets ../datasets.gold`
