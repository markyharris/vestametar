# vestametar.py - Mark Harris 6-2023
# Using the Vestaboard Display - https://www.vestaboard.com/
# Based on ShaneSutro/Vestaboard library at https://github.com/ShaneSutro/Vestaboard

# Command line variables can be passed to tweak the behavior of the program.
# Example: 'sudo python3 ledmap.py interval=120 use_wipe=0 time_display=0'
# This command will run the software with 2 min intervals between updates with no wipes and no clock
# Do not add spaces around the '=' sign. Below is the list of available commands;

# This software uses flask to create a web admin page that will control the behavior for the display.
# To access the admin page enter the IP address for the RPi and append ':5000' to it.
# For example, if the RPi is assigned the IP address, 192.168.0.32, then add ':5000' and enter;
# '192.168.0.32:5000' into a web browser that is on the same local network as the RPi.
# The file 'data.txt' holds the values for the variables that controls its behavior.


# imports
from vestaboard import Board # pip install Vestaboard
from vestaboard.formatter import Formatter
import time
import sys
import os
import urllib
import requests
import config
from routines import *
from characters import *
import RPi.GPIO as GPIO 

# Setup PIR GPIO's
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)         # Read output from PIR motion sensor
GPIO.setup(3, GPIO.OUT)         # LED output pin
use_pir = 0                     # 1 = yes, 0 = no
time_between_message = 1 * 60   # in minutes. This will keep the sensor from activating message for this time.
pir = 0                         # Set sensor to no movement


# Default Variables - Edit these to provide a default starting point. These are altered by the web interface
# If more displays are added, add to this area, along with display_flgs_lst and display_lst below in code.
flg_raw_metar_string = 1
flg_display_mult_airports2 = 1
flg_display_mult_airports1 = 1
flg_display_fc_large = 1
flg_display_decoded_metar = 1
flg_display_large_arrow = 0

# Config.py Variables - Edit config.py with different airports if running from cmd line. Otherwise use web interface to change values.
airports = config.airports
airports_fc = config.airports_fc
interval = config.interval # mins for update of data
interval_fc = config.interval_fc # mins for update of data - used for multiple airports fc

# Misc Variables
PATH = '/home/vestametar/vestametar/' 
url = config.url #"https://tgftp.nws.noaa.gov/data/observations/metar/stations/"
content = []
info = []

# Instantiate vboard
vboard = Board(apiKey=config.api_key, apiSecret=config.api_secret, subscriptionId=config.subscription_id)


# Process variables passed via command line, or from web admin page
# If new variables are to be used from the cmd line, add it to this list
variables = ['interval',
     'interval_fc',
     'raw_metar_string',
     'display_mult_airports2',
     'display_mult_airports1',
     'display_fc_large',
     'display_decoded_metar',
     'display_large_arrow',
     'airports',
     'airports_fc'
     ]

if len(sys.argv) > 1: # Grab cmdline variables and assign them properly
    print(sys.argv) # debug
    
    for j in range(1,len(sys.argv)):
        info.append(sys.argv[j].split("="))
#        print(info) # debug
        
    for j in range(len(info)):
        var = info[j][0]
        val = info[j][1]
        print("!-->"+var+"-"+val) # debug

        if var in variables:
            if var == 'interval':
                interval = int(val)
            elif var == 'interval_fc':
                interval_fc = int(val)
                
            elif var == 'raw_metar_string':
                print("HERE!!!") # debug
                flg_raw_metar_string = int(val)
                print(flg_raw_metar_string)
                
            elif var == 'display_mult_airports2':
                flg_display_mult_airports2 = int(val)
            elif var == 'display_mult_airports1':
                flg_display_mult_airports1 = int(val)                    
            elif var == 'display_fc_large':
                flg_display_fc_large = int(val)
            elif var == 'display_decoded_metar':
                flg_display_decoded_metar = int(val)
            elif var == 'display_large_arrow':
                flg_display_large_arrow = int(val)
            elif var == 'airports':
                val = val[1:len(val)-1]
                airports = val.split(',')
            elif var == 'airports_fc':
                val = val[1:len(val)-1]
                airports_fc = val.split(',')
                    
    print("\nUsing Cmdline variables rather than defaults.")
    print(interval, interval_fc, flg_raw_metar_string, flg_display_mult_airports2, flg_display_mult_airports1, flg_display_fc_large,\
          flg_display_decoded_metar, flg_display_large_arrow, airports, airports_fc)
else:
    print("No cmd line variables, using default values.")
    print(interval, interval_fc, flg_raw_metar_string, flg_display_mult_airports2, flg_display_mult_airports1, flg_display_fc_large,\
          flg_display_decoded_metar, flg_display_large_arrow, airports, airports_fc)


# Generic Functions
def get_data():
    f=open(PATH + "data.txt", "r")
    Lines = f.readlines()
    display = str(Lines[0].strip())
    fl_interval = Lines[1].strip()
    fl_interval_fc = Lines[2].strip()
    fl_raw_metar_string = Lines[3].strip()    
    fl_display_mult_airports2 = Lines[4].strip()
    fl_display_mult_airports1 = Lines[5].strip()
    fl_display_fc_large = Lines[6].strip()
    fl_display_decoded_metar = Lines[7].strip()
    fl_display_large_arrow = Lines[8].strip()
    fl_airports = Lines[9].strip()
    fl_airports_fc = Lines[10].strip()    
    f.close()
    
    # Check variable is surrounded by [ ]
    if fl_airports[0] != '[':
        fl_airports = '[' + fl_airports
    len1 = int(len(fl_airports)-1)
    if fl_airports[len1] != ']':
        fl_airports = fl_airports + ']'
    print(fl_airports) # debug

    if fl_airports_fc[0] != '[':
        fl_airports_fc = '[' + fl_airports_fc
    len2 = int(len(fl_airports_fc)-1)
    if fl_airports_fc[len2] != ']':
        fl_airports_fc = fl_airports_fc + ']'
    print(fl_airports_fc) # debug
    
    return (display,fl_interval,fl_interval_fc,fl_raw_metar_string,fl_display_mult_airports2,fl_display_mult_airports1,\
            fl_display_fc_large,fl_display_decoded_metar,fl_display_large_arrow,fl_airports,fl_airports_fc)

def get_metar_string(airport):
    # get Metar data
    result = urllib.request.urlopen(url+airport+".TXT").read() 
    string = result.decode('utf-8')
    content = string.split('\n')
#    print(content) # debug
    metar_string = content[1] # extract raw metar string
    return(metar_string)


# Functions for different METAR Data layouts
def raw_metar_string(): # Display raw METAR string with Flight Category Tile
    time_string = time.strftime("%I:%M", time.localtime()) # %H=24 hour, %I=12 hour
    display_text = "{70}Airport Metars-"+time_string+"\n{70}{70}"

    for airport in airports:
        print(airport) # debug
        metar_string = get_metar_string(airport)

        flight_cat = determine_flight_category(metar_string) # decode flight category
        fc_color = flight_cat_to_color(flight_cat) # grab proper display
            
        # print to board
        vboard.post(time_string+"-"+"{"+fc_color+"}"+metar_string)
        time_sleep(interval)
        print('Interval in raw_metar_string is:',interval) # debug
#        time.sleep(interval * 60) # Mins * Secs - delay between updates


def display_mult_airports1(): # Display up to 12 airport's ID and flight category color next to them
    count = 1
    time_string = time.strftime("%I:%M%p", time.localtime()) # %H=24 hour, %I=12 hour
    display_text = "{70}Airport Metar-"+time_string+"\n{70}{70}"

    for airport in airports_fc:
#        print(airport) # debug
        # get Metar data
        metar_string = get_metar_string(airport)
        
        flight_cat = determine_flight_category(metar_string) # decode flight category
#        print(flight_cat,metar_string) # debug
        
        fc_color = flight_cat_to_color(flight_cat) # get proper color
        display_text = display_text+"{"+fc_color+"}"+airport+" "
        
        if count == 3 or count == 6 or count == 9:
            display_text = display_text+"\n{70}{70}"
        
        if count > 11: # limit number of airports displayed to 12.
            break
        count += 1

    display_text = display_text+"\n{66}VFR {67}MVFR {63}IFR {68}LIFR"
    print(display_text) # debug
    vboard.post(display_text)
    time_sleep(interval_fc)
#    time.sleep(interval_fc * 60) # Mins * Secs - delay between updates
    count = 1


def display_fc_large(): # Display a single airport's flight category in large letters
    time_string = time.strftime("%I:%M%p", time.localtime()) # %H=24 hour, %I=12 hour

    for airport in airports:
        display_raw = Formatter().convert(airport+"-"+time_string) # create raw data         
        
        # get Metar data
        metar_string = get_metar_string(airport)
        flight_cat = determine_flight_category(metar_string) # decode flight category

        fc_color = flight_cat_to_color(flight_cat) # grab proper display
        if fc_color == '66': # VFR
            char_output = chars_vfr
        elif fc_color == '67': # MVFR
            char_output = chars_mvfr
        elif fc_color == '63': # IFR
            char_output = chars_ifr
        else: # LIFR
            char_output = chars_lifr
            
        for j in range(len(display_raw)):
            char_output[0][j+5] = display_raw[j] # embed airport and time in first line
            
        print(airport+"\n"+str(char_output)+"\n") # debug
        vboard.raw(char_output) # send to vestaboard
        time_sleep(interval)
#        time.sleep(interval * 60) # Mins * Secs - delay between updates
        

def display_large_arrow(): # Display a single airport's METAR flight category tile and wind direction
    time_string = time.strftime("%I:%M", time.localtime()) # %H=24 hour, %I=12 hour
    display_text = "{70}Airport Metars-"+time_string+"\n{70}{70}"

    for airport in airports:
        display_raw = Formatter().convert(airport+"-"+time_string) # create raw data         

        # Get Metar String
        metar_string = get_metar_string(airport)
        
        # Get wind speed and direction
        wind_speed,wind_dir = get_wind_speed_direction(metar_string)
        if wind_dir == None:
            wind_dir = 'vrb degrees'
        print(wind_dir) # debug
        wspd = str(wind_speed)
        wdir = str(wind_dir)
#        print(wspd,wdir) # debug
        
        spd_lst = wspd.split()
        spd_lst[1] = 'kts'
        if len(spd_lst[0]) == 1:
            spd_lst[0] = "0"+spd_lst[0]
        wspd = spd_lst[0]+" "+spd_lst[1]
        
        dir_lst = wdir.split()
        dir_lst[1] = 'deg'
        if len(dir_lst[0]) == 1:
            dir_lst[0] = "00"+dir_lst[0]
        elif len(dir_lst[0]) == 2:
            dir_lst[0] = "0"+dir_lst[0]

        wdir = dir_lst[0]+" "+dir_lst[1]
        print(wspd,wdir) # debug

        
        spd_lst_raw = Formatter().convert(wspd,byWord=True) # create raw data         
        dir_lst_raw = Formatter().convert(wdir,byWord=True) # create raw data         
        print(spd_lst_raw,dir_lst_raw) # debug
        
        # Get Wind Dir Arrow
        if dir_lst[0] == 'vrb':
            dir_lst[0] = '0'
        arrow = winddir(int(dir_lst[0]))
#        print(arrow) # debug

        # Get flight category and proper color representation
        flight_cat = determine_flight_category(metar_string) # decode flight category
        fc_color = flight_cat_to_color(flight_cat) # grab proper display

        # Build Raw data for screen
        for j in range(6): # Fill screen template with Flight Cat Color
            for k in range(22):
                template[j][k] = int(fc_color)

        for j in range(0,6): # Fill part of screen with black
            for k in range(2,20):
                template[j][k] = 0
           
        for j in range(1,6): # Populate screen with proper arrow
            for k in range(8,13):
#                        print(j,k,k-8) # debug
                template[j][k] = arrow[j-1][k-8]
                
        for k in range(len(display_raw)): # embed airport and time in first line
            template[0][k+6] = display_raw[k]
            
        for j in range(2,4): # embed wind speed
            for k in range(len(spd_lst_raw[j-2])):
#                        print(j,k,k+2) # debug
                template[j][k+3] = spd_lst_raw[j-2][k]
            
        for j in range(2,4): # embed wind direction
            for k in range(len(dir_lst_raw[j-2])):
#                        print(j,k,k+2) # debug
                template[j][k+15] = dir_lst_raw[j-2][k]

        print(template) # debug
        
        # print to board
        vboard.raw(template) #"{"+fc_color+"}"+metar_string)
        time_sleep(interval)
#        time.sleep(interval * 60) # Mins * Secs - delay between updates


def display_decoded_metar(): # Display a single airport's Decode METAR data
    time_string = time.strftime("%I:%M%p", time.localtime()) # %H=24 hour, %I=12 hour
    display_text = "{70}Airport Metars-"+time_string+"\n{70}{70}"

    for airport in airports:
        ceiling = ["","","","","","","","",""]
        
        # Get Metar String
        metar_string = get_metar_string(airport)
        
        # Get Flight Cat and Color Tile
        flight_cat = determine_flight_category(metar_string) # decode flight category
        fc_color = "{"+flight_cat_to_color(flight_cat)+"}" # grab proper display
        
        # Get Decoded Metar Data
        station_id,time1,wind_dir,wind_speed,wind_gust,vis,temp,\
        dewpt,press,weather,sky,len_sky,_remarks = get_decoded_metar(metar_string)

        print(station_id,time_string,wind_dir,wind_speed,wind_gust,vis,temp,dewpt,press,weather,sky,len_sky,_remarks)
        
        if len_sky == 1:
            ceiling[0] = "SKY CLEAR"
            ceiling[1] = ""
            print("<--") # debug
            print(ceiling)
        else:
            for j in range(len_sky):
                print(j)
                ceiling[j]=str(sky[j][0])+str(sky[j][1])
                print("-->") # debug
                print(ceiling)
            
        if wind_gust == "None":
            wind_gust = "G 0"
        else:
            temp_lst = wind_gust.split()
            wind_gust = "G"+str(temp_lst[0])
        
        # Build display String
        decoded_metar = fc_color+station_id+" "+time_string+"\n" # Line 1
        decoded_metar = decoded_metar+fc_color+wind_dir+" "+wind_speed+"\n" # Line 2
        decoded_metar = decoded_metar+fc_color+wind_gust+" "+vis+" "+temp+"\n" # Line 3
        decoded_metar = decoded_metar+fc_color+dewpt+" "+press+"\n" # Line 4
        decoded_metar = decoded_metar+fc_color+ceiling[0]+"\n" # Line 5
        decoded_metar = decoded_metar+fc_color+ceiling[1]# Line 6
        
        # print to board
        print(decoded_metar)
        vboard.post(decoded_metar)

        time_sleep(interval)
#        time.sleep(interval * 60) # Mins * Secs - delay between updates


def display_mult_airports2(): # Display up to 12 airport's ID and flight category color next to them
    count = 1
    data_lst = []
    display_text = ""
    
    time_string = time.strftime("%I:%M%p", time.localtime()) # %H=24 hour, %I=12 hour
    tstring1 = time_string[:1]
    tstring2 = time_string[1:2]
    tstring3 = time_string[2:3]
    tstring4 = time_string[3:4]
    tstring5 = time_string[4:5]
    tstring6 = time_string[5:6]
#    print(time_string,tstring1,tstring2,tstring3,tstring4,tstring5,tstring6) # debug
 
    for airport in airports_fc:
        print(airport) # debug
        # get Metar data
        metar_string = get_metar_string(airport)
        
        flight_cat = determine_flight_category(metar_string) # decode flight category
        fc_color = flight_cat_to_color(flight_cat) # get proper color
        
        # Get Decoded Metar Data
        station_id,time1,wind_dir,wind_speed,wind_gust,vis,temp,\
        dewpt,press,weather,sky,len_sky,_remarks = get_decoded_metar(metar_string)
        
        print("***",station_id,time1,wind_dir,wind_speed,wind_gust,vis,temp,\
        dewpt,press,weather,sky,len_sky,_remarks,"***") # debug
        
        # store metar data to display in list then format the data to be printed to vestaboard below.
        if len_sky == 0:
            sky[0][0] = "    "
            sky[0][1] = "    "
            
        try:
            if len(str(sky[0][0])) == 2:
                pad = "{70}"
            else:
                pad = ""
        except Exception as e:
            sky[0][0] = "    "
            
        if "Non" in wind_dir:
            wind_dir = "VRB"
        elif "d" in wind_dir[:3]:
            wind_dir = wind_dir[:2] + "{70}"
        else:
            wind_dir = wind_dir[:3]
            
        # fix fractional mileage to fit alotted space on vestaboard
        if "1 3/4" in vis or "1 1/2" in vis:
            vis = '2'
        elif "1 1/4" in vis:
            vis = '1'
        elif "1/2" in vis:
            vis = '1/2'
        elif "1/4" in vis:
            vis = '1/4'
       
        if str(sky[0][1])[:4] == 'None':
            data_lst.append((fc_color,airport,wind_dir,wind_speed[:2],vis[:3],str(sky[0][0]+pad),"{70}"+"{70}"+"{70}"+"{70}"))
        else:
            data_lst.append((fc_color,airport,wind_dir,wind_speed[:2],vis[:3],str(sky[0][0]+pad),str(sky[0][1])[:4]))
#        print('XXX>',data_lst) # debug
        
        if count > 3: # limit number of airports displayed to 4.
            break
        count += 1
        
    # format the data to be printed to vestaboard
#    print(data_lst[0])
    # line 1
    display_text = "{"+data_lst[0][0]+"}"+data_lst[0][1]+"{"+data_lst[1][0]+"}"+data_lst[1][1]+"{"+data_lst[2][0]+"}"+data_lst[2][1]+"{"+data_lst[3][0]+"}"+data_lst[3][1]+"{70}"+tstring1+"\n"
    # line 2
    display_text = display_text+"{"+data_lst[0][0]+"}"+data_lst[0][2]+"@"+"{"+data_lst[1][0]+"}"+data_lst[1][2]+"@"+"{"+data_lst[2][0]+"}"+data_lst[2][2]+"@"+"{"+data_lst[3][0]+"}"+data_lst[3][2]+"@{70}"+tstring2+"\n"
    # line 3
    display_text = display_text+"{"+data_lst[0][0]+"}"+data_lst[0][3]+"kt"+"{"+data_lst[1][0]+"}"+data_lst[1][3]+"kt"+"{"+data_lst[2][0]+"}"+data_lst[2][3]+"kt"+"{"+data_lst[3][0]+"}"+data_lst[3][3]+"kt"+"{70}"+tstring3+"\n"
    # line 4
    display_text = display_text+"{"+data_lst[0][0]+"}"+data_lst[0][4]+"m"+"{"+data_lst[1][0]+"}"+data_lst[1][4]+"m"+"{"+data_lst[2][0]+"}"+data_lst[2][4]+"m"+"{"+data_lst[3][0]+"}"+data_lst[3][4]+"m{70}"+tstring4+"\n"
    # line 5
    display_text = display_text+"{"+data_lst[0][0]+"}"+data_lst[0][5]+" "+"{"+data_lst[1][0]+"}"+data_lst[1][5]+" "+"{"+data_lst[2][0]+"}"+data_lst[2][5]+" "+"{"+data_lst[3][0]+"}"+data_lst[3][5]+"{70}{70}"+tstring5+"\n"
    # line 6
    display_text = display_text+"{"+data_lst[0][0]+"}"+data_lst[0][6]+"{"+data_lst[1][0]+"}"+data_lst[1][6]+"{"+data_lst[2][0]+"}"+data_lst[2][6]+"{"+data_lst[3][0]+"}"+data_lst[3][6]+"{70}"+tstring6

    print(display_text)
    vboard.post(display_text)
    time_sleep(interval_fc)
#    time.sleep(interval_fc * 60) # Mins * Secs - delay between updates
    count = 1


def store_pid(PID):
    f= open(PATH + "vpid.txt","w+")
    f.write(str(PID))
    f.close()
    return (True)


def time_sleep(interval):
    global pir
    global time_between_message
    timer_count = 0
    interval = interval * 60
    
    if use_pir == 0: # if pir is not desired, then just sleep
        print("In Sleep Interval",interval)
        time.sleep(interval)
    else:
        #Setup timed loop for updating FAA Weather that will run based on the value of 'interval' which is a user setting
        timeout_start = time.time() #Start the timer. When timer hits user-defined value, go back to outer loop to update FAA Weather.
        
        while time.time() < timeout_start + interval:
            timer_count = round(time.time() - timeout_start)
             
            time.sleep(1)
            pir = GPIO.input(11)
            print("\033[91m:Interval ",interval,":PIR State ",pir,":Timer", timer_count, " \r", end='', flush=True)
#            print("In Timer",timer_count,":Interval ",interval,":PIR State ",pir) # display num of seconds in loop

            
            if pir == 1 and time_between_message > timer_count:                 #When output from motion sensor is LOW
                time_string = time.strftime("%I:%M%p", time.localtime()) # %H=24 hour, %I=12 hour
                print ("\nMovement Detected - :PIR State",pir)
                pir = 0
                time.sleep(10)
                vboard.post("Hello King Mark "+time_string)
                time.sleep(10)
        

# Start of executed code
if __name__ == "__main__":
    PID = os.getpid()
    store_pid(PID)
    
    display_lst = [
        raw_metar_string,
        display_mult_airports2,
        display_mult_airports1,
        display_fc_large,
        display_decoded_metar,
        display_large_arrow,
    ]
    
    display_flgs_lst = [
        flg_raw_metar_string,
        flg_display_mult_airports2,
        flg_display_mult_airports1,
        flg_display_fc_large,
        flg_display_decoded_metar,
        flg_display_large_arrow,
        ]
    
      
    
#    if len(sys.argv) <= 1:
#        vboard.post("VestaMetar Starting Up")
#        display,interval,interval_fc,raw_metar_string,display_mult_airports2,display_mult_airports1,\
#                   display_fc_large,display_decoded_metar,display_large_arrow,airports,airports_fc = get_data()
#        interval = int(interval)
#    print('Interval',interval)
#        time.sleep(30)  
        
    while True:
        time_string = time.strftime("%I:%M%p", time.localtime()) # %H=24 hour, %I=12 hour
        
        try:    
#        for j in range(len(display_flgs_lst)):
#            print(display_flgs_lst) # debug
            for j,val in enumerate(display_flgs_lst):
#                print(j) # debug
                print("Value = "+str(display_flgs_lst[j])) # debug
                if display_flgs_lst[j] == 1:
                    display_lst[j]() # Run display routine from list above 
                    
                           
        except requests.HTTPError as e: # Check and handle if Vestaboard is in Quiet Mode
            # Need to check its an 404, 503, 500, 403 etc.
            status_code = e.response.status_code
            
            if status_code == 403 or status_code == 405:
                print('\n\033[91m---> HTTPError:',status_code,'- Vestaboard is currently unavailable, will try again shortly <---\033[0m',time_string)
                time_sleep(interval)
#               time.sleep(interval * 60) 

#            if status_code == 405:
#                print('!--->',e,time_string)

            else:
                print('\n\033[91m*** Status Code:',status_code)
            time_sleep(interval)
#            time.sleep(interval * 60) 


        except Exception as e:
            print('\n\033[91m<--->',e,time_string)
#            time.sleep(15)
#            vboard.post("One Moment Please"+" "+time_string)
            time_sleep(interval)
#            time.sleep(interval * 60) # If METAR hasn't changed, wait again to try.


                
