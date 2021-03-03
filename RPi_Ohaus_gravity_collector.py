#!/usr/bin/python3

## This is a script to collect specific gravity measurements using an Ohaus Valor 7000 scale
## Written by Max Feldman USDA-ARS Prosser, WA

import serial
import re
from time import sleep
import csv
#import numpy
#from pylab import *
import datetime
import os.path
import sys
from optparse import OptionParser
import re
import glob
import pandas as pd


ser = serial.Serial(
  baudrate = 9600,
  parity = serial.PARITY_NONE,
  bytesize = 8,
  stopbits = 1,
  timeout = 1,
  port='/dev/ttyUSB0'
)

print("You are running the yield and specific gravity script\n")
program_name = "RPi_ohaus_gravity_collector.py"
version = "0.1"

## Get arguments
parser = OptionParser()
#parser.add_option("-i", "--infile") # Required
parser.add_option("-o", "--outfile") # Required
parser.add_option("-u", "--user") # Required

(options, args) = parser.parse_args()

## Re-assign values from command line into more intuitive variable names
#infile = options.infile
outfile = options.outfile
user_name = options.user

########################
## Define Fxns

def recursive_YesNo(question):
    answer = input(question)
    print("You answered: ", answer)
    if answer == 'y':
        #print("Great lets continue...\n")
        return('y')
    elif answer == 'n':
        print("Okay... Lets fix this\n")
        return('n')
    else:
        print("Hmmmmm... I didn't understand your answer\n")
        sleep(2)
        return recursive_YesNo("I don't understand your answer. 'y' or 'no' please\n")

def change_arg(question):
    global infile
    global outfile
    global user_name
    answer = input(question)
    print("You answered: ", answer)
    if answer == 'o':
        outfile = input("What is the name of the output directory?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return change_arg(question)
        else:
            print("Argument ", "-o", "was changed to ", outfile)
    elif answer == 'u':
        user_name = input("What is the name of the user?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return change_arg(question)
        else:
            print("Argument ", "-u", "was changed to ", user_name)

def get_sample(question):
    sample = input(question)
    print("You are weighing sample: ", sample)
    reply = recursive_YesNo("Is this correct? (y|n) \n")
    if reply == 'y':
        print("Great. Will will work on: ", sample)
        return sample
    else:
        print("Darn. Lets enter it again.")
        return get_sample(question)


def take_weight(sample):
    reply = ''
    print("\n\nPush Print button on scale\n")
    input("Press enter after reading is made\n")
    wt_input = ser.readline()
    #print(wt_input)
    wt_text=wt_input.decode("utf-8")
    wt_re = re.findall("[0-9]\.[0-9]+", str(wt_text))
    wt = ''.join(wt_re)
    #print(wt)
    #return wt
    print("\n\nWeight is recorded as:\t", str(wt), "\n")
    reply = input("Type 'n' to take measurment again, or hit enter to continue\n")
    if reply == 'n':
        return take_weight(sample)
    else:
        return wt

def get_data(sample):
    print("\nTaking dry weight of sample: \t", str(sample), "\n")
    dwt = take_weight(sample)
    print(dwt)
    print("\nTaking wet weight of sample: \t", str(sample), "\n")
    wwt = take_weight(sample)
    print(wwt)
    return dwt, wwt


## Remind the user what they are running
print("You are using " + str(program_name) + " version " + str(version))
sleep(1)

print("Output file name is: ", outfile, "\n", "User name is: ", user_name, "\n")
sleep(1)

pwd = os.getcwd()
outfile_path = pwd + "/" + outfile + ".csv"

## Ask user if the arguments are correct
value = recursive_YesNo("Does this look right?")

if value == 'n':
    change_arg("What argument would you like to change? -i [infile] -o [outfile] -u [user] \n")
else:
    print("No change needed\n")

## Check date with user
print("\nLets check the date and time to make sure it is accurate...\n")

## Get a datetime object
datetime_rn = datetime.datetime.now()

## Extract strings from object corresponding to date and time
date_rn = str(datetime_rn.date())
time_rn = datetime_rn.time().strftime("%H:%M:%S")

print("The date is:\t" + date_rn)
print("The time is:\t" + time_rn)
sleep(1)


summary_table = pd.DataFrame(columns=['sample', 'dwt', 'wwt', 'date_rn', 'time_rn', 'user_name'])

exit = input("Would you like to exit (y|n)?\n")

while(exit == "n"):    
    sample = get_sample("Scan or enter the sample you are working on...\n")
    #print("Is this sample:\n" + str(sample) + "\n")
    #yn_answer = input("Is this correct? (y|n)\n")
    #if(yn_answer == "n"):
    dwt, wwt = get_data(sample)
    ## Get a datetime object
    datetime_rn = datetime.datetime.now()
    ## Extract strings from object corresponding to date and time
    date_rn = str(datetime_rn.date())
    time_rn = datetime_rn.time().strftime("%H:%M:%S")
    out_entry = list()
    out_entry.extend([sample, dwt, wwt, date_rn, time_rn, user_name])
    entry_row = pd.DataFrame([out_entry], columns=['sample', 'dwt', 'wwt', 'date_rn', 'time_rn', 'user_name'])
    print(str(entry_row))
    yn_reply = input("Type 'n' if you want to redo the measurment otherwise push ENTER...\n")
    if yn_reply == 'n':
        continue
    else:
        #summary_table = summary_table.append(entry_row,)
        out_table_path = outfile_path 
        #summary_table.to_csv(out_table_path, mode='a', header=False, encoding='utf-8')
        entry_row.to_csv(out_table_path, mode='a', header=False, encoding='utf-8')
        
    exit = input("Would you like to exit (y|n)?\n")