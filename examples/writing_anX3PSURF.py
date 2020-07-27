from x3p import X3Pfile
import numpy as np
import hashlib 
# We create an empty data structure
anx3pfile = X3Pfile()
anx3pfile.set_VendorSpecificID =  "https://github.com/giacomomarchioro/pyx3p"
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
mask = np.zeros(sin2d.shape)
# we mask the forth, fifth and sixth row
mask[[3,4,5],:] = 1
data = np.ma.masked_array(sin2d, mask=mask)
anx3pfile.set_data(data)
anx3pfile.write('mytest2')