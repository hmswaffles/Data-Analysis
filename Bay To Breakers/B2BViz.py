
#### Bay To Breakers Script ###

#SOME bay to breakers analysis

#first: Raw graphs - men and women
#second: distribution of record times for 2014 race - men and women
#correcting for course changes and shortening- can this be detected by mcmc methods?
from __future__ import division
import prettyplotlib as ppl
import numpy as np
import time

# prettyplotlib imports
import matplotlib.pyplot as plt
import matplotlib as mpl
from prettyplotlib import brewer2mpl

# Set the random seed for consistency 
np.random.seed(12)

fig, ax = plt.subplots(1)










#getting data#
def data_loader():
    import csv
    d = open("C:\Users\Evan\Desktop\B2BTimes.csv",'r')
    dd = csv.reader(d)
    mdata = []
    fdata = []
    for row in dd:
        mdata.append(row[0:3])
        if row[4]:
            fdata.append([row[0],row[3],row[5]])
    ##convert times to seconds##
    return mdata,fdata



def convert_times(d):
    ###converts times to seconds
    records = []

    for row in d:
        t = row[2]
        if len(t) <5:
            print "Hello"
        else:
            if t[0] == '1':
                (h,m,s)=t.split(':')
                seconds = int(h)*3600+int(m)*60+int(s)
            elif t[5] == ':':
                (m,s,ts)=t.split(':')
                seconds = int(m)*60+int(s)
            elif t[5] == '.':
                (m,s)=t.split(':')
                seconds = int(m)*60+float(s)
            else:
                print t
            records.append(seconds)
    return records

def convert_dates(d):
    dates = []
    #print len(d)
    P=len(d)-14
    for i in range(len(d)):
       # print i
        
        row = d[i]
        date = row[0]
        year = date[-2:]
        #print year
        if i >P-2:
            full_year = '20'+year
        else:
            full_year = '19'+year
        dates.append(full_year)
    return dates

def correct_times(gender,d):
    speedls = []
    if gender=='m':
        for i in range(len(d)):
            if i<71:
                speed = float(d[i])/7.51
            else:
                speed = float(d[i])/7.46
            speedls.append(speed)
    elif gender == 'w':
        for i in range(len(d)):
            if i<15:
                 speed = float(d[i])/7.51
            else:
                speed = float(d[i])/7.46
            speedls.append(speed)
            
    return speedls
            
            

def make_plots(d,correct):
    men = d[0]
    women = d[1]
    if correct:
        
        ay = convert_times(men)
        Ym = correct_times('m',ay)
        Xm = convert_dates(men)
        print "hola"
        print len(Xm)
        print len(Ym)
        ppl.scatter(ax,Xm,Ym,label="Men's speeds")

        aw = convert_times(women)
        Yw = correct_times('w',aw)
        Xw = convert_dates(women)

        ppl.scatter(ax,Xw,Yw,label="Women's speeds")

        ppl.legend(ax)
        ax.set_title("Bay To Breakers Speeds (Seconds per Mile)")
        fig.savefig("b2bwinningtimescorrected.png")

        

    else:
        Ym = convert_times(men)
        Xm = convert_dates(men)
        ppl.scatter(ax,Xm,Ym,label="Men's Times")

        Yw = convert_times(women)
        Xw = convert_dates(women)
        ppl.scatter(ax,Xw,Yw,label="Women's Times")

        ppl.legend(ax)
        ax.set_title("Bay To Breakers times (seconds)")
        fig.savefig("b2bwinningtimes.png")

    #fig.show()


   
        

        




        
        
            
###First, Raw Graph###
def scatter_plot(x,y,title,save,l):
        ppl.scatter(ax,x,y)
        ax.set_title(title)
        ppl.show()
        if save:
            ax.set
            fig.savefig(l)
        




