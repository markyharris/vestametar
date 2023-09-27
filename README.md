# VestaMETAR
<p align="center"><img src=https://github.com/markyharris/vestametar/raw/main/static/mult2.jpg width="400"></p>
Display Airport METAR data on a Vestaboard

Visit https://www.vestaboard.com/ to learn more about the Vestaboard. 

A METAR is weather data for an airport. It provides pilots with most 
everything a pilot needs to make go/no-go decisions. These have been around for a long time
and are typically quite cryptic. Decoding them and understanding the data is part of learning to fly.
To learn more about the structure of METAR's visit; https://metar-taf.com/explanation.

This software was written in Python 3 to function on a Windows computer running Unix or, preferably a Raspberry Pi running Unix. 
There are a number of online sites that will host Python scripts as well. Examples are PythonAnywhere and Heroku, although this hasn't been tested.

Vestaboard hosts a number of apps that display info on their boards called Vestaboard+. Unfortuneatly this is a monthly 
subscription and I felt that access to these apps should have been included with the high cost of the board. So I set about 
writing this app that could be run locally to display the data I was interested in as a pilot. The nice thing about how this works 
is that you can also use other apps from Vestaboard+ while still running the VestaMETAR app locally.

<b>To install:</b><br>
Clone this repository to your Raspberry Pi by entering the following in the command line;<br>
<code>git clone https://github.com/markyharris/vestametar.git</code><br>

This will create a new directory called 'vestametar' and copy all the needed files into it.<br>
There are 2 files that need to be run at startup;<br>
<code>webapp.py</code> creates a web server that provides a web interface to make controlling the board easier. More on this after the installation info.<br>
<code>vestametar.py</code> is the script that goes out to the FAA site to grab the METAR data, format it and send it to the Vestaboard.<br>

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
 
<b>Test 1</b><br>
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

<b>NOTE:</b> Depending on the username used, the first 'vestametar' above will need to be changed. For instance;<br>
<code>sudo python3 /home/<b>pi</b>/vestametar/webapp.py &</code><br>
<code>sudo python3 /home/<b>pi</b>/vestametar/vestametar.py &</code><br>

Be sure to save the changes and return the vestametar directory;<br>
<code>ctrl-x</code><br>
<code>Y</code><br>
<code>cd ~</code><br>
<code>cd vestametar</code><br>

<b>Test 2</b><br>
Reboot the RPi now to test to be sure the rc.local will properly run 'webapp.py' and 'vestametar.py'.<br>
<code>sudo reboot now</code><br>

After it reboots, the Vestaboard should update the display automatically.<br>
Next, go to a browser on a computer/tablet/phone that is on the same WiFi network as the RPi and enter the RPi's IP address + ':5000' into the URL bar. For instance;<br>
<code>http://192.168.1.32:5000</code><br>

If the web admin page is displayed in the browser, then all is good.<br>

<b>Web Admin Page</b><br>
<p align="center"><img src=https://github.com/markyharris/vestametar/raw/main/static/webadmin.jpg width="400"></p>

To access the web admin enter the RPi's URL plus ':5000' into your web browser. The URL is displayed by the RPi on a monitor if connected 
upon boot up. When webapp.py initializes, it also displays the full URL to access the admin web page. So take a look for this. Another way to get 
the URL, you can access your router devices and look for the Raspberry Pi listed.<br>

There are 2 styles of METAR display; Multi airports and Single airports. Multi airport displays will display the flight categories of multiple airports 
on one screen, while single airport displays will display more information from a single airport on the Vestaboard. Each have the advantages. All can be 
rotated through or the user can select only the ones that are desired.<br>

Each type of display provides a pulldown menu to select the time interval between screen updates in minutes. Select as desired.<br>

Finally, a textbox with airport ids is provided for each type of display. For instance for the multi airport displays;
KFLG,KSEZ,KLAX,KPHX,KGEU,KINW,KBOS,KDAL,KDVT<br>
Add as many as 12 airports to this textbox. The 12 airport display will display the flight categories for all 12. The 4 airport display will display 
the first 4 of the list. If there are less than 12 airports, the display will adjust to the fewer number of airports. 

For the single airport display, you can put as many airports as desired. However, each airport in the list will be cycled through at the time interval selected before 
moving on to the next display format selected, which could take quite a bit of time.

Once selections have been made, click the 'Submit' button. After a moment the display will update, and continue updating at the time interval selected.<br>

<b>Misc</b><br>
In the Vestaboard settings at web.vestaboard.com the user has the ability to select 'Quiet Hours' time. This app will see an error occur when it attempts to 
update the Vestaboard display and it will simply wait the selected time interval before it attempts to update again. This will continue till the 'Quiet Hours' period 
has expired. So if the 'Quiet Hours' ends at 7 am, and the time interval selected is 10 minutes, the display will update somewhere between 7:01 am and 7:10 am.<br>

If there is an error in handling the raw METAR data, the app will attempt a soft landing by simply waiting the selected time interval before getting new METAR data. 
If another error occurs, it will continue to wait and retry again. Once the METAR data is properly decoded, the display will update again. So its possible that the info 
currently displayed on the Vestaboard is older than expected. Each display will show the time in which the update occurred to help determine how current the data is.<br>

This software is evolving and as of this writing, code for using a PIR (motion sensor) is available to play with. In the file 'vestametar.py' is a variable 'use_pir' that 
is set to '0' which ignores the use of the motion sensor. If its desirable to play with this feature, simply set this variable to '1'. i.e. 'use_pir=1' and save. 
The software is using pin 11 for the motion sensor reading but this can be changed as necessary in 'vestametar.py' if desired.<br>



