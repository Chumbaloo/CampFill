import urllib.request, urllib.parse, urllib.error
import re
from bs4 import BeautifulSoup
import requests
import time

######################################
#############Functions################
######################################
def get_formvals(cgurl):
    fhand = urllib.request.urlopen(cgurl)
    html = fhand.read().decode()
    soup = BeautifulSoup(html,'html.parser')

    #Parse HTML and indentify all form options
    for o in soup('select')[0].find_all('option'):
        try:
            if int(o.get('value')) != '':
                months.append(o.get('value'))
        except:
            continue
    for o in soup('select')[1].find_all('option'):
        try:
            if int(o.get('value')) != '':
                years.append(o.get('value'))
        except:
            continue

def set_keys(cgurl):
    fhand = urllib.request.urlopen(cgurl)
    html = fhand.read().decode()
    keys = re.findall('as_\S+.value="(\S+)"',html)
    params['as_sfid'] = keys[0]
    params['as_fid'] = keys[1]

def get_dates(cgurl, cgparams):
    postreq = requests.post(cgurl,cgparams)
    rescon = postreq.text
    resconsoup = BeautifulSoup(rescon,'html.parser')
    dates = BeautifulSoup(rescon,'html.parser')('table')[2]('font', {"size" : "1", "face" : "Arial, Helvetica, sans-serif"})
    return dates

###########################################
##############Set Parameters###############
###########################################
params = {'selectmm' : ''
        , 'selectyy' : ''
        , 'SubmitForm' : 'Display+fill+times'
        , 'as_sfid': ''
        , 'as_fid': ''}
campdata = dict()
campdata['dates'] = []
campdata['times'] = []
campdata['days'] = []
campdata['months'] = []
campdata['years'] = []
dayslist = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
months=[]
years=[]
dates =[]

############################################
#Get the possible form values from the html#
############################################
url = 'https://www.nps.gov/applications/glac/cgstatus/camping_detail.cfm?cg=Apgar'
get_formvals(url)

############################################
####Send post request and get fill times####
############################################
y=0
while y<2:
    m=0
    for month in months:
        params['selectmm'] = months[m]
        params['selectyy'] = years[y]
        t=0
        while t<3:
            time.sleep(1)
            t=t+1
            try:
                set_keys(url)
                dates = get_dates(url, params)
                print('Completed load on try',t,'for:',y,m)
                break
            except:
                print('Error. Retrying...',t,'of 3')
                continue
        d = 7
        for date in dates:
            campdata['dates'].append(date.findAll(text=True)[0])
            try:
                campdata['times'].append(date.find('font', {"color" : "FF0000"}).text.strip())
            except:
                campdata['times'].append('\xa0')
            campdata['days'].append(dayslist[d%7])
            campdata['months'].append(params['selectmm'])
            campdata['years'].append(params['selectyy'])
            d=d+1
        m=m+1
    y=y+1

x = 0
for i in campdata['dates']:
    print(campdata['dates'][x],campdata['times'][x],campdata['days'][x],campdata['months'][x],campdata['years'][x])
    x = x+1

############################################
###############Send data to SQL#############
############################################
