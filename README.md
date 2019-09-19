# pyx3p
This is an unofficial Python module that allows to open the .x3p file format create by OpenGPS consortium.

## How it's structured
This module is an implementation of the X3P format datastructure using the dot
notation. The xml structure of the .x3p is almost always mantained and made
accessible using the dot notation. For instance, for accessing the revision field, first we create an instance of X3Pfile class (e.g. `anx3pfile`) then we can use
anx3pfile.record1.revison.
The same is true for the other fields (creator, comment, etc. etc.). 
Few execptions have been made to this rule: when there is a data structure that
is clearly easier to describe using an array, a numpy array is used.
This happens:

    - for the rotation matrix there are no r11,r12 etc. etc. params but a 3 x 3
      numpy matrix (r11 at index 0,0)
    - in case there is a profile encoded in the xml file ( a DataList).

The attribute `data` contains the data as a masked numpy array. Using this data structure is possible to add the valids point as a `mask` attribute.

## Requirements
All the module is based on the standard library except for numpy.

## Installation
At the moment you have to clone the x3p folder in your working directory or in a directory listed in your python path. 

 
## Reading an .x3p file 
The followings examples assume you have downoladed the .x3p file samples from the OpenGPS website.

```python
from x3p import X3Pfile
anx3pfile = X3Pfile('1-euro-star.x3p')
# access an attribute
anx3pfile.record1.featuretype
anx3pfile.record1.axes.CX.axistype
# access the data
anx3pfile.data
```

For plotting matplotlib can be used.

```python
# assuming you have run succeffuly the previous code
import matplotlib.pyplot as plt
plt.pcolormesh(anx3pfile[:,:,0])
plt.show()
```

## Writing an .x3p file
** This feature is under developing**
Writing a file can be done easly using the same data structure. Because the module don't use any `.xsd` for checking the xml structure all the rules on the `.xsd` file have been converte in python conditional statements. To ensure that the xml structure is correct the user should used the `set` methods create for every attribute (missing for date attribute  at the moment).

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


