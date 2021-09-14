import urllib.request, urllib.parse, urllib.error
import re
from bs4 import BeautifulSoup
import requests
import time


def get_formvals(cgurl):
    """
    This function pulls all possible month and year values for the web form which is used to pull the data

    :param cgurl:
    :return:
    """

    fhand = urllib.request.urlopen(cgurl)
    html = fhand.read().decode()
    soup = BeautifulSoup(html, "html.parser")

    for o in soup("select")[0].find_all("option"):
        try:
            if int(o.get("value")) != "":
                months.append(o.get("value"))
        except:
            continue
    for o in soup("select")[1].find_all("option"):
        try:
            if int(o.get("value")) != "":
                years.append(o.get("value"))
        except:
            continue


def set_keys(cgurl):
    """
    The NPS website uses a firewall to secure the html form we will be using
    each time the page is loaded, an as_sfid and as_fid key is generated
    this code saves those keys to the params dictionary so our requests will work

    :param cgurl:
    :return:
    """

    fhand = urllib.request.urlopen(cgurl)
    html = fhand.read().decode()
    keys = re.findall('as_\S+.value="(\S+)"', html)
    params["as_sfid"] = keys[0]
    params["as_fid"] = keys[1]


def get_dates(cgurl, cgparams):
    """
    This function sends a POST request to the webpage which submits the HTML form
    once submitted the form populates the webpage with the relevant fill times for the campground
    this function then returns a list of each square in the webpages calendar
    from these squares (one for each calender date), we can get the fill times
    and the dates

    the post request takes as arguments the url and parameters that will be passed
    the paramters include the as_sfid key, as_fid key, month, and year

    :param cgurl:
    :param cgparams:
    :return:
    """

    postreq = requests.post(cgurl, cgparams)
    rescon = postreq.text

    resconsoup = BeautifulSoup(rescon, "html.parser")
    dates = BeautifulSoup(rescon, "html.parser")("table")[2](
        "font", {"size": "1", "face": "Arial, Helvetica, sans-serif"}
    )
    return dates


if __name__ == "__main__":

    params = {"selectmm": "", "selectyy": "", "SubmitForm": "Display+fill+times", "as_sfid": "", "as_fid": ""}

    campdata = dict()
    campdata["dates"] = []
    campdata["times"] = []
    campdata["days"] = []
    campdata["months"] = []
    campdata["years"] = []

    dayslist = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    months = []
    years = []
    dates = []
    url = "https://www.nps.gov/applications/glac/cgstatus/camping_detail.cfm?cg=Apgar"
    get_formvals(url)

    y = 0
    while y < 2:
        m = 0
        for month in months:
            params["selectmm"] = months[m]
            params["selectyy"] = years[y]

            t = 0
            while t < 3:
                time.sleep(1)
                t = t + 1
                try:
                    set_keys(url)
                    dates = get_dates(url, params)
                    print("Completed load on try", t, "for:", y, m)  # only runs if previous line worked
                    break
                except:
                    print("Error. Retrying...", t, "of 3")
                    continue

            d = 7
            for date in dates:
                campdata["dates"].append(date.findAll(text=True)[0])  # add dates to dataset (1,2,3,4,etc)
                try:
                    campdata["times"].append(date.find("font", {"color": "FF0000"}).text.strip())  # add camp fill time
                except:
                    campdata["times"].append("\xa0")  # if campground didn't fill up that day, add blank to dataset
                campdata["days"].append(dayslist[d % 7])
                campdata["months"].append(params["selectmm"])
                campdata["years"].append(params["selectyy"])
                d = d + 1
            m = m + 1
        y = y + 1

    x = 0
    for i in campdata["dates"]:
        print(
            campdata["dates"][x], campdata["times"][x], campdata["days"][x], campdata["months"][x], campdata["years"][x]
        )
        x = x + 1
