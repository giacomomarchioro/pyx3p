# pyx3p
This is an unofficial Python module that allows opening the .x3p file format created by [OpenGPS consortium](http://open-gps.sourceforge.net/).

## How it's structured
This module is an implementation of the X3P format data structure using the dot
notation. The XML structure of the .x3p is almost always maintained and made
accessible using the dot notation. For instance, for accessing the revision field. First, we create an instance of X3Pfile class (e.g. `anx3pfile`) then we can use
anx3pfile.record1.revison.
The same is true for the other fields (creator, comment, etc. etc.). 
Few exceptions have been made to this rule: when there is a data structure that
is clearly easier to describe using an array, a numpy array is used.
This happens:

    - for the rotation matrix there are no r11,r12 etc. etc. params but a 3 x 3
      numpy matrix (r11 at index 0,0)
    - in case there is a profile encoded in the xml file ( a DataList).

The attribute `data` contains the data as a masked numpy array. Using this data structure is possible to add the valid points as a `mask` attribute.

## Requirements
All the module is based on the standard library except for numpy.

## Installation
You can install the module using: 
```
pip install git+https://github.com/giacomomarchioro/pyx3p
```

 
## Reading an .x3p file 
The followings examples assume you have downloaded the .x3p file samples from the [OpenGPS website](https://sourceforge.net/projects/open-gps/files/Sample-Files/).

```python
from x3p import X3Pfile
anx3pfile = X3Pfile('1-euro-star.x3p')
# access an attribute
anx3pfile.record1.featuretype
anx3pfile.record1.axes.CX.axistype
# access the data
anx3pfile.data
```

For plotting, matplotlib can be used.

```python
# assuming you have run succeffuly the previous code
import matplotlib.pyplot as plt
plt.pcolormesh(anx3pfile[:,:,0])
plt.show()
```

## Writing an .x3p file
** This feature is under testing**
Writing a file can be done easily using the same data structure. Because the module doesn't use any `.xsd` for checking the XML structure all the rules on the `.xsd` file have been converted in python conditional statements. To ensure that the XML structure is correct the user should use the `set` methods create for every attribute (missing for date attribute at the moment).

```python
from x3p import X3Pfile
# We create an empty data structure
anx3pfile = X3Pfile()
# access an attribute
anx3pfile.record1.set_featuretype('SUR')
anx3pfile.record1.axes.CX.axistype
# access the data
anx3pfile.data

```