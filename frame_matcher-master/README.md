# Frame Matcher
A probabilistic entity resolution module to link unclassified government units to existing frames developed by Carlos Eduardo Ortega and Shohini Saha with guidance from Keith Finlay, Ph.D. and Liz Willhide.

*Please do not store any data in this repository. All test data has been fabricated by the authors.*

## Dependencies
Frame matcher uses Python 3.6.3 and the following packages:
- Flask [http://flask.pocoo.org/docs/0.12/installation/]
- pandas [https://pandas.pydata.org/]
- numpy [http://www.numpy.org/]
- sqlite3 [https://docs.python.org/3/library/sqlite3.html#module-sqlite3]

## Installation
To install the required dependencies run the following commands in your terminal (commands may differ across operating systems, these were used in Windows 10).

*Note: If you have Anaconda (e.g. Anaconda Navigator / Anaconda Prompt) installed, you should already have all of these dependencies.*
```
$ pip install Flask==0.12.2
$ pip install pandas==0.20.3
$ pip install numpy==1.13.3
$ pip install gensim==3.7.3
```

## How to Start Application
Frame_matcher.py is a local web app that runs in your browser (it has only been tested on Chrome and Firefox). 

To start up the application:
1. Open up a terminal and run the following command
```
$ python3 app.py
```
If you do not have python3 set up in your path replace with the variable you do have set to python or with the path to python. 
```
$ C:\Anaconda\python.exe app.py 
$ python app.py
```
2. In your browser go to [http://localhost:5000/]

## How to Close Application
1. To close down the application, either click the 'End Program' button in the browser or press 'Ctrl+C' in the terminal window the application is running in.

## Public domain

Except where noted, this project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the CC0 1.0 Universal public domain dedication. Except where noted, all contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are affirming that the changes are yours to license and you are agreeing to comply with this waiver of copyright interest, or that the changes are already in the public domain.


