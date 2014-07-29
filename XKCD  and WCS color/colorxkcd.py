#WELCOME TO THE WIDE WEIRD WORLD OF COLOR



#super concise summary: The code below can 'average' colors together in a way that would make sense to a painter, and interact with the data from both the XKCD
#color survey, as well as academic research on color

#Less concise summary: This code contains the tools necessary to a) investigate the xkcd color database, b) transform rgb values to perceptually even colorspaces,
# c) Plot colors in perceptually even 3d colorspace and d) compare with the results of the World Color Survey.
#For instance, If you are curious about what all of the 'happy' colors (aka 'happy blue', 'happy green', look like, what their perceptual center is,
#as well as how this relates to the munsell standard color reference) you are in the right place.


#there are also routines for converting RGB to CIELab and CIELove space, with various types of illuminants, primaries, and chromatic adaptations- the 
#RGB to XYZ coefficents are calculated in-house.
#Additionally, there are tools for (some) linguistic analysis of the color terms
#Towards the bottom, there is a routine for looking into the non-uniformity of the WCS stimulus, specifically looking at chromatic pop-out



#thanks to the good folks at Enthought and the authors of the Mayavi package, Brent Berlin, Paul Kay, Randall Munroe, all those involved in the WCS or the XKCD color survey
#and Terry Regier and the fine folks at the U.C. Berkeley Language and Cognition Lab. Especially Emily Cibelli.

# Questions? email evanw@evanwarfel.com 

# if you do use this in something publication worthy, please cite me. 

#This code is for academic/research purposes only, unless you contact me first.

#----------------------------------------------------------------------------

#

#A note on illuminants:
#Berlin and Kay, 1969 used illuminant A
#the WCS used the shady outdoors, which  d65 attemps to capture
#however, the LAB values for the munsell chips in the WCS were calculated with the C illuminant.
#note that all colorings of the 3d chips are only approximations.

#########################################################
#side note: the modal search is currently a bit buggy, and the chromatic adaptation/conversion between xyz/lab is not quite right

#General Housekeeping

from __future__ import division 
import sys
import csv
import colorsys
import sqlite3
import matplotlib.pyplot as plt    
import numpy as np
#import scipy as sp [package isn't actually used in this iteration#
from numpy import *
from scipy import stats
from collections import Counter
from numpy import matrix
from numpy import linalg
from mayavi import mlab



#Database Housekeeping
#Assuming that the XKCD database is the working directory, as colordata.db

conn = sqlite3.connect ('colordata.db')
c = conn.cursor()
conn.text_factory = str




#Data scrubbing Housekeeping
# a small routine to delete the achromatic chips from the WCS Munsell coordinates

def isnotcollumn0(n):                   #looks to see if the chip is achromatic
        if n[1] is not '0':             #by seeing if it is in column '0'
                return True
        else:                           
                return False



#Data Importing housekeeping
mchipsall=[]
mchips=[]
f = open('C:\Python27\MUNSELLCHIPS.csv')  #This data can be found at http://www1.icsi.berkeley.edu/wcs/
reader = csv.reader(f)
mc =mchipsall.append
for row in reader:                          #reads the munsell chips (row, column and lab coordinates) into a list
        mc(row)
del mchipsall[0]                            #removes the L* A* B* collumn headings
mmchips = filter(isnotcollumn0,mchipsall)  #filters out the achromatic chips. new list is called mmchips.




##Illuminant and Primary housekeeping

def illuminantlookup(W):
        #The illuminant is the rerference whitepoint
        #d65 is considered standard daylight, A approximates an incandescent lightbulb
        if W == 'd50':
                return ((96.422,100,82.521),(0.34567,0.35850)) #using values from :http://home.tiscali.nl/t876506/ColorDesign.html#coef
        elif W == 'd65':                                       #also found at http://en.wikipedia.org/wiki/Standard_illuminant
                return ((95.047,100,108.883),(0.31271,0.32902))#and http://www.easyrgb.com/index.php?X=MATH&H=15#text15
        elif W == 'd75':
                return ((94.972,100,122.638),(0.29902,0.31485))
        elif W == 'f2':
                return ((99.187,100,67.395),(0.37208,0.37529))
        elif W == 'A_ill':
                return ((109.850,100,35.585), (0.45117,0.40594))
        elif W == 'C':
                return ((98.074,100,118.232),(0.31006, 0.31616))
        else:
                return False

        
def rgbprimarylookup(rgbprimary_name):
        #values for grounding what 'red','green', and 'blue are
        if rgbprimary_name == 'Adobe':
                rgbprimaries= [(0.64,0.33),(0.21,0.71),(0.15,0.06)]
        elif rgbprimary_name == 'CIE':
                rgbprimaries= [(0.735,0.265),(0.274,0.717),(0.167, 0.009)]
        elif rgbprimary_name == 'sRGB':
                rgbprimaries= [(0.64,0.33),(0.30,0.60),(0.15,0.06)]               #also the same for hdtv
        elif rgbprimary_name == 'lcd':
                rgbprimaries= [(0.66,0.33),(0.28,0.60),(0.14,.06)]                # from http://www.creol.ucf.edu/research/Publications/2216.pdf
        return rgbprimaries




#Notes on the actual program

#The following routine is for extracting, analyzing and plotting the data which correspond to different colornames.
#To use the program, give it 
#       1) a list of tuples of strings - e.g. listofcolors = [('super blue',),('super dark blue',),('bad blue',),('awful blue',),('bad green',),('awful green',),]
#       2) The illuminant you want to use as a string - e.g. 'd65' or 'C'
#       3) the rgb primary used for converting the xkcd colors to lab space. This can be 'lcd','CIE','Adobe', or 'sRGB'
#       4) either 'mean', 'mode', or '3d' (central tendency options), depending on what you want to do
#
#
#
# Details:
#CENTRAL TENDENCY MEASURES OPTIONS: 
#   A) 'mean', which returns the total number entries for each color term along with it's average and std deviation in both LAB and RGB coordinates
#   B) 'mode', which snaps each color that was named to the nearest munsell chip and then counts said chips. This looks at the modal chips, because very rarely do the exact color coordinates overlap
#   C) '3d' plots the named color coordinates against the munsell chips in 3d cielab space- see above for toggle options
    
# There are more, optional parameters in addition to the 4 above. They are as follows: 
    #Flag:        if set to True, the nearest chip searcher uses actual euclidean distance, rather than d^2. This is a speed shortcut.
    
    #Labeling:    if set to True, the focal colors will be labeled when graphed in 3d
    
    #Concat:      if set to True, multiple sql querys, aka. multiple color labels, will be plotted against the munsell chips if '3d' is also specified.
    #                 if 'mean' is specified and concat is set to true then all the color labels will be treated as one color for analysis, instead of many
    
    #Lab:        if set to True, the 'mean' subroutine will return the mean of the lab coordiantes of all the colors, instead of converting them back to RGB
    
    #Screentype: selects which answers to select from the database based on what users reported thier screentype was. Can be 'lcd', etc. 
    #jmunchips:  if set to True, just the munsell chips will be plotted in 3d, w or w/o labeling. '3d' should still be specified
    #meancoerce: if set to True, all entries per color name will be (perceptually averaged), then snaped  to the nearst munsell chip
    #adaptype:   type of chromatic adaptation. can be 'brad' for bradford, or 'von kries'

#Important- if the list colors contains more than 1 entry while graphing in 3d, concat should be set to true, else only the munsell chips will be plotted




# meet munster, aka mr. munsell

def munster(listofcolors,illuminant,rgbprimary_name,centraltendencymeasure,
            flag=False,labeling=False,concat=False,lab=True,Screentype='LCD',jmunchips=False,meancoerce=False,adaptype='brad'):  

    if jmunchips==False and concat==False:
            mflag = False
    else:
            mflag = True
    #if more than one color is entered, with the '3d' option,
    #mayavi will just graph the munsell chips, unless you want to see all of the points concatenated together
    
    ls = [] 
    illum = illuminantlookup(illuminant)         # returns a pair- the lab illuminant is [0], the xyz coordinates are [1]
   #the following returns the rgb primaries:
    rgbprimaries=rgbprimarylookup(rgbprimary_name)
    coefficentmatrix = getrgbxyz_coefficents(illum[1],rgbprimaries)    #sets up the RGB to XYZ matrix at the begining, so it isn't calculated for every conversion.
    mchips = [[[],[],[],[],[],[]] for x in xrange(320) ]
    
    #converting the munsell chips to lab space with chromatic adaptation so that they can be compared to the xkcd colors'
    
    #(for munsell chips only, the conversion goes: Lab->xyz, xyz->chromaticadapt->xyz, xyz->Lab)
    for i in range(len(mmchips)):
           # print chip
            a = altLabXyzConvert(illum[1],float(mmchips[i][3]),float(mmchips[i][4]),float(mmchips[i][5]))
            b = chromaticadapt(a,illuminantlookup('C')[0],illuminantlookup(illuminant)[0],adaptype)
            q1 = (b[0]-a[0])
            q2 = (b[1]-a[1])
            q3 = (b[2]-a[2])
            if abs(q1)>.5:
                    print q1
            elif abs(q2)>.5:
                    print q2
            elif abs(q3)>.5:
                    print q3
            dd = munlabconvert(illum[0],([b[0]],[b[1]],[b[2]]))

            mchips[i][0]=mmchips[i][0]
            mchips[i][1]=mmchips[i][1]
            mchips[i][2]=mmchips[i][2]
            mchips[i][3]=round(dd[0],5)
            mchips[i][4]=round(dd[1],5)
            mchips[i][5]=round(dd[2],5)

  #
  #
  #
  #
  #Now starts the bulk of the program.
  #
  #
  #
  #
  #
    print listofcolors
    if centraltendencymeasure == 'mean': #this will 'average' as many colors as you want
        flag = True
        a = Mean_calc(illum[0],listofcolors,ls,coefficentmatrix,concat,lab,
                  Screentype,meancoerce) #converts to LAB, runs calculations
      #  print a
       # print 'ak!'
        if meancoerce == True:
                print a[7]
                print quick_mode_mun_search((a[7],a[8],a[9]),mchips,flag)
    elif centraltendencymeasure == 'mode':
        for color in listofcolors:
            Modal_mun_search(color,illum[0],coefficentmatrix,mchips,flag,Screentype)
            
            #the conversions and things are done here 
  
  
    #that was most of it, the rest is an in-routine 3d graphing bit 
    elif centraltendencymeasure == '3d':       
        a = len(listofcolors)
                #formulate munsell chips to be used in 3d.
                #need all of the L* data from the munsell chips to be in i.
        i=[]
        j=[]
        k=[]
        ii=[]
        jj=[]
        kk=[] #keeping the color like the 'c' illuminant
        print 'setting up the munsell chips...'
        for chip in mchips:
            i.append(float(chip[3]))
            j.append(float(chip[4]))
            k.append(float(chip[5]))
        print 'coloring them'
        #convert mchips to rgb
        mchipscolor =[]
        Imatrix = coefficentmatrix.I #(inverted)
       
        for chip in mmchips:
                ii.append(float(chip[3]))
                jj.append(float(chip[4]))
                kk.append(float(chip[5]))
        print ii[0:5]
        for p in range(320): #Purely for coloring the chips!
                tt = (altLabXyzConvert(illum[1],ii[p],jj[p],kk[p])) 
                uu = xyzrgbconvert(tt,Imatrix)  
                r = uu[0]
                g = uu[1]
                b = uu[2]
                if r>1: #takes care of impossible colors outside of the rgb gamut
                        R = 1
                        print 'rounded'
                elif r<0:
                        R = 0
                        print 'rounded'
                else:
                        R = r
                if g>1: 
                        G = 1
                        print 'rounded'
                elif g<0:
                        G = 0
                        print 'rounded'
                else:
                        G = g
                if b>1: 
                        B = 1
                        print 'rounded'
                elif b<0:
                        B = 0
                        print 'rounded'
                else:
                        B = b
                        
                w = (R,G,B)
                mchipscolor.append(w) #mchipscolor is now the list of rgb triplets associated with each point
                
                
        d=[]
        for u in range(a):
                    q=[]
                    qq=[]
                    x=[]#for 3d plotting
                    y=[]
                    z=[]
                    #some null lists. (I should find a cleaner way to do this)
                    print 'fetching from database'
                    print listofcolors[u]
                    #print Screentype
                    c.execute("Select answers.r, answers.g, answers.b from answers inner join users on answers.user_id = users.id where colorname=? and monitor =?",
                              (listofcolors[u][0],Screentype,))
                    d.extend(c.fetchall())    
        ixyzconvert(d,q,coefficentmatrix)
        imun_convert(q,qq,illum[0]) #converts to LAB for a specific illuminant
        e = len(qq) 
        for u in xrange (e):
                        x.append(qq[u][0])
                        y.append(qq[u][1])
                        z.append(qq[u][2])
        X=np.array(x)
        Y=np.array(y)
        Z=np.array(z)
        I=np.array(i)
        J=np.array(j)
        K=np.array(k)
        print "about to plot..."
        if jmunchips :
            if labeling == True:
                for i in range(len(mchipscolor)):
                        if i == 48: #labels the focal chips- from WCS (Yellow)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'C9')
                                
                        elif i == 176:#WCS,XKCD (green)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'F17',color=(1,0,1))
                                
                        elif i == 188:#WCS (blue)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'F29')
                                
                        elif i == 200:#WCS (red)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'G1')
                                                                          
                        else:
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
            elif labeling == False:
                for i in range(len(mchipscolor)):
                                         a = mlab.points3d(I[i],J[i],K[i],
                                                           color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                mlab.draw()
                mlab.show()

        elif jmunchips == False:
                if labeling == True:
                    #this is a basic filter for taking a representitive (?) sample of the xkcd colors
                    if e < 2000:
                                s = mlab.points3d(X, Y, Z,
                                                  colormap="hsv",scale_factor=2) #plots normally
                    elif 1999 < e < 10001:
                                s = mlab.points3d(X, Y, Z,
                                                      colormap="hsv", mask_points=5, scale_factor=2) #plots 1 out of every 5 points
                    elif e > 10000:
                                s = mlab.points3d(X, Y, Z,
                                                      colormap="hsv", mask_points=50, scale_factor=2) #plots 1 out of every 50 points
                    elif e> 200000:
                                s = mlab.points3d(X, Y, Z,
                                                      colormap="hsv", mask_points=65, scale_factor=2) # 1/65.
                    mlab.draw()
                   
                                
                    print 'points plotted, next are the munsell chips'
                    
                    for i in range(len(mchipscolor)):
                        if i == 48: #labels the focal chips- from WCS (Yellow)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'C9')
                                
                        elif i == 176:#WCS,XKCD (green)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'F17',color=(1,0,1))
                                
                        elif i == 188:#WCS (blue)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'F29')
                                
                        elif i == 200:#WCS (red)
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                                b = mlab.text3d(I[i],J[i],K[i],'G1')
                                
                   
                        else:
                                a = mlab.points3d(I[i],J[i],K[i],
                                                  color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                    mlab.show()
                elif labeling == False:
                     if e < 2000:
                                s = mlab.points3d(X, Y, Z,
                                                  colormap="hsv",scale_factor=1) #plots normally
                     elif 1999 < e < 10001 :
                                s = mlab.points3d(X, Y, Z,
                                                      colormap="hsv", mask_points=5, scale_factor=1) #plots 1 out of every 5 points
                     elif e > 10000:
                                s = mlab.points3d(X, Y, Z,
                                                      colormap="hsv", mask_points=50, scale_factor=1) #plots 1 out of every 50 points
                     elif e> 200000:
                                s = mlab.points3d(X, Y, Z,
                                                      colormap="hsv", mask_points=65, scale_factor=1) # 1/65.
                     print 'points plotted, next are the munsell chips'
                     for i in range(len(mchipscolor)):
                                     a = mlab.points3d(I[i],J[i],K[i],
                                                       color =(mchipscolor[i]),mode='cube',scale_factor=2,scale_mode='none')
                     mlab.draw()
                     mlab.show()
    else: print "I haven't written that measure of central tendancy yet"


# In[ ]:

#Calculates the perceptual average for the colors corresponding to each entry in the list of colors
def Mean_calc(illuminant,listofcolors,lnull,coefficentmatrix,concat,lab,Screentype,meancoerce):
    #converts to LAB with an illuminant of one's choice 
        a = len(listofcolors)
        d = []
        if concat== False:
                for i in range(a):
                    q=[]
                    qq=[]
                    y=[]
                    yy=[]
                    #print listofcolors[i]
                    c.execute("Select answers.r, answers.g, answers.b from answers inner join users on answers.user_id = users.id where colorname=? and monitor =?",
                              (listofcolors[i][0],Screentype,))
                    d = c.fetchall() #executes the promise and actually grabs from database
                    if len(d)==0:
                            print listofcolors[i]
                            print 'not found'
                    else:
                            ixyzconvert(d,q,coefficentmatrix)
                            imun_convert(q,qq,illuminant) #converts to LAB for a specific illuminant
                            z = np.array(qq)       #using the NUMPY package to find std and mean
                            e = z.std(axis=0)
                            f = z.mean(axis = 0)
                            g =  f.tolist()
                            if lab ==False:
                                    h = altLabXyzConvert(illuminant,g[0],g[1],g[2])
                                    print h
                                    j = xyzrgbconvert(h,coefficentmatrix.I) #can't use i because it is the index
                                    k = tuple(j) #could add mean back in after h below, though it should probably be converted back to rgb
                                    rrr = int(ceil(k[0]*255))
                                    ggg = int(ceil(k[1]*255))
                                    bbb = int(ceil(k[2]*255))
                                    #print 'k'
                                    #print k[0],k[1],k[2]
                                    print rrr
                                    lnull = (listofcolors[i],len(d),
                                             'std(L,A,B):',e[0],e[1],e[2],'mean(R,G,B):',rrr,ggg,bbb) #makes a list of the summary results
                                    if meancoerce:
                                            return lnull
                                    else:
                                            print lnull
                            elif lab == True:
                                    lnull = (listofcolors[i],len(d),
                                             'std(L,A,B):',e[0],e[1],e[2],'mean(L,A,B):',g[0],g[1],g[2]) #makes a list of the summary results
                                    if meancoerce:
                                            return lnull
                                    else:
                                            print lnull
                                    
        elif concat==True:
                for i in range(a):
                    q=[]
                    qq=[]
                    y=[]
                    yy=[]
                    c.execute("Select answers.r, answers.g, answers.b from answers inner join users on answers.user_id = users.id where colorname=? and monitor =?",
                              (listofcolors[i][0],Screentype,))
                    d.extend(c.fetchall()) 
                ixyzconvert(d,q,coefficentmatrix)
                imun_convert(q,qq,illuminant) #converts to LAB for a specific illuminant
                z = np.array(qq)       #using the NUMPY package to find std and mean
                e = z.std(axis=0)
                f = z.mean(axis = 0)
                g =  f.tolist()
                if lab == False:
                        h = altLabXyzConvert(illuminant,g[0],g[1],g[2])
                        j = xyzrgbconvert(h,coefficentmatrix.I) #can't use i because it is the index
                        k = tuple(j)
                        rrr = int(ceil(k[0]*255))#rounds up after RGB is stored as a value between 1 and 0
                        ggg = int(ceil(k[1]*255))
                        bbb = int(ceil(k[2]*255))
                        lnull.append((listofcolors[i],len(d),'std(L,A,B):',
                                      e[0],e[1],e[2],'mean(r,g,b):',rrr,ggg,bbb)) #makes a list of the summary results
                        #print lnull
                        return lnull
                elif lab == True:
                        lnull = (listofcolors[i],len(d),'std(L,A,B):',
                                 e[0],e[1],e[2],'mean(L,A,B):',g[0],g[1],g[2]) #makes a list of the summary results
                        #print lnull
                        return lnull
                        
        #the 'distance' returned is the square of the distance


# In[ ]:

#Modal chip routine.
def Modal_mun_search(color,lab_illuminant,coefficentmatrix,mchips,flag,Screentype):
        #the 'loop' for this program is in munster, not here
    w=[]
    x=[]
    y=[]
    z=[]
    cnt= Counter()
    #for color in listofcolors:
    #print Screentype
    print color[0]
    c.execute("""Select answers.r, answers.g, answers.b from answers inner join users on answers.user_id = users.id where colorname=? and monitor =?""",
                              (color[0],Screentype))
    b = c.fetchall()
    #print b
    for i in xrange(len(b)):
            x.append(rgbxyzconvert(b[i],coefficentmatrix))
    for i in xrange(len(x)):
            y.append(munlabconvert(lab_illuminant,x[i]))
   #now everything is in perceptual space. EDIT: more or less. working on Ciecam02
   
    modal_mun_searcher(y,z,1,mchips,flag)
    chipnameselector(z,w)
    for chip in w:
        cnt[chip] +=1 
    print cnt




#Finds nearest munsell chip to the nearestcolor sample                
def quick_mode_mun_search(chip, mchips,flag): 
        ls =[]
        distances =[]
        c1=float(chip[0])
        c2=float(chip[1])
        c3=float(chip[2])
        #narrowing down the search space
        for element in mchips:
                q1=float(element[2])
                q2=float(element[3])
                q3=float(element[4])
                if abs(q1-c1) < 40:             #this finds the nearest chips within a range of 80 on the x axis
                        ls.append(element)        #if neccessary, the L* range could be smaller (if needed for tweaking
                elif abs(q2-c2) < 40:             #this finds the nearest chips within a range of 80 on the y axis
                        ls.append(element)
                elif abs(q3-c3) < 40:             #etc
                        ls.append(element)
        #the next part of the program now searches through the much smaller list and calculates the distance to each one
   
        for mchip in ls:
                q1=float(mchip[3])
                q2=float(mchip[4])
                q3=float(mchip[5])
        #calculates distance here
                d1= (c1 - q1)**2
                d2= (c2 - q2)**2
                d3= (c3 - q3)**2
                d = (d1 + d2 + d3) #don't actually need to take sqrt, this is unecessary
                if flag:
                        e = d**.5
                else:
                        e = d
                t = (e,mchip)
                distances.append(t)
        return min(distances)
                



### Tools for additional analysis- #######################################################################################

def counter(color): #counts the number of words in the colornames that contain the input,but are not equal to the input
        ccc = color[1:-1]#for this to work, the function should be called like counter('%dark blue%')
        import re
        conn.text_factory = str
        c.execute("""Select answers.colorname, answers.r, answers.g,
                  answers.b from answers inner join users on answers.user_id= users.id where colorname like ?
                  and colorname!=?  and monitor =?""", (color,ccc,'LCD'))
        Y = c.fetchall()
        print Y[0:10]
        YY = []
        zz=[]
        result=[]
        yyappend = YY.append
#First, clean out all less than 3 word answers. 
        for answer in Y:
                if len(re.findall(r'\w+', answer[0])) > 2 and len(re.findall('r\w+', answer[0])) < 12:
                        yyappend(answer) 
        zz= [x[0] for x in YY]
        ansLs=sorted(YY)

        for i in range(len(ansLs)):
            if i == 0:
                    continue
            else:
                oans = ansLs[i-1][0]
                nans = ansLs[i][0]

                if oans != nans: 
                    Wcount=len(re.findall(r'\w+', oans))
                    m = munster([(str(oans),)],'d65','lcd','mean',lab=True)
                    l = round(m[7],3)
                    result.append((Wcount,l,oans))
                else:
                        continue
        return result
    
def wordcolorplotter(colorobject):
        x=[]
        y=[]
        xappend = x.append
        yappend = y.append
        for i in range(len(colorobject)):
                xappend(colorobject[i][1])
                yappend(colorobject[i][0])
        import matplotlib.pyplot as plt
        plt.plot(x,y, 'ro')
        plt.show()   



#RGB/XYZ/CIElAB code for Color conversions and related 

#Iluminants- as specified by CIE, found on a hunterlab pdf or two
#EVERYTHING IS AT 2 DEGREES.
#the first triplet is the tristiumulus values for a perfectly diffuse reflector, the next pair are the xy chromaticity coordinates.
   
def rgblabconverter(rgbtriple,illuminant,primary_name,adaptype=False,destwhite=False): #new as of april 2013
        ii = illuminantlookup(illuminant)
        primes = rgbprimarylookup(primary_name)
        coefficentmatrix = getrgbxyzcoefficents(ii[1],primes)
        AA= rgbxyzconvert(rgbtriple,coefficentmatrix)
        if adapt:
                BB=chromaticadapt(rgbtriple,ii[0],illuminantlookup(destwhite)[0],adaptype)
                CC=munlabconvert(BB,illuminantlookup(destwhite)[0])
        else:
                CC=munlabconvert(AA,ii)
        return CC 

def munlabconvert(illuminant,xyzchip):#converts any xyz triplet to lab for any illuminant, specificed by (x,y) coordinates
    #print illuminant
    Xn=illuminant[0]
    Yn=illuminant[1]
    Zn=illuminant[2]
    x=xyzchip[0][0]*100
    y=xyzchip[1][0]*100
    z=xyzchip[2][0]*100
    Ty= y/Yn
    Tx= x/Xn
    Tz= z/Zn
    e = .008856
    k = 903.3
    if Tx> e:
        Ftx = Tx**(1/3)
    else:
        Ftx = (k*Tx+16)/116
    if Ty> e:
        Fty = Ty**(1/3)
    else:
        Fty = (k*Ty+16)/116
        #Fty = (Ty*(1/3))*(29/6)**2 +(4/29)
    if Tz> e:
        Ftz = Tz**(1/3)
    else:
        Ftz = (k*Ty+16)/116
       # Ftz = (Tz*(1/3))*(29/6)**2 +(4/29)
    Lstar= (116*Fty)-16
    Astar=500*(Ftx-Fty)
    Bstar=200*(Fty-Ftz)
    return Lstar,Astar,Bstar            




#If you want CIELove instead...
def loveconverter(illuminant,xyzchip):
	X=xyzchip[0]
	Y=xyzchip[1]
	Z=xyzchip[2]
	Xr=illuminant[0]
	Yr=illuminant[1]
	Zr=illuminant[2]
	yr=Y/Yr
	uprime=(4*X)/(X+15*Y+3*Z)
	vprime=(9*Y)/(X+15*Y+3*Z)
	urprimer= (4*Xr)/(Xr+15*Yr+3*Zr)
	vprimer=(9*Yr)/(Xr+15*Yr+3*Zr)
	e=.008856
	k=903.3
	if yr>e:
	    L=116*((yr**(1/3)-16)
        else:
            L=k*yr
        U=13*L*(uprime-uprimer)
        V=13*L*(vprime-vprimer)
        return L,U,V



#Alternate way to convert xyz and lab spaces...
#http://www.brucelindbloom.com
def altLabXyzConvert(illuminant,l,a,b):
        g = xy_XYZer(illuminant)
        Xr=g[0]*100
        Yr=g[1]*100#look, i didn't name these variables.
        Zr=g[2]*100#blame bruce lindbloom
        #print Xr,Yr,Zr
        #print l,a,b
        e= 216/24389
        k= 24389/27
        Fy=(l+16)/116
        Fx= (a/500)+Fy
        Fz= Fy-(b/200)
        if Fx**3 > e:
                xr=Fx**3
        else:
                xr=((116*Fx)-16)/k
        if l > k*e:
                yr=((l+16)/116)**3
        else:
                yr=l/k
        if Fz**3 >e:
                zr= Fz**3
        else:
                zr=((116*Fz)-16)/k
        x=xr*Xr
        y=yr*Yr
        z=zr*Zr
        return x/100,y/100,z/100              




def ixyzconvert(old,new,matrix): 
        for color in old:
                new.append((rgbxyzconvert(color,matrix)))

#converts one r,g,b triplet to one x,y,z triplet
def rgbxyzconvert(rgbtriplet,matriX):
       #print rgbtriplet
        rr=rgbtriplet[0]/255
        gg=rgbtriplet[1]/255
        bb=rgbtriplet[2]/255
        r=rr**2.2
        g=gg**2.2
        b=bb**2.2
        rgb = np.matrix([[r],[g],[b]])
        #print rgb
        #print matrix
        xyz = matriX*rgb
        a = xyz.tolist()
        b = (a[0]*100,a[1]*100,a[2]*100)
        return a


#converts on xyz triplet to one rgb triplet. assuming this is just the inverse of the function represented above.
def xyzrgbconvert(xyztriplet,matriX):#note that this matrix is the inverted version of the matrix from above
        #how to scale the x,y and z coordinate to be between 0 and 1?
        xx=xyztriplet[0]
        yy=xyztriplet[1]
        zz=xyztriplet[2]
        xyz = np.matrix([[xx],[yy],[zz]])
       # print matrix
       # print xyz
        rgb = matriX.dot(xyz) 
        RGB = rgb.tolist()
       # print RGB
        r = abs(RGB[0][0])**(1/2.2) #approximates gamma? the 1/2.2 root (not sure about the abs() part)
        g = abs(RGB[1][0])**(1/2.2)
        b = abs(RGB[2][0])**(1/2.2)
        return r,g,b
        
def xy_XYZer (xypair): #for any given pair (x,y) of chromaticity values, this computes the triplet (x,y,z)
   # print xypair
    x=xypair[0]
    y=xypair[1]
    Y = 1.0
    X = x*(Y/y)
    Z = (1-x-y)*(Y/y)
    xx=X*1
    yy=Y*1
    zz=Z*1
    return xx,yy,zz 


# In[ ]:

def getrgbxyz_coefficents(illuminantxyz,rgbprimaries): #returns a matrix with the correct coefficents
    #print illuminantxyz
    z = xy_XYZer(illuminantxyz) #calculates for white
    R = xy_XYZer(rgbprimaries[0]) #calculates xyz for xred and yred
    G = xy_XYZer(rgbprimaries[1]) #same for x,y for blue
    B = xy_XYZer(rgbprimaries[2]) #as for green
    #
    Xr = R[0] #gets the right values for the matrix
    Yr = R[1] # See for further details -http://home.tiscali.nl/t876506/ColorDesign.html#coef
    Zr = R[2] #or bruce lindbloom
    #
    Xg = G[0]
    Yg = G[1]
    Zg = G[2]
    #
    Xb = B[0]
    Yb = B[1]
    Zb = B[2]
    # Form the white coordinates
    Xw = z[0]
    Yw = float(z[1])
    Zw = z[2]
    #
    RGBMatrix = np.matrix([[Xr,Xg,Xb],[Yr,Yg,Yb],[Zr,Zg,Zb]])
    Inverted_matrix = RGBMatrix.I #inverts the RGB Matrix
    #now form the whitepoint matrix
    White = matrix([[Xw],[Yw],[Zw]])
    A = Inverted_matrix*White
    A.transpose 
    RGBlist = RGBMatrix.tolist()
    Alist = A.tolist() 
    Ar = Alist[0][0]
    Ag = Alist[1][0]
    Ab = Alist[2][0]
    XrAr =  Ar*RGBlist[0][0]
    XgAg = Ag*RGBlist[0][1]
    XbAb = Ab*RGBlist[0][2]
    YrAr = Ar*RGBlist[1][0]
    YgAg = Ag*RGBlist[1][1]
    YbAb = Ab*RGBlist[1][2] 
    ZrAr = Ar*RGBlist[2][0]
    ZgAg = Ag*RGBlist[2][1]
    ZbAb = Ab*RGBlist[2][2]
    RGBtoXYZ = np.matrix([[XrAr,XgAg,XbAb],[YrAr,YgAg,YbAb],[ZrAr,ZgAg,ZbAb]])
    return RGBtoXYZ


#Chromatic Adaptation
def chromaticadapt(sourcecolor,sourcewhite,destwhite,adaptype): #takes munsell chips under the c illuminant and converts them to the A illuminant for comparison.
        Xs = sourcecolor[0] #however, this is all within XYZ
        Ys = sourcecolor[1]
        Zs = sourcecolor[2]
        Xws = sourcewhite[0]/100
        Yws = sourcewhite[1]/100
        Zws = sourcewhite[2]/100
        Xds = destwhite[0]/100
        Yds = destwhite[1]/100
        Zds = destwhite[2]/100
        swhite = np.matrix([[Xws],[Yws],[Zws]])
        dwhite = np.matrix([[Xds],[Yds],[Zds]])
        colormat=np.matrix([[Xs],[Ys],[Zs]])
        #using the bradford matrix for chromatic adaptation
        if  adaptype == 'brad': #bradford
                br = np.matrix([[0.8951000,  0.2664000, -0.1614000],[-0.7502000,  1.7135000,  0.0367000],[0.0389000, -0.0685000,  1.0296000]])
        elif adaptype =='von kries':
                br = np.matrix([[0.4002400,  0.7076000, -0.0808100],[-0.2263000,  1.1653200,  0.0457000],[0.0000000,  0.0000000,  0.9182200]])
        PBYs = br*swhite
        PBYd = br*dwhite
        S=PBYs.tolist()
        D=PBYd.tolist()
        Pdiv = D[0][0]/S[0][0]
        Bdiv = D[1][0]/S[1][0]
        Ydiv = D[2][0]/S[2][0]
        conetransform = np.matrix([[Pdiv,0,0],[0,Bdiv,0],[0,0,Ydiv]])
        M = br*conetransform*br.I
        destmat= M*colormat
        d = destmat.tolist()
        return d[0][0],d[1][0],d[2][0]#returns new X,Y,Z



#  short routines, more housekeeping. 
def chipnameselector(ls,newls): #adds together the chip letter and number into one item, for the collections function up above
    a=len(ls)
    print a
    for i in range(a):
        newls.append(ls[i][1][0]+ls[i][1][1])

def modal_mun_searcher(oldlist,newlist,j,mchips,flag):
    a=len(oldlist)
    for i in xrange(a):
        newlist.append(quick_mode_mun_search(oldlist[i],mchips,flag))
        

def labconverter(r,g,b,illuminant,primary):
    illum= illuminantlookup(illuminant)
    coefficentmatrix = getrgbxyz_coefficents(illum[1],rgbprimaries)
    a=rgbxyzconvert((r,g,b),coefficentmatrix)
    b=munlabconvert(illum[0],a)
    return b

        
def imun_convert(origlist,newlist,illuminant):
        a = len(origlist)
        for i in xrange(a):
            b = munlabconvert(illuminant,origlist[i])
            newlist.append(b)
            
def ixyz_convert(origlist,newlist,matrix):
        a = len(origlist)
        for i in range(a):
            b = rgbxyzconvert(origlist[i],matrix)
            newlist.append(b)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# That was the bulk of the color code, what follows are some tools for calculating non-uniformity of the World Color Survey Stimulus, which might explain
# the wierd results found with respect to focal yellow in Brazil
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



####some tests for non-uniformity in the WCS stimulus

##greatest chromatic 'pop out':

def chromamaximizer(Chroma_list):
    newls= []
    #need to skip row b and row i for 'center' of 9 average.

    #...may Brian Harvey never see this code...
    g = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38]
    f = [2,3,4,5,6,7]
    ChromaA = Chroma_list
    for i in f:
        for n in g:
                Top = float(ChromaA[i-1][n-1])+float(ChromaA[i-1][n])+float(ChromaA[i-1][n+1])  
                Middle = float(ChromaA[i][n-1])+float(ChromaA[i][n])+float(ChromaA[i][n+1]) 
                Bottom = float(ChromaA[i+1][n-1])+float(ChromaA[i+1][n])+float(ChromaA[i+1][n+1])
                #print Top, Middle, Bottom
                localAv = (Top + Middle + Bottom)/9
                diff = float(ChromaA[i][n])-localAv
                newls.append((diff,ChromaA[i][0],ChromaA[0][n]))
    print sorted(newls,reverse=True)




Chroma_list= [
                ['n',1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40],
                ['B',2,2,2,2,2,2,2,2,4,6,6,6,6,4,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                ['C',6,6,6,6,6,6,8,14,16,14,12,12,12,10,10,8,8,6,6,6,6,4,4,4,4,4,4,4,6,6,4,4,4,4,6,6,6,6,6,6],
                ['D',8,8,10,10,10,14,14,14,12,12,12,12,12,12,10,10,10,8,8,8,8,8,6,6,6,6,6,8,8,8,6,6,6,6,8,8,10,10,8,8],
                ['E',12,12,12,14,16,12,12,12,10,10,10,10,10,10,12,12,10,10,10,10,8,8,8,8,8,8,8,10,10,10,8,8,8,8,10,10,10,10,12,12],
                ['F',14,14,14,16,14,12,10,10,8,8,8,8,8,8,10,12,12,10,10,10,10,8,8,8,8,8,8,10,12,12,10,10,10,10,10,12,12,12,14,14],
                ['G',14,14,14,14,10,8,8,6,6,6,6,6,6,6,8,8,10,10,10,10,8,8,8,8,6,6,8,8,10,10,12,10,10,10,10,10,10,10,10,10],
                ['H',10,10,12,10,8,6,6,6,4,4,4,4,4,4,6,6,8,8,10,8,6,6,6,6,6,6,6,8,10,10,12,10,10,10,10,10,10,10,10,10],
                ['I',8,8,8,6,4,4,4,2,2,2,2,2,2,2,4,4,4,6,6,6,4,4,4,4,4,4,6,6,6,8,10,8,8,8,6,6,8,8,8,8]]

#that's the chroma values for every chip in the world color survey stimulus

def distanceCalc(mchips):
        ls = mchips
        row=[]
        column=[]
        for j in range(7):      
                for i in range(39*j+j, 39*j+j+39):#by row
                        a=[]
                        x = (float(ls[i][2])-float(ls[i+1][2]))**2
                        y = (float(ls[i][3])-float(ls[i+1][3]))**2
                        z = (float(ls[i][4])-float(ls[i+1][4]))**2
                        dist = (x+y+z)**.5
                        a.append((dist,ls[i][0]+ls[i][1]))
                        row.append(a)
        #by column
        for j in range(39):      
                for i in range(j,280,40):#by column
                        #print i
                        a=[]
                        x = (float(ls[i][2])-float(ls[i+40][2]))**2
                        y = (float(ls[i][3])-float(ls[i+40][3]))**2
                        z = (float(ls[i][4])-float(ls[i+40][4]))**2
                        dist = (x+y+z)**.5
                        a.append((dist,ls[i][0]+ls[i][1]))
                        column.append(sorted(a))
        print "distance by row:",sorted(row,reverse=True)
        print "break"
        print "distance by column:",sorted(column ,reverse=True)
      