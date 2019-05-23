#! /bin/bash
for (( c=1; c < 31; c++ ))
do
	python main.py 4 $c 0.06 0.02
done