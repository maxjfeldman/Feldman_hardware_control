#!/usr/bin/env python3

## This is a script to collect images from a Nikon D7100 camera
## Written by Max Feldman USDA-ARS Prosser, WA

program_name = "RPi_NikonD7100_control.py"
version = 0.01

## Import python libraries
from time import sleep
#from serial import Serial
import csv
#import numpy
#from pylab import *
import datetime
import os.path
#import matplotlib.pyplot as plt
#import cv2
import sys
from optparse import OptionParser
import re
import glob
#from picamera import PiCamera
#import pandas as pd
#import gphoto2 as gp
import subprocess


## Get the pwd
pwd = os.getcwd()
subprocess.call(["pkill", "-f", "gphoto2"])

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
        return(recursive_YesNo("I don't understand your answer. 'y' or 'no' please\n"))

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

def get_Sample(question):
    sample = input(question)
    print("You are imaging sample: ", sample)
    reply = recursive_YesNo("Is this correct? (y|n) \n")
    if reply == 'y':
        print("Great. Will will work on: ", sample)
        return sample
    else:
        print("Darn. Lets enter it again.")
        return(get_Sample(question))

def capture_image(sample):
    outfile_name = outfile_path + "/" + str(sample) + ".jpg"
    subprocess.call(["gphoto2", "--set-config", "iso=100"])
    subprocess.call(["gphoto2", "--set-config", "whitebalance=7"])
    subprocess.call(["gphoto2", "--set-config", "/main/capturesettings/f-number=0"])
    subprocess.call(["gphoto2", "--set-config", "/main/capturesettings/shutterspeed=17"])
    if os.path.exists(outfile_name):
        print("This file exists. Perhaps you have already imaged this sample.\nAdd a .1, .2, .3, etc. to replicate number if a repeat\n")
        new_name = get_Sample("Please enter a different sample name. \n")
        capture_image(new_name)
    else:
        print("We are capturing an image of sample: " + str(sample))
        print("We are writing to: "+outfile_name)
        subprocess.call(["gphoto2", "--capture-image-and-download", "--filename", outfile_name,"--force-overwrite", "--keep-raw"])

def set_date_time():
    date_rn = input("Please enter the correct date.\nFormat is: YYYY-MM-DD (example: 2020-01-20\n")
    time_rn = input("Please enter the correct time (military time).\nFormat is: HH:MM:SS (23:10:00)\n")
    yn = input("Are the date: " + str(date_rn) + "\nand time: " + str(time_rn) +"\nCorrect? (y|n)")
    if (yn == "y"):
        print("Okay.")
        date_time = date_rn + " " + time_rn
        subprocess.call(["sudo", "date", "-s", date_time])
        return(date_rn, time_rn)
    else:
        print("Lets try again...")
        return(set_date_time())

########################
## Main program


## Remind the user what they are running
print("You are using " + str(program_name) + " version " + str(version))
sleep(1)

print("Output file name is: ", outfile, "\n", "User name is: ", user_name, "\n")
sleep(1)

## Ask user if the arguments are correct
value = recursive_YesNo("Does this look right?")

if value == 'n':
    change_arg("What argument would you like to change?  -o [outfile] -u [user] \n")
else:
    print("No change needed\n")


## If no directory to store data is present, go ahead and create it
#outfile_path = "/media/pi/FD2D-7416" + "/" + outfile
outfile_path = pwd + "/" + outfile

if os.path.exists(outfile_path):
    print("This directory already exists. We will write results to this folder\n")

if not os.path.exists(outfile_path):
    print("\n" + "No file directory named: " + str(outfile_path) + "\n")
    print("\n" + "Creating the directory\n" + str(outfile_path) + "\n")
    os.makedirs(outfile_path)

## Check date with user
#print("\nLets check the date and time to make sure it is accurate...\n")

## Get a datetime object
datetime_rn = datetime.datetime.now()

## Extract strings from object corresponding to date and time
date_rn = str(datetime_rn.date())
time_rn = datetime_rn.time().strftime("%H:%M:%S")

#print("The date is:\t" + date_rn)
#print("The time is:\t" + time_rn)
#sleep(1)

## Check to see if this is info is correct
#usr_input = input("Does this look accurate?...(y|n)\n")
#print(usr_input)
#if usr_input == 'y':
#    print("Great...\n")
#else:
#    print("Okay. Lets fix this. \n")
#    date_rn, time_rn = set_date_time()

exit = input("Would you like to exit (y|n)?\n")

print("You said: " + exit)

#summary_table = pd.DataFrame(columns=['sample', 'date_rn', 'time_rn', 'user_name', 'outfile_path'])

while(exit == "n"):
    ## Get a datetime object
    ## Ask the user what sample they are measuring
    sample = get_Sample("Scan or enter sample are you imaging?\n")
    print("Now place the potatoes on the black background of the imaging system. \n")
    sleep(1)
    print("They cannot be touching!!!\n")
    sleep(1)
    yn_reply = recursive_YesNo("Enter y when ready...\n")
    if (yn_reply == "y"):
        ## Image the potato with the numbers side up
        datetime_rn = datetime.datetime.now()
        ## Extract strings from object corresponding to date and time
        date_rn = str(datetime_rn.date())
        time_rn = datetime_rn.time().strftime("%H:%M:%S")
        sleep(1)
        print("Okay...\n")
        out_entry = list()
        out_entry.extend([sample, date_rn, time_rn, user_name, outfile_path])
        #entry_row = pd.DataFrame([out_entry], columns=['sample', 'date_rn', 'time_rn', 'user_name', 'outfile_path'])
        print(sample)
        capture_image(sample)
        #summary_table = summary_table.append(entry_row,)
        print("Image captured!\n")
        # Image the other side of the potato
        #print ("Flip the potatoes over to image the other side\n")
        #yn_reply = recursive_YesNo("Enter y when ready...\n")
        #if (yn_reply == "y"):
        #    side = 2
        #    light = "std"
        #    print("Okay...\n")
        #    datetime_rn = datetime.datetime.now()
        #    ## Extract strings from object corresponding to date and time
        #    date_rn = str(datetime_rn.date())
        #    time_rn = datetime_rn.time().strftime("%H:%M:%S")
        #    out_entry = list()
        #    out_entry.extend([sample, date_rn, time_rn, user_name, outfile_path])
        #    entry_row = pd.DataFrame([out_entry], columns=['sample', 'date_rn', 'time_rn', 'user_name', 'outfile_path'])
        #    #capture_image(sample)
        #    summary_table = summary_table.append(entry_row,)
        #   print("Side 2 captured!\n")
    #out_table_path = outfile_path + "/photo_metadata.csv"
    #summary_table.to_csv(out_table_path, mode='a', header=False, encoding='utf-8')
    exit = input("Would you like to exit (y|n)?\n")