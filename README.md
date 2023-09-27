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

To install and run:<br>
Clone this repository to your Raspberry Pi by entering the following in the command line;<br>
git clone https://github.com/markyharris/vestametar.git<br>

This will create a new directory called 'vestametar' and copy all the needed files into it.<br>
There are 2 files that need to be run at startup;<br>
webapp.py<br>
vestametar.py<br>

webapp.py creates a web server that provides a web interface to make controlling the board easier. More on this after the installation info.<br>
vestametar.py is the script that goes out to the FAA site to grab the METAR data, format it and send it to the Vestaboard.<br>

Once cloning is complete, open the config.py file and make a few edits;<br>
cd vestametar<br>
sudo nano config.py<br>

Visit; https://web.vestaboard.com/ and create an account, or login.<br>
Select 'API' from the left side<br>
Select 'Create new Installable' from the right side<br>
Enter a Title in the pop up box, i.e. 'VestaMETAR'<br>
Click 'Create and API Credential' button on the right side. A pop up box should allow you to choose your Vestaboard. Then click 'Create API Credentials'.<br>
IMPORTANT: Copy and paste these credentials into the config.py file BEFORE closing the box, otherwise you will lose the 'Secret' key.<br>




