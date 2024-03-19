A quick and dirt python script that allows average power per-lap/interval to be displayed on screen in Zwift because for some fkn reason that isn't already a feature?!?

To run the script, download or copy it to a text file. 
Make sure you have python installed, then run it as:
python Add_avgp_to_zwo.py

It will bring up a prompt to input a directory for the workoutfiles
I set it to show the default location Zwift usually puts them when you download the app \
which is usually in the "documents" folder on most systems, and then the folder that contains
the workouts for a given user is usually some string of numbers and has all the .ZWO files inside. 

Point the script to that, and then select the option to expand grouped intervals and click enter.
Leave the output folder path blank, it will make a new one within the input which is best. 

The expand grouped interval option is needed to compute the average power per-lap when the workout 
has a "block" of On-Off intervals that repeats. The script just expands these blocks into individual intervals. 

I hope it works for yall. 

https://youtube.com/shorts/dLwe9rXiLtY?feature=share
