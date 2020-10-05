#!/bin/bash
# ***************************************************************************
# * @File:       datagen.sh
# *
# * @Brief:      Generates training data
# *              datagen.sh <outdir> <#iter> <#pile (2-50)>
# *
# * @Author:     Milan Ganai
# * 
# * @Creation:   Dec 2017
# ***************************************************************************

if [ "$#" -ne 3 ]; then
    echo "usage: datagen.sh <outdir> <#iter> <#pile (2-50)>"
    exit
fi

dataout="$1"
LOOP_MAX="$2"
PILE_MAX="$3"

mkdir -p $dataout

#Numer of Pythia runs = LOOP_MAX * (PILE_MAX-1) * 6


ROOT="$PWD"
FASTJET=$ROOT/fastjet-3.3.0/example/07-subtraction
PYTHIA=$ROOT/pythia8226/examples/mymain

pythiaOut="particle.dat"
csvFlag=1
logOut="/dev/null"


for i in $(eval echo "{1..${LOOP_MAX}}"); do
jetOut="$dataout/jet$i.csv"
paramOut="$dataout/param$i.txt"
appendFlag=0
count=0
\rm -f $jetOut
printf "eCM, nPile, seed, R\n"> $paramOut 

for eCM in 7000 14000; do
for nPile in $(eval echo "{2..${PILE_MAX}}"); do
seed=$RANDOM
count=$((count+1))
echo "Pythia Run: $count"
printf "1 $eCM $nPile $seed $pythiaOut\nEOF\n" > cmnd1
head -n 1 cmnd1
$PYTHIA < cmnd1  >> $logOut
fjcount=0
for R in 0.4 0.5 0.6; do
if [ -e $jetOut ];then
appendFlag=1
fi
printf "$R $pythiaOut $appendFlag $csvFlag $jetOut\nEOF\n" > cmnd2
fjcount=$((fjcount+1))
echo "Fastjet Run: $fjcount"
head -n 1 cmnd2
$FASTJET  < cmnd2 >> $logOut
printf "$eCM, $nPile, $seed, $R\n">> $paramOut 
done #loop R
done #loop for nPile
done #loop for eCM
done #loop for i
