#!/bin/bash
while [ true ]
do
        sleep 30m
        for i in storeroom*
        do
                find $i -mmin +30 -delete
        done
done