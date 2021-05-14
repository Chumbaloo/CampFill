import urllib.request, urllib.parse, urllib.error
import re
from bs4 import BeautifulSoup
import requests
import time

######################################
#############Functions################
######################################
def get_formvals(cgurl):
#This function pulls all possible month and year values for the web form
#which is used to pull the data
    fhand = urllib.request.urlopen(cgurl) #connect to webpage for campground
    html = fhand.read().decode() #read html from webpage and store as string in html variable
    soup = BeautifulSoup(html,'html.parser') #use BeautifulSoup package to parse the html string into object called soup

    #loop through soup object and indentify all form options on webpage
    for o in soup('select')[0].find_all('option'): #get possible month values
        try:
            if int(o.get('value')) != '': #ignore blank form option values
                months.append(o.get('value'))
        except:
            continue
    for o in soup('select')[1].find_all('option'): #get possible year values
        try:
            if int(o.get('value')) != '': #ignore blank form option values
                years.append(o.get('value'))
        except:
            continue

def set_keys(cgurl):
#the NPS website uses a firewall to secure the html form we will be using
#each time the page is loaded, an as_sfid and as_fid key is generated
#this code saves those keys to the params dictionary so our requests will work
    fhand = urllib.request.urlopen(cgurl) #connect to webpage for campground
    html = fhand.read().decode() #read html from webpage and store as string in html variable
    keys = re.findall('as_\S+.value="(\S+)"',html) #use regular expression to find keys in HTML
    params['as_sfid'] = keys[0]
    params['as_fid'] = keys[1]

def get_dates(cgurl, cgparams):
#This function sends a POST request to the webpage which submits the HTML form
#once submitted the form populates the webpage with the relevant fill times for the campground
#this function then returns a list of each square in the webpages calendar
#from these squares (one for each calender date), we can get the fill times
#and the dates

    #the post request takes as arguments the url and parameters that will be passed
    #the paramters include the as_sfid key, as_fid key, month, and year
    postreq = requests.post(cgurl,cgparams) #send POST request
    rescon = postreq.text #get the text from the POST request response as a string

    #use BeautifulSoup package to parse the html string into object called resconsoup
    resconsoup = BeautifulSoup(rescon,'html.parser')

    #using BeautifulSoup, find all of the squares from the webpage's calendar graphic
    #the calendar is the third table on the webpage and all of the squares are formatted with the
    #font size as 1 and Arial, Helvetica, sans-serif
    dates = BeautifulSoup(rescon,'html.parser')('table')[2]('font', {"size" : "1", "face" : "Arial, Helvetica, sans-serif"})
    return dates #return a list with all the squares from the calender

###########################################
##############Set Parameters###############
###########################################

#Used for html form submittal
params = {'selectmm' : ''
        , 'selectyy' : ''
        , 'SubmitForm' : 'Display+fill+times'
        , 'as_sfid': ''
        , 'as_fid': ''}

campdata = dict() #holds fill time data
campdata['dates'] = []
campdata['times'] = []
campdata['days'] = []
campdata['months'] = []
campdata['years'] = []

#List of days of week
dayslist = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

#used for indexing when looping through to submit the form for every possible year and month combination
#these get populated by the get_formvals function
months=[]
years=[]

#will hold, in a list, the squares in the calender with the fill times populated.
dates =[]

############################################
#Get the possible form values from the html#
############################################
url = 'https://www.nps.gov/applications/glac/cgstatus/camping_detail.cfm?cg=Apgar'
get_formvals(url) #pull all possible form values

############################################
####Send post request and get fill times####
############################################
y=4 #used for indexing year
while y<5: #loop through every possible year (only doing first two for testing)
    m=0 #used for indexing month
    for month in months: #loop through every possible month
        params['selectmm'] = months[m] #set month parameter for form request
        params['selectyy'] = years[y] #set year parameter for form request

        #sometimes the POST request for the form will fail. This logic will try
        #three times before giving up
        t=0
        while t<3:
            time.sleep(1) #wait 1 second between each attempt (be polite)
            t=t+1
            try:
                set_keys(url) #set firewall keys
                dates = get_dates(url, params) #send POST request and get calender squares, may fail
                print('Completed load on try',t,'for:',y,m) #only runs if previous line worked
                break #exit loop after success
            except:
                print('Error. Retrying...',t,'of 3')
                continue

        #This code populates the campdata dictionary with data we want from the webpage
        d = 7 #logic for day of week
        for date in dates: #loop through the calender squares
            campdata['dates'].append(date.findAll(text=True)[0]) #add dates to dataset (1,2,3,4,etc)
            try:
                campdata['times'].append(date.find('font', {"color" : "FF0000"}).text.strip()) #add camp fill time
            except:
                campdata['times'].append('\xa0') #if campground didn't fill up that day, add blank to dataset
            campdata['days'].append(dayslist[d%7]) #add day of week to dataset (Sunday, Monday, etc)
            campdata['months'].append(params['selectmm']) #add month to dataset
            campdata['years'].append(params['selectyy']) #add year to dataset
            d=d+1 #logic for day of week
        m=m+1 #used for indexing the months
    y=y+1 #used for indexing the years

############################################
###############Send data to SQL#############
############################################

#First, we need to clean up the data

#build a list with all the indexes we want to delete (date is empty)
index_deletions = []
for record in enumerate(campdata['dates']):
    if record[1] == '\xa0':
        index_deletions.append(int(record[0]))

#start from highest index first so indexes don't change as we delete from list
index_deletions.reverse()

for deletion in index_deletions:
    del campdata['dates'][deletion]
    del campdata['days'][deletion]
    del campdata['times'][deletion]
    del campdata['months'][deletion]
    del campdata['years'][deletion]

x = 0
for i in campdata['dates']:
    print(campdata['dates'][x],campdata['times'][x],campdata['days'][x],campdata['months'][x],campdata['years'][x])
    x = x+1
