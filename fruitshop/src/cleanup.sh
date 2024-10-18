#!/bin/bash

while [ true ]
do
	sleep 30m
	for i in shop*
	do
	        find $i/storeroom -mmin +30 -delete  > /dev/null
	done
done
