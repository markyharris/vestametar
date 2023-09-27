# webapp.py - Mark Harris
# for VestaMetar

from vestaboard import Board # pip install Vestaboard
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, Response
import time
import os
import sys
import subprocess as s
from config import *
import config

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# variables
PATH = config.PATH # '/home/vestametar/vestametar/'
display_lst = [
            "display_mult_airports2",
            "display_mult_airports1",
            "display_fc_large",
            "display_large_arrow",
            "display_decoded_metar"
            "fl_display_large_arrow"
            ]


# Instantiate vboard
vboard = Board(apiKey=api_key, apiSecret=api_secret, subscriptionId=subscription_id)


# Routes for flask
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route("/vestametar", methods=["GET", "POST"])
def vestametar():
    global display,fl_interval, fl_interval_fc, fl_raw_metar_string, fl_display_mult_airports2, fl_display_mult_airports1, fl_display_fc_large,\
           fl_display_decoded_metar, fl_display_large_arrow, fl_airports, fl_airports_fc, name, version
    
    print(os.name) # debug
    
    display,fl_interval,fl_interval_fc,fl_raw_metar_string,fl_display_mult_airports2,fl_display_mult_airports1,\
    fl_display_fc_large,fl_display_decoded_metar,fl_display_large_arrow,fl_airports,fl_airports_fc = get_data()

    templateData = {
        'fl_interval' : fl_interval,
        'fl_interval_fc' : fl_interval_fc,
        'fl_raw_metar_string' : fl_raw_metar_string,
        'fl_display_mult_airports2' : fl_display_mult_airports2,
        'fl_display_mult_airports1' : fl_display_mult_airports1,
        'fl_display_fc_large' : fl_display_fc_large,
        'fl_display_decoded_metar' : fl_display_decoded_metar,
        'fl_display_large_arrow' : fl_display_large_arrow,
        'fl_airports' : fl_airports,
        'fl_airports_fc' : fl_airports_fc,
        'name': name,
        'version': version,
        'display': display
        }

    if request.method == "POST": # Process info submitted from html file.
        display = request.form['display']
        # Process Input Boxes
        fl_interval = request.form['fl_interval']
        fl_interval_fc = request.form['fl_interval_fc']
                       
        # Process Checkboxes
        try:
            fl_raw_metar_string = request.form['fl_raw_metar_string'] # Checkbox
            fl_raw_metar_string = 1
        except:
            fl_raw_metar_string = 0 
        
        try:
            fl_display_mult_airports2 = request.form['fl_display_mult_airports2'] # Checkbox
            fl_display_mult_airports2 = 1
        except:
            fl_display_mult_airports2 = 0
        
        try:
            fl_display_mult_airports1 = request.form['fl_display_mult_airports1'] # Checkbox
            fl_display_mult_airports1 = 1
        except:
            fl_display_mult_airports1 = 0
        
        try:
            fl_display_fc_large = request.form['fl_display_fc_large'] # Checkbox
            fl_display_fc_large = 1
        except:
            fl_display_fc_large = 0
        
        try:
            fl_display_decoded_metar  = request.form['fl_display_decoded_metar'] # Checkbox
            fl_display_decoded_metar  = 1
        except:
            fl_display_decoded_metar  = 0
        
        try:
            fl_display_large_arrow  = request.form['fl_display_large_arrow'] # Checkbox
            fl_display_large_arrow  = 1
        except:
            fl_display_large_arrow  = 0
        
        # Process input boxes, multiline
        fl_airports = request.form['fl_airports']
        fl_airports_fc = request.form['fl_airports_fc']            

        # Write data to file
        write_data(display,fl_interval,fl_interval_fc,fl_raw_metar_string,fl_display_mult_airports2,fl_display_mult_airports1,\
        fl_display_fc_large,fl_display_decoded_metar,fl_display_large_arrow,fl_airports,fl_airports_fc)                   
        print("Writing Data to File")
                           
        variables1 = 'display='+str(display) +' '+'interval='+str(fl_interval) +' '+'interval_fc='+str(fl_interval_fc) +' '+'raw_metar_string='+str(fl_raw_metar_string) \
                         +' '+'display_mult_airports2='+str(fl_display_mult_airports2) +' '+'display_mult_airports1='+str(fl_display_mult_airports1) \
                         +' '+ 'display_fc_large='+str(fl_display_fc_large) +' '+'display_decoded_metar='+str(fl_display_decoded_metar) \
                         +' '+ 'display_large_arrow='+str(fl_display_large_arrow) +' '+ 'airports='+str(fl_airports) +' '+'airports_fc='+str(fl_airports_fc)
                            
        print("From HTML:",variables1) # debug

        if display == "off":
            if os.name == 'nt': # Check to see if script is being run under Windows
                PID = get_pid()
                killProcess(PID)
            else:
                os.system("ps -ef | grep 'vestametar.py' | awk '{print $2}' | xargs sudo kill")
                os.system('sudo python3 ' + PATH + 'vestametar.py '+ variables1+' &')

            flash("Turning Off VestaMetar Display")
            vboard.post("VestaMetar is OFF"+" "+time.strftime("%I:%M%p", time.localtime()))
            
        if display == "clear":
            if os.name == 'nt': # Check to see if script is being run under Windows
                PID = get_pid()
                killProcess(PID)
            else:
                os.system("ps -ef | grep 'vestametar.py' | awk '{print $2}' | xargs sudo kill")
                os.system('sudo python3 ' + PATH + 'vestametar.py '+ variables1+' &')

            flash("Turning Off and Clearing VestaMetar Display")
            vboard.post("")

        else:
            print(os.name) # debug
            if os.name == 'nt': # Check to see if script is being run under Windows
                PID = get_pid()
                killProcess(PID)
                os.system('python ' + PATH + 'vestametar.py '+ variables1+' &')            
            else: # Assume Unix 
                os.system("ps -ef | grep 'vestametar.py' | awk '{print $2}' | xargs sudo kill")
                os.system('sudo python3 ' + PATH + 'vestametar.py '+ variables1+' &')
                
            flash("Running VestaMETAR") 
        
        def convert_chkbox(name):
            if name == 1:
                name = '1'
            else:
                name = '0'
            return(name)
        
        fl_raw_metar_string = convert_chkbox(fl_raw_metar_string)
        fl_display_mult_airports2 = convert_chkbox(fl_display_mult_airports2)
        fl_display_mult_airports1 = convert_chkbox(fl_display_mult_airports1)
        fl_display_fc_large = convert_chkbox(fl_display_fc_large)
        fl_display_decoded_metar = convert_chkbox(fl_display_decoded_metar)
        fl_display_large_arrow = convert_chkbox(fl_display_large_arrow)
        
        templateData = {
            'fl_interval' : fl_interval,
            'fl_interval_fc' : fl_interval_fc,
            'fl_raw_metar_string' : fl_raw_metar_string,
            'fl_display_mult_airports2' : fl_display_mult_airports2,
            'fl_display_mult_airports1' : fl_display_mult_airports1,
            'fl_display_fc_large' : fl_display_fc_large,
            'fl_display_decoded_metar' : fl_display_decoded_metar,
            'fl_display_large_arrow' : fl_display_large_arrow,
            'fl_airports' : fl_airports,
            'fl_airports_fc' : fl_airports_fc,
            'name': name,
            'version': version,
            'display': display
            }

        return render_template("vestametar.html", **templateData)
    
    else:
        return render_template("vestametar.html", **templateData)

 
# Functions
def write_data(display,fl_interval,fl_interval_fc,fl_raw_metar_string,fl_display_mult_airports2,fl_display_mult_airports1,\
                fl_display_fc_large,fl_display_decoded_metar,fl_display_large_arrow,fl_airports,fl_airports_fc):
 
    f= open(PATH + "data.txt","w+")
    f.write('"'+str(display)+'"'+"\n")
    f.write(str(fl_interval)+"\n")
    f.write(str(fl_interval_fc)+"\n")
    f.write(str(fl_raw_metar_string)+"\n")
    f.write(str(fl_display_mult_airports2)+"\n")
    f.write(str(fl_display_mult_airports1)+"\n")
    f.write(str(fl_display_fc_large)+"\n")
    f.write(str(fl_display_decoded_metar)+"\n")
    f.write(str(fl_display_large_arrow)+"\n")
    f.write(str(fl_airports.strip())+"\n")
    f.write(str(fl_airports_fc.strip()))
    f.close()
    return (True)

    
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


def killProcess(pid):
    s.Popen('taskkill /F /PID {0}'.format(pid), shell=True)
    

def get_pid():
    f=open(PATH + "vpid.txt", "r")
    Lines = f.readlines()
    PID = Lines[0].strip()
    f.close()
    return(int(PID))

        
# Start of Flask
if __name__ == '__main__':
#    error = 1/0 # Force webapp to stop executing for debug purposes
    display,fl_interval,fl_interval_fc,fl_raw_metar_string,fl_display_mult_airports2,fl_display_mult_airports1,\
                   fl_display_fc_large,fl_display_decoded_metar,fl_display_large_arrow,fl_airports,fl_airports_fc = get_data()

    variables = 'display='+str(display) +' '+'interval='+str(fl_interval) +' '+'interval_fc='+str(fl_interval_fc) +' '+'raw_metar_string='+str(fl_raw_metar_string) \
                     +' '+'display_mult_airports2='+str(fl_display_mult_airports2) +' '+'display_mult_airports1='+str(fl_display_mult_airports1) \
                     +' '+ 'display_fc_large='+str(fl_display_fc_large) +' '+'display_decoded_metar='+str(fl_display_decoded_metar) \
                     +' '+ 'display_large_arrow='+str(fl_display_large_arrow) +' '+ 'airports='+str(fl_airports) +' '+'airports_fc='+str(fl_airports_fc)
    
    print("From GetData():",variables) # debug
    print("\n"+PATH + 'vestametar.py ' + variables) # debug
    
    app.run(debug=True, use_reloader=True, host='0.0.0.0') # use use_reloader=False to stop double loading

    
    print(os.name) # debug
    if os.name == 'nt': # Check to see if script is being run under Windows
        print('Running under Windows')
        PID = get_pid()
        killProcess(PID)
        os.system('python ' + PATH + 'vestametar.py '+ variables+' &')

    else: # Assume Unix
        print('Running under Unix')
        os.system("ps -ef | grep 'vestametar.py' | awk '{print $2}' | xargs sudo kill")
        os.system('sudo python3 ' + PATH + 'vestametar.py '+ variables+' &')
        
#    app.run(debug=True, use_reloader=True, host='0.0.0.0') # use use_reloader=False to stop double loading    
             