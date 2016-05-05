
#XKCD-World Color Survey

======================





WELCOME TO THE WIDE WORLD OF COLOR





##Super Concise Summary: 
The code in this directory 'average' colors together in a way that would make sense to a painter, and interact with the data from both the XKCDcolor survey, as well as academic research on colornaming and categorization.

###Less Concise Summary: 
This code contains the tools necessary to
a) investigate the xkcd color database,
b) transform rgb values to perceptually even colorspaces,
c) Plot colors in perceptually even 3d colorspace and d) compare with the results of the World Color Survey.

For instance, if you are curious about what all of the 'happy' colors (aka 'happy blue', 'happy green',
look like, what their perceptual center is,as well as how this relates to the munsell standard color reference)
you are in the right place.


There are also routines for converting RGB to CIELab and CIELove space
 with various types of illuminants, primaries, and chromatic adaptations- the 
RGB to XYZ coefficents  are calculated in-house.

Additionally, there are tools for (some) linguistic analysis of the color terms. Towards the bottom, there is a routine for looking into the non-uniformity of the WCS stimulus, specifically 
looking at chromatic pop-out


##Other Notes:

Vendi Vidi Ceviche, er Caveat Emptor.

This was the first real coding project I ever did, so expect to find plenty of odd code. It works, it's useful if you know what you are looking for, but it ain't pretty.

Thanks to the good folks at Enthought and the authors of the Mayavi package, 
Brent Berlin, Paul Kay, Randall Munroe, all those involved in the WCS or the XKCD color survey 
and Terry Regier and the fine folks at the U.C. Berkeley Language and Cognition Lab. Especially Emily Cibelli.


## Questions? 
Email hello@evanwarfel.com if you have any questions. If you do use this in something publication worthy, please cite me if you have the cance to do so. 
This code is for academic/research purposes only, unless you contact me first.


#Technical Note-
A note on illuminants: The original 
Berlin and Kay study,(1969) used illuminant A, whereas the WCS used the grand ol' shady outdoors, which illuminant d65 attemps to capture. However, the LAB values for the munsell chips in the WCS were calculated with the C illuminant.

Please note that all colorings of the 3d chips are only approximations.

