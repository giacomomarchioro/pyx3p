from __future__ import print_function
import zipfile
import hashlib
import xml.etree.ElementTree as ET
import numpy as np
import _x3pfileclasses
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
__all__ = ['x3pfile']

class x3pfile(object):
    """docstring for x3pfile."""
    def __init__(self,):
        self.data = np.array([])
        self.record1 = _x3pfileclasses.Record1()
        self.record2 = _x3pfileclasses.Record2()
        self.record3 = _x3pfileclasses.Record3()
        self.record4 = _x3pfileclasses.Record4()
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


    def load(self, filepath):
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
