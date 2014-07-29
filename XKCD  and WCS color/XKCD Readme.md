
XKCD-World Color Survey

======================





WELCOME TO THE WIDE WORLD OF COLOR





super concise summary: The code below can 'average' colors together in a way 
that would make sense to a painter, and interact with the data from both the 
XKCD
#color survey, as well as academic research on color

#Less concise summary: 
This code contains the tools necessary to a) investigate the xkcd color database,
 b) transform rgb values to perceptually even colorspaces,
# c) Plot colors in
 perceptually even 3d colorspace and d) compare with the results of the World Color Survey.
#For instance,
 If you are curious about what all of the 'happy' colors (aka 'happy blue', 'happy green',
 look like, what their perceptual center is,
#as well as how this relates to the munsell standard color reference)
 you are in the right place.


#there are also routines for converting RGB to CIELab and CIELove space
 with various types of illuminants, primaries, and chromatic adaptations- the 
#RGB to XYZ coefficents
 are calculated in-house.
#Additionally, there are tools for (some) linguistic analysis of the color terms




Towards the bottom, there is a routine for looking into the non-uniformity of the WCS stimulus, specifically 
looking at chromatic pop-out



#thanks to the good folks at Enthought and the authors of the Mayavi package, 
Brent Berlin, Paul Kay, Randall Munroe, all those involved in the WCS or the XKCD color survey 
and Terry Regier and the fine folks at the U.C. Berkeley Language and Cognition Lab. Especially Emily Cibelli.


 Questions? email evanw@evanwarfel.com  if you do use this in something publication worthy, please cite me. 
This code is for academic/research purposes only, unless you contact me first.


A note on illuminants: The original 
Berlin and Kay study,(1969) used illuminant A
, where as the WCS
used the shady outdoors, which illuminant d65 attemps to capture
 .

however, the LAB values for the munsell chips in the WCS were calculated with the C illuminant.

note that all colorings of the 3d chips are only approximations.

