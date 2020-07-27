import os 
from x3p import X3Pfile
import matplotlib.pyplot as plt
# visit : https://sourceforge.net/projects/open-gps/files/Sample-Files/
# substitute this path with the path were the samples file have been downoladed
samplesfiles_path = r'/Users/giacomo/Desktop/20110630_X3PSampleFiles_NanoFocus/'
files = [i for i in os.listdir(samplesfiles_path) if i.endswith('.x3p')]
x3pobjs = dict()
errors = []
for i in files:
    print("Importing %s" %i)
    try:
        x3pobjs[i] = X3Pfile(os.path.join(samplesfiles_path,i))
    except ValueError:
        print('Error reading %s' %i)
        errors.append(i)


for filen in x3pobjs:
    if len(x3pobjs[filen].data.shape) > 2:
        axest = x3pobjs[filen].record1.axes.get_XYaxes_types()
        if axest == ['I','I']:
            for i in range(x3pobjs[filen].data.shape[0]):
                plt.imshow(x3pobjs[filen].data[i,:,:])
                plt.title(" %s layer %s" %(filen,i+1))
                plt.show()
        else:
            plt.imshow(x3pobjs[filen].data[0,:,:])
            plt.title(filen)
    else:
        plt.imshow(x3pobjs[filen].data)
        plt.title(filen)
        plt.show()