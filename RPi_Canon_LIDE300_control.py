#!/usr/bin/env python3

## This is a script to collect scans using a Canon LIDE 300 scanner on Raspberry Pi
## Written by Max Feldman USDA-ARS Prosser, WA


program_name = "RPi_canon_lide300_control.py"
version = 0.01

## Import python libraries
from time import sleep
from serial import Serial
import csv
#import numpy
#from pylab import *
#from datetime import date
import datetime
import os.path
#import matplotlib.pyplot as plt
#import cv2
import sys
from optparse import OptionParser
import re
import glob

import subprocess
#import sane


## Get the pwd
pwd = os.getcwd()

parser = OptionParser()
#parser.add_option("-i", "--infile") # Required
parser.add_option("-o", "--outfile") # Required
parser.add_option("-u", "--user") # Required
parser.add_option("-c", "--clone") # Required
parser.add_option("-r", "--rep") # Required

(options, args) = parser.parse_args()

## Re-assign values from command line into more intuitive variable names
#infile = options.infile
outfile = options.outfile
user_name = options.user
clone = options.clone
rep = options.rep

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
    #elif answer == 'exit':
    #    print("Exiting program...\n")
    #    exit()
    else:
        print("Hmmmmm... I didn't understand your answer\n")
        sleep(1)
        return(recursive_YesNo("I don't understand your answer. 'y' or 'n' please\n"))

def change_arg(question):
    #global infile
    global outfile
    global user_name
    global clone
    global rep
    global side
    answer = input(question)
    print("You answered: ", answer)
    if answer == 'o':
        outfile = input("What is the name of the output directory?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return(change_arg(question))
        else:
            print("Argument ", "-o", "was changed to ", outfile)
    elif answer == 'u':
        user_name = input("What is the name of the user?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return(change_arg(question))
        else:
            print("Argument ", "-u", "was changed to ", user_name)
    elif answer == 'c':
        clone = input("What is the name of the clone?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return(change_arg(question))
        else:
            print("Argument ", "-c", "was changed to ", clone)
    elif answer == 'r':
        rep = input("What replicate (rep)?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return(change_arg(question))
        else:
            print("Argument ", "-r", "was changed to ", rep)
    elif answer == 's':
        side = input("What side are you measuring?\n")
        reply = recursive_YesNo('Do you want to change another argument? (y|n) \n')
        if reply == 'y':
            return(change_arg(question))
        else:
            print("Argument ", "-s", "was changed to ", side)

def get_Clone(question):
    clone = input(question)
    print("You are imaging clone: ", clone)
    reply = recursive_YesNo("Is this correct? (y|n) \n")
    if reply == 'y':
        print("Great. Will will work on: ", clone)
        return clone
    else:
        print("Darn. Lets enter it again.")
        return(get_Clone(question))

def get_Rep(question):
    rep = input(question)
    print("What replicate (rep) is this?: ", rep)
    reply = recursive_YesNo("Is this correct? (y|n) \n")
    if reply == 'y':
        print("Great. Will will work on replicate: ", rep)
        return rep
    else:
        print("Darn. Lets enter it again.")
        return(get_Rep(question))

def capture_scan(clone, rep):
    outfile_name = outfile_path + "/" + str(clone) + "_" + str(rep) + ".tif"
    if os.path.exists(outfile_name):
        print("This file exists. Perhaps you have already imaged this clone.\n")
        new_name = get_Clone("Please enter a different clone name. \n")
        new_rep = get_Rep("Please enter a different LED name. \n")
        capture_scan(new_name, new_rep)
    else:
        print("We are capturing an image of clone: ", clone, "\n Replicate:", rep, "\n  ")
        ## Find path to scanner
        ## sudo LD_LIBRARY_PATH=/usr/local/lib scanimage -L
        subprocess.call(["sudo", "LD_LIBRARY_PATH=/usr/local/lib", "scanimage", "--device-name=pixma:04A91913_4B52F7", "--resolution", "300", "--format", "tiff", "--output-file", outfile_name])
        #ver = sane.init()
        #devices = sane.get_devices()
        #print(devices)
        #dev = sane.open(devices[0][0])
        ##params = dev.get_parameters()
        ## Start a scan... and get a PIL.Image object
        #dev.mode = 'color'
        #dev.start()
        #print(dev.is_active())
        #im = dev.snap()
        #sleep(30)
        #im.save(outfile_name)
        #sleep(30)
        #del im
        #dev.close()
        #print(dev.is_active())
        #del dev
        #sane.close()
        #sane.exit()
        print("exit subroutine\n")

########################
## Main program

## Remind the user what they are running
print("You are using " + str(program_name) + " version " + str(version))
sleep(1)

print("Output file name is: ", outfile, "\n","User name is: ", user_name, "\n")
sleep(1)

print("Clone name is: ", clone, "\n","Replicate is: ", rep, "\n", "\n")
sleep(1)

## Ask user if the arguments are correct
value = recursive_YesNo("Does this look right?\n\nType 'y' to proceed \n OR \nType 'n' to change arguments\n")

if value == 'n':
    change_arg("What argument would you like to change? -o [outfile] -u [user] -c [clone] -r [rep] \n")
else:
    print("No change needed\n")


## If no directory to store data is present, go ahead and create it
outfile_path = "/home/pi/Desktop" + "/" + outfile


if os.path.exists(outfile_path):
    print("This directory already exists. We will write results to this folder\n")

if not os.path.exists(outfile_path):
    print("\n" + "No file directory named: " + str(outfile_path) + "\n")
    print("\n" + "Creating the directory\n" + str(outfile_path) + "\n")
    os.makedirs(outfile_path)

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

## Check to see if this is info is correct
#usr_input = input("Does this look accurate?...(y|n)\n")
#if (usr_input != 'Y' or 'y'):
#    print("Great...\n")
#else:
#    print("Okay. Lets fix this. \n")
#    date_rn, time_rn = set_date_time()

print("Okay... Now place the potatoes on the scanner...\n")
print("They cannot be touching!!!\n")
yn_reply = recursive_YesNo("Enter y when ready...\n")
if (yn_reply == "y"):
    print("Okay...capturing scan\n")
    print("Clone: " + str(clone) + "\n" + "Replicate: " + str(rep) + "\n" + "\ncaptured!\n")
    capture_scan(clone, rep)
    print("Scan completed.\n")
    exit()
