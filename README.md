# VestaMETAR
Display Airport METAR data on a Vestaboard

Visit https://www.vestaboard.com/ to learn more about the Vestaboard. 

METAR's are weather data for airports around the world. They provide pilots with most 
everything a pilot needs to make go/no-go decisions. These have been around for a long time
and are typically quite cryptic. Decoding them and understanding the data is part of learning to fly.
To learn more about the structure of METAR's visit; https://metar-taf.com/explanation.

This software was written in Python to function on a Windows computer running Unix or, preferable a Raspberry Pi running Unix. 
There are a number of online sites that will host Python scripts as well. Examples are PythonAnywhere and Heroku.

Vestaboard hosts a number of apps that display info on their boards called Vestaboard+. Unfortuneatly this is a monthly 
subscription and I felt that access to these apps should have been included with the high cost of the board. So I set about 
writing this app that could be run locally to display the data I was interested in as a pilot. The nice thing about how this works 
is that you can also use other apps from Vestaboard+ while still running the VestaMETAR app locally.

<b>To install:</b><br>
Clone this repository to your Raspberry Pi by entering the following in the command line;<br>
<code>git clone https://github.com/markyharris/vestametar.git</code><br>

This will create a new directory called 'vestametar' and copy all the needed files into it.<br>
There are 2 files that need to be run at startup;<br>
<code>webapp.py</code><br> creates a web server that provides a web interface to make controlling the board easier. More on this after the installation info.<br>
<code>vestametar.py</code><br> is the script that goes out to the FAA site to grab the METAR data, format it and send it to the Vestaboard.<br>

Once cloning is complete, open the config.py file and make a few edits;<br>
<code>cd vestametar</code><br>
<code>sudo nano config.py</code><br>

Visit; https://web.vestaboard.com/ and create an account, or login.<br>
Select 'API' from the left side<br>
Select 'Create new Installable' from the right side<br>
Enter a Title in the pop up box, i.e. 'VestaMETAR'<br>
Click 'Create and API Credential' button on the right side. A pop up box should allow you to choose your Vestaboard. Then click 'Create API Credentials'.<br>

<b>IMPORTANT</b>: Copy and paste these credentials into the config.py file <b>BEFORE</b> closing the box, otherwise you will lose the 'Secret' key.<br>
<code>api_key='Your Key'</code><br>
<code>api_secret='Your Key'</code><br>

There are some optional settings that can be tailored as well.<br>
<code>interval=</code> In minutes. This is the time in minutes between updating the Vestaboard for the 'airports' list.<br>
<code>interval_fc=</code> In minutes. This is the time in minutes between updating the Vestaboard for the 'airports_fc' list.<br>
<code>airports=</code> List of airports used on the display screens that display only 1 airport at a time.<br>
<code>airport_fc=</code> List of airports used on the display screens that display multiple airports at the same time.<br>

<b>NOTE:</b> The settings in the config.py file are used to run the app when not using the web based admin page which will be discussed shortly.<br>
 
<b>Test</b><br>
From the command line enter;<br>
<code>cd vestametar</code><br>
<code>sudo python3 vestametar.py</code><br>

The text output will show the data being grabbed from the FAA and the formatted data being sent to the Vestaboard. Then shortly after, the Vestaboard 
will display the METAR data using the settings in the config.py file.

Assuming that is working, we need to setup the RPi to run the app automatically upon boot up. From the command line, enter;<br>
<code>cd ~</code><br>
<code>cd /etc</code><br>
<code>sudo nano rc.local</code><br>

Add the following lines after the 'fi' and before the 'exit';<br>
<code>sleep 30</code><br>
<code>sudo python3 /home/vestametar/vestametar/webapp.py &</code><br>
<code>sudo python3 /home/vestametar/vestametar/vestametar.py &</code><br>

<b>NOTE:</b>depending on the username used, the first 'vestametar' above will need to be changed. For instance;<br>
<code>sudo python3 /home/<b>pi</b>/vestametar/webapp.py &</code><br>





