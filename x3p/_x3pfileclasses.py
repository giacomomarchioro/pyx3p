from __future__ import print_function
import numpy as np
from datetime import datetime
import warnings
"""
This implements the elements of the xmltree using python classes and the xsd
rules using conditional statements.
"""
class Ax(object):
    """docstring for axes. Here we have an additional axisname attribute, not
    present in the original implementation, for checking that if the axistype
    is Z it should be "A" by defult."""
    def __init__(self, name):
        self.axistype = None
        self.datatype = None
        self.increment = None
        self.offset = None
        self.axisname = name

    def set_axistype(self, axistype):
        """
        Type of axis can be "I" for Incremental, "A" for Absolute.
        The z-axis must be absolute!
        """
        if axistype in ["I", "A"]:
            if self.axisname == 'CZ':
                self.axistype = 'A'
                print("The z-axis is set absolute by defult")
            else:
                self.axistype = axistype
        else:
            print("Axistype must be incremental (I) or absolute (A) get:")
            print(axistype)

    def set_datatype(self, datatype):
        """
        Data type for absolute axis: "I" for int16, "L" for int32, "F" for
        float32, "D" for float64. Incremental axes do not have/need a data type.
        """
        if datatype in ["I", "L", "F", "D"]:
            self.datatype = datatype
        else:
            print("In axis %s" % (self.axisname))
            print("Datatype must be: I, F or D get: %s" % (datatype))

    def set_increment(self, increment):
        """
        Needed for incremental axis and integer data types: Increment is the
        multiplyer of the integer coordinate for the computation of the	real
        coordinate: Xreal = Xoffset + Xinteger*XIncrement.
        The unit of increment and offset is metre.
        """
        self.increment = float(increment)

    def set_offset(self, offset):
        """
        The offset of axis in meter.
        """
        self.offset = float(offset)

    def get_datatypeobj(self, dt=None):
        """
        Return the corrispective numpy datatype.
           I -> np.int16
           L -> np.int32
           F -> np.float32
           D -> np.float64
        """
        if dt is None:
            dt == self.datatype
        datatypes = {"I": np.int16,
                     "L": np.int32,
                     "F": np.float32,
                     "D": np.float64,
                     }
        return datatypes[dt]


class Axes(object):
    """
    The axes calss contains information regarding the axes.
    Instead of storing the rotation matrix as separate fields a numpy array of
    fload is used.

    The optional transformation contains a 3D rotation matrix R with 3 by 3
    elements that is used to rotate the data points in its final orientation.
    The full transformation consists of a rotation and a following translation
    that is taken from the	AxisDescriptionType.Offset elements: Q = R*P + T
    with Q	beeing the final point, P the coordinate as specified in Record3,
    R the 3 by 3 rotation matrix and T the	3-element offset vector.
    The * denotes a matrix product.
    The formula for the x coordinate is:
    Qx = r11*Px+r12*Py+r13*Pz + Tx
    The formula for the y coordinate is:
    Qy = r21*Px+r22*Py+r23*Pz + Ty
    The formula for the z coordinate is:
    Qz = r31*Px+r32*Py+r33*Pz + Tz.s
               x
         __1   2  3__
       1 |11  12  13 |
     y 2 |21  22  23 |
       3 |31  32  33 |

    """
    def __init__(self):
        self.CX = Ax('CX')
        self.CY = Ax('CY')
        self.CZ = Ax('CZ')
        self.rotation = np.zeros((3, 3), float)

    def set_rotation(self, row, col, value):
        if -1 <= float(value) <= 1:
            # WARNING we use xindex - 1 to start counting from 1.
            self.rotation[row-1, col-1] = float(value)
        else:
            print("Value must be in range -1 to 1. Get: %s " % (value))

    def get_rotation(self, row, col, as_string=False):
        rot = self.rotation[row-1, col-1]
        if as_string:
            rot = str(rot)
        return rot

    def set_no_rotation(self):
        self.rotation = np.fill_diagonal(self.rotation, 1)

    def get_axes_dataype(self):
        '''
        Return a tuple with the number of axes and the dataypes of the axes.
        If the dataype is the same for all the axes a single numpy datatype
        is returned (e.g. np.float32).
        '''
        return {self.CX.datatype, self.CY.datatype, self.CZ.datatype}


class Record1(object):
    '''Record1 contains the axis description'''
    def __init__(self):
        # Revision of file format. Currently: ISO5436 - 2000
        self.revision = 'ISO5436 -2000'
        self.featuretype = None
        self.axes = Axes()

    def set_featuretype(self, featuretype):
        """
        This method is used for setting the feature type.
        "SUR" for surface type feature, "PRF" for profile type feature or "PCL"
        for unordered point clouds.
        Profile features are allways defined as a matrix of size (N,1,M) with N
        beeing the number of points in the profile and M the number of layers
        in z-direction.Point clouds have to be stored as list type.
        """
        if featuretype in ["SUR", "PLC", "PRF"]:
            self.featuretype = featuretype
        else:
            print("Feature type must be one of the following: SUR,PLC or PRF")
            print("Get: %s" % (featuretype))
# End of Record1 classes.


class Instrument(object):
    """docstring for Instrument."""
    def __init__(self):
        self.manufacturer = None
        self.model = None
        self.serial = None
        self.version = None

    def set_manufacturer(self, manufacturer):
        '''
        Name of the equipment manufacturer
        '''
        self.manufacturer = manufacturer.encode('utf-8')

    def set_model(self, model):
        '''
        Name of the machine model used for the measurement
        '''
        self.model = model.encode('utf-8')

    def set_serial(self, serial):
        '''
        Serial number of the machine.
        '''
        self.serial = serial

    def set_version(self, version):
        '''
        Software and hardware version strings used to create this file.
        '''
        self.version = version



class ProbingSystem(object):
    """docstring for ProbingSystem."""
    def __init__(self):
        self.type = None
        self.identification = None

    def set_type(self, instrument_type):
        """ one of "NonContacting" or "Contacting" or "Software" """
        if instrument_type in ["NonContacting", "Contacting", "Software"]:
            self.type = instrument_type
        else:
            print("Instrument type must be one of the following:")
            print(" 'NonContacting', 'Contacting', 'Software' ")
            print("Get: %s" % (instrument_type))

    def set_identification(self, identification):
        """
        Vendor specific identification of probe tip,lens, etc...
        """
        self.identification = identification


class Record2(object):
    """Record2 is optional and contains the metadata of the data set."""
    def __init__(self):
        self.date = None
        self.creator = None
        self.instrument = Instrument()
        self.calibrationdate = None
        self.probingsystem = ProbingSystem()
        self.comment = None

    def _check_datetime(self,datetime_str,url=None):
        if datetime_str is not None:
            try:
                datetime.strptime(datetime_str,'%Y-%m-%dT%H:%M:%S')
            except ValueError:
                msg = ('The date must be in the following format es. 2020-6-14T18:30:29\n')
                warnings.warn(msg + "\n it was: %s"%datetime_str,stacklevel=3)
        return datetime_str

    def set_date(self, datetimeisostring,):
        """Date and time of file creation.It must be xsd:dateTime"""
        self.date = self._check_datetime(datetimeisostring)

    def set_calibrationdate(self, datetimeisostring,):
        """	Date of currently used calibrationIt must be xsd:dateTime"""
        self.calibrationdate = self._check_datetime(datetimeisostring)

    def set_creator(self, name):
        """Method for setting the name of the creator.
        Optional name of the creator of the file: Name of the measuring person.
        """
        if str.isdigit(str(name.encode('utf8'))):
            # This doesn't work for float
            print('Excpected a string with the creator name. Get:%s' % (name))
        else:
            self.creator = name.encode('utf-8')


    def set_comment(self, name):
        """	User comment to this data set
        """
        if str.isdigit(str(name.encode('utf8'))):
            # This doesn't work for float
            print('Excpected a string with the comment. Get:%s' % (name))
        else:
            self.comment = name.encode('utf-8')

# End of Record2 classes.


class MatrixDimension(object):
    """docsting for Matrix"""
    def __init__(self):
        self.sizeX = None
        self.sizeY = None
        self.sizeZ = None

    def set_sizeX(self, value):
        self.sizeX = int(value)

    def set_sizeY(self, value):
        self.sizeY = int(value)

    def set_sizeZ(self, value):
        self.sizeZ = int(value)

class DataLink(object):
    """docstring for DataLink."""
    def __init__(self):
        self.PointDataLink = None
        self.MD5ChecksumPointData = None
        self.ValidPointsLink = None
        self.MD5ChecksumValidPoints = None

    def set_PointDataLink(self, pointdatalink):
        """
        This should be the link to the point data.
        Should be bin\
        """
        self.PointDataLink = pointdatalink

    def set_MD5ChecksumPointData(self, checksum):
        """ """
        self.MD5ChecksumPointData = checksum

    def set_ValidPointsLink(self, validpointslink):

        self.ValidPointsLink = validpointslink

    def set_MD5ChecksumValidPoints(self, checksum):
        self.MD5ChecksumValidPoints = checksum


class Record3(object):
    """docstring for Record4"""
    def __init__(self):
        self.matrixdimension = MatrixDimension()
        self.datalink = DataLink()
        self.datalist = None
        self.listdimension = None

    def set_datalist(self, array):
        """ Data list is ordered like specified in
    DataOrder: Z-Index is empty (only one sample
    per pixel) X is fastest index, Y is slower,
    Z is slowest:
    (x1,y1),(x2,y1),(x3,y1),(x4,y1),(x1,y2)..."""
        pass

    def set_listdimension(self, dimension):
        """A list does specify an unordered data set
        like a point cloud which does not contain
        topologic information."""
        self.listdimension = int(dimension)

# End of Record 3 classes.


class Record4(object):
    """Record4 contains only the checksum of the xml file."""
    def __init__(self):
        self.checksumfile = None
