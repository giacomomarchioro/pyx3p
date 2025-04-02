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

The attribute `data` contains the data as a masked numpy array. Using this data structure it is possible to add the valid points as a `mask` attribute.

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
plt.imshow(anx3pfile.data)
plt.colorbar()
plt.show()
```

## Writing an .x3p file
**This feature is under testing**
Writing a file can be done easily using the same data structure. Because the module does not use any `.xsd` for checking the XML structure all the rules on the `.xsd` file have been converted in python conditional statements. To ensure that the XML structure is correct the user should use the `set` methods create for every attribute.

```python
from x3p import X3Pfile
import numpy as np
import hashlib 
# We create an empty data structure
anx3pfile = X3Pfile()
anx3pfile.set_VendorSpecificID("https://github.com/giacomomarchioro/pyx3p")
# Record 1
anx3pfile.record1.set_featuretype('SUR')

anx3pfile.record1.axes.CX.set_axistype('I')
anx3pfile.record1.axes.CX.set_increment(50/1000**2) # 50 microns scan step
anx3pfile.record1.axes.CX.set_offset(50/1000) # 50 mm offset
# anx3pfile.record1.axes.CX.set_datatype("L")

anx3pfile.record1.axes.CY.set_axistype('I')
anx3pfile.record1.axes.CY.set_increment(50/1000**2) # 50 microns scan step
anx3pfile.record1.axes.CY.set_offset(50/1000) # 50 mm offset
# anx3pfile.record1.axes.CY.set_datatype("L")

# CZ is by default incremental with increment 1
# anx3pfile.record1.axes.CZ.set_datatype("L")
# Record 2
anx3pfile.record2.set_calibrationdate("2008-08-25T13:59:21.4+02:00")
anx3pfile.record2.set_creator("Giacomo Marchioro")
anx3pfile.record2.set_date("2008-08-25T13:59:21.4+02:00")
anx3pfile.record2.instrument.set_manufacturer("Univeristy of Verona (Optimet-Physics Instrumente)")
anx3pfile.record2.instrument.set_model("ConoProbe-3H")
anx3pfile.record2.instrument.set_serial("Not availabe")
anx3pfile.record2.instrument.set_version("v3")
anx3pfile.record2.probingsystem.set_identification("25 mm lens")
anx3pfile.record2.probingsystem.set_type("NonContacting")
anx3pfile.record2.set_comment("Example of scan.")

# we generate a 2D array of distances with a sine pattern as sample data
sin2d = np.vstack([np.sin(np.arange(-12.0, 12.0, 1))]*12)/1000**2 # microns
# Create boolean mask array
mask = np.zeros(sin2d.shape, dtype=bool)  # Important: specify dtype=bool
# we mask the forth, fifth and sixth row (True values will be masked)
mask[[3,4,5],:] = True
# Create masked array with the boolean mask
data = np.ma.masked_array(sin2d, mask=mask)
anx3pfile.set_data(data)
anx3pfile.write('mytest2')
```

## Things to remember
We save the mask in the `bindata\valids.bin` (I could not find any recomandation on the standard).
The data must be provided in the following dimension data[layers,x_dim,y_dim]. Remember it is a layer if X and Y are set to incremental otherwise the other two array contain the coordinates of the heights variations.