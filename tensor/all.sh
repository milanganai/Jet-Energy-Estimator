#!/bin/bash
# ***************************************************************************
# * @File:       all.sh
# *
# * @Brief:      wrapper on training and mining script
# *
# * @Author:     Milan Ganai
# * 
# * @Creation:   Dec 2017
# ***************************************************************************
./train_eval.py "$@" | tee all.log
egrep "Total|RMS error|jpt_hard|Train" all.log | tee t
echo "======================="
echo "======================="
./mine.py t

