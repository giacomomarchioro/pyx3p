from __future__ import print_function
import zipfile
import hashlib
import xml.etree.ElementTree as ET
import numpy as np
"""
This module is an implementation of the .x3p format datastructure using the dot
notation. The xml structure of the .x3p is almost always mantained and made
accessible using the dot notation (e.g. for accessing the revision we can use
x3pfile.record1.revison).
Few execptions have been made to this rule: when there is a data structure that
is clearly easier to describe using an array, a numpy array is used.
This happens:
    - for the rotation matrix there are no r11,r12 etc. etc. param but a 3 x 3
      numpy matrix (r11 at index 0,0)
    - in case there is a profile encoded in the xml file ( a DataList).
    -

Issues not solved:
   - there are some problems with encoding e.g. accent, greekletters

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

    def get_rotation(self, row, col):
        return self.rotation[row-1, col-1]

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
        self.manufacturer = manufacturer

    def set_model(self,model):
        '''
        Name of the machine model used for the measurement
        '''
        self.model = model.encode('utf-8')

    def set_serial(self,serial):
        '''
        Serial number of the machine.
        '''
        self.serial = serial

    def set_version(self,version):
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

    def set_date(self, datetimeisostring,):
        """Date and time of file creation.It must be xsd:dateTime"""
        # TODO: this should be implemented for checking that is the right
        # format
        self.date = datetimeisostring

    def set_calibrationdate(self, datetimeisostring,):
        """	Date of currently used calibrationIt must be xsd:dateTime"""
        # TODO: this should be implemented for checking that is the right
        # format
        self.date = datetimeisostring

    def set_creator(self, name):
        """Method for setting the name of the creator.
        Optional name of the creator of the file: Name of the measuring person.
        """
        if str.isdigit(str(name.encode('utf8'))):
            # This doesn't work for float
            print('Excpected a string with the creator name. Get:%s' % (name))
        else:
            self.creator = name


    def set_comment(self, name):
        """	User comment to this data set
        """
        if str.isdigit(str(name.encode('utf8'))):
            # This doesn't work for float
            print('Excpected a string with the creator name. Get:%s' % (name))
        else:
            self.creator = name

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
        self.MD5ChecksumValidPoints = checksum

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


class x3pfile(object):
    """docstring for x3pfile."""
    def __init__(self,):
        self.data = np.array([])
        self.record1 = Record1()
        self.record2 = Record2()
        self.record3 = Record3()
        self.record4 = Record4()
        self.VendorSpecificID = None

    def convert_datatype(self, dtype):
        '''
        This tool is used to cenvert datatype
        '''
        dt = {"I": np.int16,
              "L": np.int32,
              "F": np.float32,
              "D": np.float64,
              np.int16: "I",
              np.int32: "L",
              np.float32: "F",
              np.float64: "D"}
        return dt[dtype]

    def set_VendorSpecificID(self, url):
        '''This is an extension hook for vendor specific data formats derived
        from ISO5436_2_XML. This tag contains a vendor specific ID which is the
        URL of the vendor. It does not need to be valid but it must be
        worldwide unique!Example: http://www.example-inc.com/myformat
        '''
        pass


    def read(self, filepath):
        # The x3p file format is zipped.
        zfile = zipfile.ZipFile(filepath, 'r')
        # We read the md5 checksum from the file inside the .zip
        # Note: there is also the *main.xml we use `.split` to eliminate it.
        # We use as convention to convert checksum to lower case letters.
        checksum = zfile.read('md5checksum.hex').split(' ')[0].lower()
        # We now calculate the checksum from the main.xml.
        checksum_calc = hashlib.md5(zfile.read('main.xml')).hexdigest().lower()
        if checksum != checksum_calc:
            print("WARNING: checksum doesn't match!")
        tree = ET.parse(zfile.open('main.xml'))
        root = tree.getroot()
        # return tree,root #for debug
        # We first get the records it would not be efficient to iter all the
        # root because sometimes Record3 contains very long profiles

        records = {}
        for child in root:
            records[child.tag] = child

        axes = None
        # We must take care that field with minOccurs = 0 could not be present
        # we use "if" structure to avoid using execption.
        # We also use the setter method for double check the import.
        for item in records['Record1']:
            if item.tag == 'Revision':
                self.record1.revision = item.text
            if item.tag == 'FeatureType':
                self.record1.set_featuretype(item.text)
            if item.tag == 'Axes':
                axes = item
        for ax in axes:
            if ax.tag == 'CX':
                for elem in ax:
                    if elem.tag == 'AxisType':
                        self.record1.axes.CX.set_axistype(elem.text)
                    if elem.tag == 'Increment':
                        self.record1.axes.CX.set_increment(elem.text)
                    if elem.tag == 'Offset':
                        self.record1.axes.CX.set_offset(elem.text)
                    if elem.tag == 'DataType':
                        self.record1.axes.CX.set_datatype(elem.text)

            if ax.tag == 'CY':
                for elem in ax:
                    if elem.tag == 'AxisType':
                        self.record1.axes.CY.set_axistype(elem.text)
                    if elem.tag == 'Increment':
                        self.record1.axes.CY.set_increment(elem.text)
                    if elem.tag == 'Offset':
                        self.record1.axes.CY.set_offset(elem.text)
                    if elem.tag == 'DataType':
                        self.record1.axes.CY.set_datatype(elem.text)

            if ax.tag == 'CZ':
                for elem in ax:
                    if elem.tag == 'AxisType':
                        self.record1.axes.CZ.set_axistype(elem.text)
                    if elem.tag == 'Increment':
                        self.record1.axes.CZ.set_increment(elem.text)
                    if elem.tag == 'Offset':
                        self.record1.axes.CZ.set_offset(elem.text)
                    if elem.tag == 'DataType':
                        self.record1.axes.CZ.set_datatype(elem.text)

            if ax.tag == 'Rotation':
                # we construct the rotation matrix using the set rotation and
                # the indexes taken from the element tag.
                for elem in ax:
                    col, row = elem.tag[1:]
                    self.record1.axes.set_rotation(int(row),
                                                   int(col), elem.text)

        def xml2dict(elem):
            xdict = {}
            for item in elem.iter():
                xdict[item.tag] = item.text
            return xdict

        # Records2 is optional so we check if it's in the records list
        if 'Record2' in records:
            # filed in record2 are unique we use a dict
            xd = xml2dict(records['Record2'])
            # even though the whole record is not mandatory some value are
            self.record2.set_date(xd['Date'])
            self.record2.probingsystem.set_type(xd['Type'])
            self.record2.probingsystem.set_identification(xd['Identification'])
            self.record2.instrument.set_model(xd['Model'])
            self.record2.instrument.set_serial(xd['Serial'])
            self.record2.instrument.set_manufacturer(xd['Manufacturer'])
            self.record2.instrument.set_version(xd['Version'])
            self.record2.set_calibrationdate(xd['CalibrationDate'])
            if 'Creator' in xd:
                self.record2.set_creator(xd['Creator'])
            if 'Comment' in xd:
                self.record2.set_comment(xd['Comment'])

        else:
            self.record2 = None

        # Records3 is more problematic because it could contain a lot of data
        for elem in records['Record3']:
            if elem.tag == 'MatrixDimension':
                xd = xml2dict(elem)
                self.record3.matrixdimension.set_sizeX(xd['SizeX'])
                self.record3.matrixdimension.set_sizeY(xd['SizeY'])
                self.record3.matrixdimension.set_sizeZ(xd['SizeZ'])

            if elem.tag == 'DataLink':
                # This mean that we have a binary file
                mask = np.ma.nomask
                for i in elem:
                    if i.tag == 'PointDataLink':
                        self.record3.datalink.set_PointDataLink(i.text)
                        binfile = zfile.read(i.text)
                    if i.tag == 'MD5ChecksumPointData':
                        self.record3.datalink.set_MD5ChecksumPointData(i.text)
                        # We check the checksum on the way
                        checksum_calc = hashlib.md5(binfile).hexdigest()
                        if checksum_calc.lower() != i.text.lower():
                            print("Checksums bin data are different!")

                    if i.tag == 'ValidPointsLink':
                        self.record3.datalink.set_ValidPointsLink(i.text)
                        validpoints = zfile.read(i.text)

                    if i.tag == 'MD5ChecksumValidPoints':
                        self.record3.datalink.set_MD5ChecksumValidPoints(i.text)
                        # We check the checksum on the way
                        checksum_calc = hashlib.md5(validpoints).hexdigest()
                        if checksum_calc.lower() != i.text.lower():
                            print("Checksums valid bin data are different!")

                    if self.record3.matrixdimension.sizeZ == 1:
                        size = (self.record3.matrixdimension.sizeX,
                                self.record3.matrixdimension.sizeY)
                        dtypes = self.record1.axes.get_axes_dataype()
                        if len(dtypes) == 1:
                            dtype = self.convert_datatype(dtypes.pop())
                            data = np.frombuffer(binfile, dtype=dtype)
                            self.data = np.ma.masked_array(data,
                                                           mask=mask,
                                                           dtype=dtype
                                                           ).reshape(size)

            #np.ma.masked_array([(1,2,3),(3,4,5),(5,6,7)],dtype = [('x', 'i8'), ('y',   'f4'),('z','i8')])

            if elem.tag == 'DataList':
                self.record3.datalink = None
                datalist = []
                for value in elem:
                    if value.text is None:  # it means its an invalid entry
                        nanarr = [np.nan]*self.record3.matrixdimension.sizeZ
                        datalist.append(nanarr)
                    else:
                        datalist.append(value.text.split(';'))

                dtypes = self.record1.axes.get_axes_dataype()
                if len(dtypes) == 1:
                    dtype = self.convert_datatype(dtypes.pop())
                    self.data = np.array(datalist, dtype=dtype).T
