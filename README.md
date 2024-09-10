I should state first that the program will not run just by activating the python file, you will need to run the program within an iteration of Visual Studio (I used Visual Studio: Code). 
While it isn't necessary, you should run the debugger as well (it will only 'debug' if you use the 'Python File' debug option).

BUT BEFORE EVEN THAT you will need several packages installed, AND create the 'data' folder and import the right data into it.
The data comes from here, https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/data, create a 'data' folder in the same directory and put the .csv file into it.
If it isn't already, name it 'games.csv'.
As for the packages, the versions I used were not up to date at the time, so while it will probably run on modern stuff, it would be safer to install these versions of them.

- Python 3.11.5
- pandas 2.1.0 (run 'pip install pandas==2.1.0' in your command prompt)
- plotly 5.16.1 (run 'pip install plotly==5.16.1')
- dash 2.13.0 (run 'pip install dash==2.13.0')

If errors come up, its either because you already have those modules installed or your python version is too updated to run them. 
Again to stress, I have not tested this on the most up-to-date versions of these packages, but it should work.

With that out of the way, when you run the program in visual studio (code?) (its safer to use debugger here) it will come up with a line like this: 

"Dash is running on http://..." 

Take that http address and put it into your internet browser of choice. It will take a while for everything to load so don't do anything and make sure to stay on the same screen. 
DO NOT MINIMISE IT. 

~20 seconds later the dash screen will appear, congratulations you've run my program. 

Should I have implemented a less fiddly system? Yes. 

Am I going to? No, this project has already taken up way too long for something which only exists to prove I can make the thing I'm writing about in my report. 

Appologies for these instructions being so conversational, this is a last minute inclusion. 

Have a great day.
