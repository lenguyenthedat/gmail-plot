from imaplib import IMAP4_SSL
from datetime import date,timedelta,datetime
from time import mktime
from email.utils import parsedate
from pylab import figure,hist,date2num,num2date,show,xticks,
from matplotlib.dates import DateFormatter

# C&P from http://stackoverflow.com/questions/3463930/how-to-round-the-minute-of-a-datetime-object-python/10854034#10854034
def roundTime(dt=None, roundTo=60):
    """Round a datetime object to any time laps in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt == None : dt = datetime.datetime.now()
    seconds = (dt - dt.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0,rounding-seconds,-dt.microsecond)

# The below script was based on http://glowingpython.blogspot.sg/2012/05/analyzing-your-gmail-with-matplotlib.html
def getHeaders(address,password,folder,d):
    """ retrieve the headers of the emails 
     from d days ago until now """
    # imap connection
    mail = IMAP4_SSL('imap.gmail.com')
    mail.login(address,password)
    mail.select(folder) 
    # retrieving the uids
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, data = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))
    # retrieving the headers
    result, data = mail.uid('fetch', data[0].replace(' ',','), 
                         '(BODY[HEADER.FIELDS (DATE)])')
    mail.close()
    mail.logout()
    return data

def hourlyTimeSeries(headers):
    hours = []
    for h in headers: 
        if len(h) > 1:
            timestamp = mktime(parsedate(h[1][5:].replace('.',':')))
            mailstamp = datetime.fromtimestamp(timestamp)
            # Time the email is arrived
            # Note that years, month and day are not important here.
            y = roundTime(datetime(2014,10,11,mailstamp.hour, mailstamp.minute, mailstamp.second),roundTo=60*60)
            hours.append(y)

    """ draw the histogram of the daily distribution """
    # converting dates to numbers
    numtime = [date2num(t) for t in hours] 
    # plotting the histogram
    ax = figure(figsize=(18, 6), dpi=80).gca()
    _, _, patches = hist(numtime, bins=24,alpha=0.5)
    # adding the labels for the x axis
    tks = [num2date(p.get_x()) for p in patches] 
    xticks(tks,rotation=30)
    # formatting the dates on the x axis
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.autoscale(tight=False)
        
def monthlyTimeSeries(headers):
    months = []
    for h in headers: 
        if len(h) > 1:
            timestamp = mktime(parsedate(h[1][5:].replace('.',':')))
            mailstamp = datetime.fromtimestamp(timestamp)
            # Time the email is arrived
            y = datetime(mailstamp.year,mailstamp.month,mailstamp.day, mailstamp.hour, mailstamp.minute, mailstamp.second)
            months.append(y)

    """ draw the histogram of the daily distribution """
    # converting dates to numbers
    numtime = [date2num(t) for t in months] 
    # plotting the histogram
    ax = figure(figsize=(18, 6), dpi=80).gca()
    _, _, patches = hist(numtime, bins=30,alpha=0.5)
    # adding the labels for the x axis
    tks = [num2date(p.get_x()) for p in patches] 
    xticks(tks,rotation=30)
    # formatting the dates on the x axis
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.autoscale(tight=False) 

# Main
print 'Fetching emails...'

#TODO: Config file.
headers = getHeaders('your.email@gmail.com','your.password','[Gmail]/Sent Mail',365*3)

print 'Plotting...'
hourlyTimeSeries(headers)
monthlyTimeSeries(headers)

show()
