from __future__ import print_function
import zipfile
import hashlib
import xml.etree.ElementTree as ET
import numpy as np
from . import _x3pfileclasses
import warnings
import logging
try:
    # python2
    from urlparse import urlparse
except ModuleNotFoundError:
    # python3
    from urllib.parse import urlparse
"""
This module is an implementation of the .x3p format datastructure using the dot
notation. The xml structure of the .x3p is almost always mantained and made
accessible using the dot notation (e.g. for accessing the revision we can use
x3pfile.record1.revison).
Few execptions have been made to this rule: when there is a data structure that
is clearly easier to describe using an array, a numpy array is used.
This happens:
    - for the rotation matrix there are no r11,r12 etc. etc. params but a 3 x 3
      numpy matrix (r11 at index 0,0)
    - in case there is a profile encoded in the xml file ( a DataList).
    -

Issues not solved:
   - there are some problems with encoding e.g. accent, greekletters

"""
__all__ = ['X3Pfile']

class X3Pfile(object):
    """docstring for x3pfile."""
    def __init__(self, filepath=None):
        self.data = np.array([])
        self.record1 = _x3pfileclasses.Record1()
        self.record2 = _x3pfileclasses.Record2()
        self.record3 = _x3pfileclasses.Record3()
        self.record4 = _x3pfileclasses.Record4()
        self.VendorSpecificID = None
        self.infos = {'Rotation': False, 'Record2': False}
        self.warnings = warnings
        self.logging = logging
        if filepath is not None:
            self.load(filepath)

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
        result = urlparse(url)
        if not all([result.scheme, result.netloc, result.path]):
            raise ValueError("%s does not appear as a valid url." %url)
        else:
            self.VendorSpecificID = url

    def infer_metadata(self, override=False, verbose=True):
        '''
        This function try to fill the metadata from the numpy array describing
        the surface.
        '''
        raise NotImplementedError
        self.data.shape

    def load(self, filepath):
        # The x3p file format is zipped.
        zfile = zipfile.ZipFile(filepath, 'r')
        # We read the md5 checksum from the file inside the .zip
        # Note: there is also the *main.xml we use `.split` to eliminate it.
        # We use as convention to convert checksum to lower case letters.
        checksum_line = zfile.read('md5checksum.hex').decode('utf8')
        checksum = checksum_line.split(' ')[0].lower()
        # We now calculate the checksum from the main.xml.
        checksum_calc_xml = zfile.read('main.xml')
        checksum_calc = hashlib.md5(checksum_calc_xml).hexdigest().lower()
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
                self.infos['Rotation'] = True
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
            # fileds in record2 are unique we use a dict
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
                self.record3.datalist = False
                # This mean that we have a binary file
                print('Found a binary file')
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
                    axest = self.record1.axes.get_XYaxes_types()
                    # if we have incremental axis 
                    if axest == ['I','I']:
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
                            else:
                                msg = "Multipe datatypes not implemented"
                                raise NotImplementedError(msg)

                        elif self.record3.matrixdimension.sizeZ > 1:
                            # This is the case of multiple layers
                            size = (self.record3.matrixdimension.sizeZ,
                                    self.record3.matrixdimension.sizeX,
                                    self.record3.matrixdimension.sizeY,
                                    )
                            dtypes = self.record1.axes.get_axes_dataype()
                            if len(dtypes) == 1:
                                dtype = self.convert_datatype(dtypes.pop())
                                data = np.frombuffer(binfile, dtype=dtype)
                                self.data = np.ma.masked_array(data,
                                                            mask=mask,
                                                            dtype=dtype
                                                            ).reshape(size)
                            else:
                                msg = "Multipe datatypes not implemented"
                                raise NotImplementedError(msg)

                    # for absolute axes the shape contains also the coordinates
                    elif axest == ['A','A']:
                        if self.record3.matrixdimension.sizeZ == 1:
                            size = (self.record3.matrixdimension.sizeX,
                                    self.record3.matrixdimension.sizeY,
                                    3) # Z is set to 3 becuase it contains also the x,y coordinates
                            dtypes = self.record1.axes.get_axes_dataype()
                            if len(dtypes) == 1:
                                dtype = self.convert_datatype(dtypes.pop())
                                data = np.frombuffer(binfile, dtype=dtype)
                                self.data = np.ma.masked_array(data,
                                                            mask=mask,
                                                            dtype=dtype
                                                            ).reshape(size)
                            else:
                                msg = "Multipe datatypes not implemented"
                                raise NotImplementedError(msg)
                    else:
                        raise NotImplementedError("Incremental and absolute axes togehter are not implemented.")

            #np.ma.masked_array([(1,2,3),(3,4,5),(5,6,7)],dtype = [('x', 'i8'), ('y',   'f4'),('z','i8')])

            if elem.tag == 'DataList':
                print('Found a datalist')
                self.record3.datalink = False
                datalist = []
                # it could be reasonable to expect sizeZ to be the number of
                # profiles
                n_profiles = self.record3.matrixdimension.sizeZ
                for value in elem:
                    if value.text is None:  # it means its an invalid entry
                    # actualy xsd:float has also a NaN value that could be used
                        nanarr = [np.nan]*n_profiles
                        datalist.append(nanarr)
                    else:
                        values = value.text.split(';')
                        datalist.append(values)
                        if len(values) > n_profiles:
                            n_profiles = len(values)


                dtypes = self.record1.axes.get_axes_dataype()
                if len(dtypes) == 1:
                    dtype = self.convert_datatype(dtypes.pop())
                    data = np.array(datalist, dtype=dtype)
                    self.data = data.T
            # Record4 contains only one element
            self.record4.checksumfile = records['Record4'][0].text

    def write(self, filepath):
        # XML file creation: > check if the element present (if not mandatory)
        #                    > recreate the datastructure from the numpy arrays
        p = ET.Element('p:ISO5436_2')
        p.set("xmlns:p", "http://www.opengps.eu/2008/ISO5436_2")
        p.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        p.set("xsi:schemaLocation",
              "http://www.opengps.eu/2008/ISO5436_2 http://www.opengps.eu/2008/ISO5436_2/ISO5436_2.xsd")
        Record1 = ET.SubElement(p, 'Record1')
        Revision = ET.SubElement(Record1, 'Revision')
        Revision.text = self.record1.revision
        FeatureType = ET.SubElement(Record1, 'FeatureType')
        FeatureType.text = self.record1.featuretype
        Axes = ET.SubElement(Record1, 'Axes')
        CX = ET.SubElement(Axes, 'CX')
        AxisType = ET.SubElement(CX, 'AxisType')
        AxisType.text = self.record1.axes.CX.axistype
        if self.record1.axes.CX.datatype is not None:
            DataType = ET.SubElement(CX, 'DataType')
            DataType.text = self.record1.axes.CX.datatype
        if self.record1.axes.CX.increment is not None:
            Increment = ET.SubElement(CX, 'Increment')
            Increment.text = str(self.record1.axes.CX.increment)
        if self.record1.axes.CX.offset is not None:
            Offset = ET.SubElement(CX, 'Offset')
            Offset.text = str(self.record1.axes.CX.offset)
        CY = ET.SubElement(Axes, 'CY')
        AxisType = ET.SubElement(CY, 'AxisType')
        AxisType.text = self.record1.axes.CY.axistype
        if self.record1.axes.CY.datatype is not None:
            DataType = ET.SubElement(CY, 'DataType')
            DataType.text = self.record1.axes.CY.datatype
        if self.record1.axes.CY.increment is not None:
            Increment = ET.SubElement(CY, 'Increment')
            Increment.text = str(self.record1.axes.CY.increment)
        if self.record1.axes.CY.offset is not None:
            Offset = ET.SubElement(CY, 'Offset')
            Offset.text = str(self.record1.axes.CY.offset)
        CZ = ET.SubElement(Axes, 'CZ')
        AxisType = ET.SubElement(CZ, 'AxisType')
        AxisType.text = self.record1.axes.CZ.axistype
        if self.record1.axes.CZ.datatype is not None:
            DataType = ET.SubElement(CZ, 'DataType')
            DataType.text = self.record1.axes.CZ.datatype
        if self.record1.axes.CZ.increment is not None:
            Increment = ET.SubElement(CZ, 'Increment')
            Increment.text = str(self.record1.axes.CZ.increment)
        if self.record1.axes.CZ.offset is not None:
            Offset = ET.SubElement(CZ, 'Offset')
            Offset.text = str(self.record1.axes.CZ.offset)
        if self.infos['Rotation']:  # We chek if we have a rotation
            Rotation = ET.SubElement(Axes, 'Rotation')
            r11 = ET.SubElement(Rotation, 'r11')
            r11.text = self.record1.axes.get_rotation(1, 1, as_string=True)
            r12 = ET.SubElement(Rotation, 'r12')
            r12.text = self.record1.axes.get_rotation(1, 2, as_string=True)
            r13 = ET.SubElement(Rotation, 'r13')
            r13.text = self.record1.axes.get_rotation(1, 3, as_string=True)
            r21 = ET.SubElement(Rotation, 'r21')
            r21.text = self.record1.axes.get_rotation(2, 1, as_string=True)
            r22 = ET.SubElement(Rotation, 'r22')
            r22.text = self.record1.axes.get_rotation(2, 2, as_string=True)
            r23 = ET.SubElement(Rotation, 'r23')
            r23.text = self.record1.axes.get_rotation(2, 3, as_string=True)
            r31 = ET.SubElement(Rotation, 'r31')
            r31.text = self.record1.axes.get_rotation(3, 1, as_string=True)
            r32 = ET.SubElement(Rotation, 'r32')
            r32.text = self.record1.axes.get_rotation(3, 2, as_string=True)
            r33 = ET.SubElement(Rotation, 'r33')
            r33.text = self.record1.axes.get_rotation(3, 3, as_string=True)
        if self.record2 is not None:
            Record2 = ET.SubElement(p, 'Record2')
            Date = ET.SubElement(Record2, 'Date')
            Date.text = self.record2.date
            if self.record2.creator is not None:
                Creator = ET.SubElement(Record2, 'Creator')
                Creator.text = self.record2.creator.decode('utf-8')
            Instrument = ET.SubElement(Record2, 'Instrument')
            Manufacturer = ET.SubElement(Instrument, 'Manufacturer')
            Manufacturer.text = \
                self.record2.instrument.manufacturer.decode('utf-8')
            Model = ET.SubElement(Instrument, 'Model')
            Model.text = self.record2.instrument.model.decode('utf-8')
            Serial = ET.SubElement(Instrument, 'Serial')
            Serial.text = self.record2.instrument.serial
            Version = ET.SubElement(Instrument, 'Version')
            Version.text = self.record2.instrument.version
            CalibrationDate = ET.SubElement(Record2, 'CalibrationDate')
            CalibrationDate.text = self.record2.calibrationdate
            ProbingSystem = ET.SubElement(Record2, 'ProbingSystem')
            Type = ET.SubElement(ProbingSystem, 'Type')
            Type.text = self.record2.probingsystem.type
            Identification = ET.SubElement(ProbingSystem, 'Identification')
            Identification.text = self.record2.probingsystem.identification
            if self.record2.comment is not None:
                Comment = ET.SubElement(Record2, 'Comment')
                Comment.text = self.record2.comment
        Record3 = ET.SubElement(p, 'Record3')
        MatrixDimension = ET.SubElement(Record3, 'MatrixDimension')
        SizeX = ET.SubElement(MatrixDimension, 'SizeX')
        SizeX.text = str(self.record3.matrixdimension.sizeX)
        SizeY = ET.SubElement(MatrixDimension, 'SizeY')
        SizeY.text = str(self.record3.matrixdimension.sizeY)
        SizeZ = ET.SubElement(MatrixDimension, 'SizeZ')
        SizeZ.text = str(self.record3.matrixdimension.sizeZ)
        if self.record3.datalink is not False:
            DataLink = ET.SubElement(Record3, 'DataLink')
            PointDataLink = ET.SubElement(DataLink, 'PointDataLink')
            PointDataLink.text = self.record3.datalink.PointDataLink
            MD5ChecksumPointData = ET.SubElement(DataLink,
                                                 'MD5ChecksumPointData')
            MD5ChecksumPointData.text = \
                self.record3.datalink.MD5ChecksumPointData
            # Check if we have also the valid points link
            if self.record3.datalink.ValidPointsLink is not None:
                ValidPointsLink = ET.SubElement(DataLink, 'ValidPointsLink')
                ValidPointsLink.text = self.record3.datalink.ValidPointsLink
                MD5ChecksumValidPoint = ET.SubElement(DataLink,
                                                      'MD5ChecksumValidPoints')
                MD5ChecksumValidPoint.text = \
                    self.record3.datalink.MD5ChecksumValidPoints
        elif self.record3.datalist is not False:
            DataList = ET.SubElement(Record3, 'DataList')
            for values in self.data.T:
                Datum = ET.SubElement(DataList, 'Datum')
                if not all(np.isnan(values)):
                    Datum.text = ";".join([str(i) for i in values])

        Record4 = ET.SubElement(p, 'Record4')
        ChecksumFile = ET.SubElement(Record4, 'ChecksumFile')
        ChecksumFile.text = self.record4.checksumfile
        #
        xml = ET.tostring(p, encoding='utf-8')
        # MD5 Check sum
        md5 = hashlib.md5(xml).hexdigest() + " *main.xml"
        # WRITING INTO THE ZIP FILE ALL THE DATA
        with zipfile.ZipFile("".join([filepath, '.x3p']), 'w') as zf:
            zf.writestr("md5checksum.hex", md5)
            zf.writestr("main.xml", xml)
            if self.record3.datalink is not False:
                zf.writestr("bindata/data.bin", self.data.data.tobytes())
