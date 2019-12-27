# MusicBeeStats
MusicBeeStats tracks your play counts and other stats over time. To update it every day add it to your startup sequence by adding a `.bat` file with the following command:
```
python main.py FILE_PATH_TO_XML_LIBRARY_FILE [-saveOnly]
```  
The `FILE_PATH_TO_XML_LIBRARY_FILE` is the path to MusicBee's exported iTunes formatted XML file. You can enable MusicBee to export your libary as an XML file and update it everytime it closes under `Preferences > Library > export the library as an iTunes formatted XML file`.  
The `-saveOnly` argument tells MusicBeeStats whether to just save the stats and only show your statistics on the first day of each month for monthly stats and the first day of the year for the yearly stats or show some plots about your current stats (omit `-saveOnly` for the second option). 

MusicBeeStats will save your stats once a day (assuming you boot your pc at least once a day). 

## Requirements
Requires Python 3.7 to run.