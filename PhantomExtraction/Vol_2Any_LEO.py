### Copy this file into (usually) C:\Users\<name>\fiji.app\plugins\ then open FIJI and select Plugins/Install... in the menu bar
# and select this file.
### Restart FIJI. The plugin should now appear in the Plugins menu.
###
### Select the plugin.
### Select an input folder that contains all the scans you wish to convert.
### The plugin searches for any .vol or .raw files with accompanying .vgi files in that folder.
### Then it loads those files into FIJI, which then exports as either TIFF or BMP, depending on your choice. *It will use this export type every time.
### The image stack is saved into new folder in the scan directory.
###
### code originally written by Dan Sykes, NHM & Peter Swart, Imperial College London.

### modified by Ken Johnson to run on Unix (used os.path.join)
### modified by Leo Bertini to run on a single folder tree with the following format (update Aug 2022)
# --> master folder holding scans
#       -scan 1 \TIFF
#       -scan 2 \TIFF
#       -scan 3 \TIFF
#   it saves each stack inside a TIFF dir for each scan folder

import os
import re
from ij import IJ
from ij.io import DirectoryChooser
from ij.gui import GenericDialog


def start():
    ### gets user input for root directory to search through. Then executes the script on all the folders within that directory.
    import_foldername = DirectoryChooser("Choose a folder").getDirectory()
    ifnBackup = import_foldername;
    if import_foldername is None:
        print("User cancelled the dialog!")
    else:
        print("\nSelected folder:", import_foldername, "\n\n\n")
        # findvols(import_foldername)
        convert_vols(import_foldername)
        # fixvols(import_foldername)


### imageJ macro for rescaling down to 16-bit greyvalue
def contrast_auto_adjust_macro():
    cMacro = """
	Stack.getStatistics(count, mean, min, max, std);
	setMinAndMax(min, max)
	run("16-bit");
	setMinAndMax(0, 65535)
	"""
    return cMacro


### doubles up the backslashes in path for the imageJ macro
def doubleBackslash(path):
    rgMacroString = re.compile("\'.*\'")
    dbsPath = rgMacroString.findall(repr(path))[0][1:-1]
    return dbsPath;


### Finds the raw and vol files then renames them to remove [ ] which causes issues with FIJI.
def findvols(import_foldername):
    for root, dirs, files in os.walk(import_foldername):
        for file in files:
            if file[-4:] == '.raw':
                process_rename(file, root, import_foldername)
            elif file[-4:] == '.vol':
                process_rename(file, root, import_foldername)
            elif file[-4:] == '.txm':
                process_rename(file, root, import_foldername)
            elif file[-4:] == '.vgl':
                process_rename(file, root, import_foldername)
            else:
                pass


### Converts the raw and vol files to image stacks
def convert_vols(import_foldername):
    count = 0
    output = ""
    for root, dirs, files in os.walk(import_foldername):
        for file in files:
            if file[-4:] == '.raw':
                print('file', file)
                print('root', root)
                print('import_foldername', import_foldername)
                count += 1
                # if this is the first file (count = 1) and no output type has been chosen. Then open dialog to get output type. Then export image stack.
                if count == 1 and output == "":
                    output = getType()
                    process_raw(file, root, import_foldername, output)
                # For all other files export an image stack of the type select in dialog beforehand.
                elif count != 1 and output != "":
                    process_raw(file, root, import_foldername, output)
                else:
                    print("Urgh!")
            # same as above but for vol files.
            elif file[-4:] == '.vol':
                count += 1
                if count == 1 and output == "":
                    output = getType()
                    process_vol(file, root, import_foldername, output)
                elif count != 1 and output != "":
                    process_vol(file, root, import_foldername, output)
                else:
                    print("Urgh!")
            else:
                pass


### Undo the rename performed earlier to return directory names to their originals
def fixvols(import_foldername):
    for root, dirs, files in os.walk(import_foldername):
        for file in files:
            if file[-4:] == '.raw':
                process_unname(file, root, import_foldername)
            elif file[-4:] == '.vol':
                process_unname(file, root, import_foldername)
            else:
                pass


### Finds the [ ] and replaces with + $ then renames directory
def process_rename(file, root, import_foldername):
    upOne = os.path.basename(root)
    pathOrig = os.path.normpath(root)[:-len(upOne)]
    filename = pathOrig.replace('[', '+')
    filename = filename.replace(']', '$')
    os.renames(pathOrig, filename)


### Finds the + $ and replaces with [ ] then renames directory
def process_unname(file, root, import_foldername):
    upOne = os.path.basename(root)
    pathOrig = os.path.normpath(root)[:-len(upOne)]
    filename = pathOrig.replace('+', '[')
    filename = filename.replace('$', ']')
    os.renames(pathOrig, filename)


### Run the image stack export of raw files
def process_raw(file, root, import_foldername, output):
    upOne = os.path.basename(root)
    pathOrig = os.path.normpath(root)[:-len(upOne)]
    # extracts x y z sizes from .vgi file
    regex = re.compile('size = ([0-9]*) ([0-9]*) ([0-9]*)')  # define regex to find x y z pixels
    volPath = os.path.join(root, file)
    if any(item.endswith(".vgl") for item in os.listdir(root)):
        vgi = volPath[:-4] + ".vgl"

    if any(item.endswith(".vgi") for item in os.listdir(root)):
        vgi = volPath[:-4] + ".vgi"

    print("File is")
    print(vgi)

    f = open(vgi, 'r')
    line1 = f.readline();
    line2 = f.readline();
    XYZ = f.readline()
    f.close()
    XYZ = regex.findall(XYZ)
    print("XYZ is")
    print(XYZ)
    x, y, z = XYZ[0]
    fName = file[:-4]
    # Run export through FIJI
    if output == "tiff":
        # savePath = pathOrig + "\\TIFF\\" + fName + "_0001.tif"
        savePath = os.path.join(import_foldername, fName, "TIFF")
        print("savePath is " + savePath)
        export(pathOrig, volPath, "16-bit Unsigned", x, y, z, "TIFF", fName, savePath)
    elif output == "bmp":
        savePath = pathOrig + "\\BMP\\" + fName + "_0001.bmp"
        print(savePath)
        export(pathOrig, volPath, "16-bit Unsigned", x, y, z, "BMP", fName, savePath)
    else:
        print("Bugger it!")


def process_vol(file, root, import_foldername, output):
    upOne = os.path.basename(root)
    pathOrig = os.path.normpath(root)[:-len(upOne)]
    # extracts x y z sizes from .vgi file
    regex = re.compile('size = ([0-9]*) ([0-9]*) ([0-9]*)')  # define regex to find x y z pixels
    volPath = os.path.join(root, file)
    vgi = volPath[:-4] + ".vgi"
    f = open(vgi, 'r')
    line1 = f.readline();
    line2 = f.readline();
    XYZ = f.readline()
    f.close()
    XYZ = regex.findall(XYZ)
    x, y, z = XYZ[0]
    fName = file[:-4]
    # Run export through FIJI
    if output == "tiff":
        savePath = os.path.join(import_foldername, fName, "TIFF")
        print("savePath is " + savePath)
        export(pathOrig, volPath, "32-bit Real", x, y, z, "TIFF", fName, savePath)
    elif output == "bmp":
        savePath = pathOrig + "\\BMP\\" + fName + "_0001.bmp"
        print("savePath is " + savePath)
        print(savePath)
        export(pathOrig, volPath, "32-bit Real", x, y, z, "BMP", fName, savePath)
    else:
        print("Bugger it!")


### Dialog box to get user input for file type 
def getType():
    gd = GenericDialog("Type")
    types = ["bmp", "tiff"]  # List of file types available
    gd.addChoice("Output as", types, types[len(types) - 1])
    # gd.addCheckbox("Same for all?", True) 
    gd.showDialog()
    # Error message 
    if gd.wasCanceled():
        print("User cancelled dialog!")
    # Read out the options   
    output = gd.getNextChoice()
    # all = gd.getNextBoolean()
    return output


### Run FIJI macros to import images then export to new folder, this is the main bit!
def export(pathOrig, volPath, type, x, y, z, format, fName, savePath):
    fName = fName + "_"
    print("fName is " + fName + " save Path is " + savePath)
    ###Ken added "use" command to use virtual stack?
    stringImport = """run("Raw...", "open=[""" + doubleBackslash(
        volPath) + """] image=[""" + type + """] width=""" + x + """ height=""" + y + """ offset=0 number=""" + z + """ gap=0 little-endian use");"""
    print("stringImport is " + stringImport)
    stringSaveStack = """run("Image Sequence... ", "format=""" + format + """ name=""" + fName + """ start=1 digits=4 save=[""" + doubleBackslash(
        savePath) + """]");"""
    print("string save is " + stringSaveStack)

    # os.makedirs(savePath)
    if not os.path.exists(savePath):  # Leo Bertini added this line to save folder with images inside scan folder
        os.makedirs(savePath)

    IJ.runMacro(stringImport)
    IJ.runMacro(contrast_auto_adjust_macro())
    IJ.runMacro(stringSaveStack)
    IJ.runMacro("""run("Close");""")
    print("Successfully exported to: \'" + savePath[:-9] + "\'\n\n")


print(start())
