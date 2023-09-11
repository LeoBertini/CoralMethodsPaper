'''
2017-07-26
2017-09-22
2017-09-27
2019-01-17
2019-11-14 #Fiji Core Data
2021-August Only Process folders which haven't been handled yet  - Leo Mod
2021-December : when importing voxel size from metadata , make sure all decimals are included when converting from str to float
'''

import numpy as np
import cv2
from scipy.spatial.distance import cdist
import re
import os


def trimFileExtension(fname):  # note this is also in metadata_extract.py
    p = re.compile('\.(tif{1,2}|jpg|jpeg|csv|txt|raw|txm)$')
    return p.sub('', fname)


# 2017-09-22
def drawResults(img, standCenter, standRadius, circles, insertShrink=None, noiseExpand=None,
                realStandRadius=None):  # code for visualisation
    if insertShrink != None:  # shrink circles to show region used to extract gray
        circles[0][:, 2] = circles[0][:, 2] - circles[0][:, 2] * insertShrink
    if np.all(realStandRadius != None):  # show standard with "real" radius, not fit radius
        standRadius = np.mean(realStandRadius)  # the radius is a range - find average only
        standRadius = standRadius.astype("int16")
    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # make it color
    cv2.circle(cimg, (standCenter[0], standCenter[1]), standRadius, (0, 255, 0), 2)  # put the standard in
    if noiseExpand != None:  # draw the region used to find noise value - based on read diameter of standard
        for expand in noiseExpand:
            cv2.circle(cimg, (standCenter[0], standCenter[1]), int(standRadius + standRadius * expand), (0, 128, 255),
                       2)
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)  # draw the insets
        cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)  # draw the center of the circle
    return (cimg)


# 2017-05-23
def get_next_slice(fnames, status, qState):
    # qState= {"state": "S", "side":("T","B"),"run":0,"faillength":10} #parameters for running the slice queue
    # Swap until a hit then hold
    # if in a hold, keep going until faillength fails and then quit.
    if status == "OK":
        if qState["state"] == "S":
            qState["state"] = "H"  # switch to holding
        else:  # reset run if already holding
            qState["run"] = 0
    else:  # standard not found
        if qState["state"] == "S":  # swap sides
            qState["side"] = [qState["side"][1], qState["side"][0]]
        else:
            qState["run"] = qState["run"] + 1  # one more failed in run
    # get results
    if len(fnames) == 0 or qState["run"] > qState["faillength"]:  # quit trying
        qState["state"] = "K"
        out = ""
    else:
        if qState["side"][0] == "T":
            out = fnames.pop(0)
        else:
            out = fnames.pop()
    return out, fnames, qState


# 2017-07-24
# first remove all circles that are too close to the center or perimeter of the standard
# then merge circles that have lots of overlap
def cleanCircles(circles, insertTolerance, standCenter, standRadius, standardShrink):
    if circles is not None and circles.shape[1] > insertTolerance['minnum'] - 1:
        shrunkRange = (standRadius * standardShrink, standRadius * (1 - standardShrink))
        xy = circles[0][:, 0:2]
        dist = cdist([standCenter], xy)
        a = dist < shrunkRange[1]
        b = dist > shrunkRange[0]
        keep = a & b
        if np.any(keep):
            circles = np.array([circles[0, keep[0]]])
            return circles
        else:
            return None
    return None


# 2017-06-27
# merge circles that are strongly overlapping
# DEBUG - set number of circles to 6 or 7 and see if multiple merges works !
def mergeCircles(circles, merged, insertTolerance):
    xy = circles[0, :, 0:2]
    mradius = np.median(circles[0, :, 2])
    tolerance = mradius * insertTolerance["overlap"]
    dist = cdist(xy, xy)
    ind = np.triu_indices(dist.shape[0])  # fill upper triangle with numbers higher than tolerance
    dist[ind] = tolerance
    tooclose = np.where(dist < tolerance)
    if len(tooclose[0]) == 1:
        ind = np.sort([tooclose[0][0], tooclose[1][0]])
        tomerge = circles[:, ind]
        tomerge = np.mean(tomerge, axis=1)
        circles[:, ind[0]] = tomerge  # replace row of first element in index
        circles = np.delete(circles, ind[1:], axis=1)  # delete remaining rows
        merged[ind[0]] = 1  # merged cell gets a found code of 1
        merged = np.delete(merged, ind[1])  # deleted entry for merged circle
    return circles, merged


# 2017-06-27
# new version that uses center of standard and might get 4 spots only ?
def checkCircles(circles, insertTolerance,
                 standCenter):  # are they all equally distant from the centroid and at the correct angle?
    ok = False
    comment = ""
    found = np.zeros(circles.shape[1])
    if insertTolerance["overlap"] > 0:
        circles, found = mergeCircles(circles, found, insertTolerance)
    xy = circles[0][:, 0:2]
    dist = cdist([standCenter], xy)
    deviation = np.ptp(dist) / np.mean(dist)
    if deviation < insertTolerance["dist"]:
        xy = xy - standCenter  # calculate all angles for circles from x axis (0,1) and the sort and find differences - they should be 72
        xaxis = np.array([100, 0])
        angles = np.empty(xy.shape[0], dtype="float32")
        for i in np.arange(xy.shape[0]):
            cent = xy[i]
            angles[i] = np.math.atan2(np.linalg.det([cent, xaxis]), np.dot(cent, xaxis))
            angles[i] = np.degrees(angles[i])
            if (angles[i] < 0):
                angles[i] = angles[i] + 360
        sortorder = np.argsort(angles)
        angles = angles[sortorder]
        deviation = np.fabs(np.diff(angles))
        # add deviation from last back to first
        deviation = np.append(deviation, [angles[0] + 360 - angles[-1]])
        nfound = circles.shape[1]
        if nfound == 5:  # if 5 circles all differences should be 72
            deviation = np.absolute(deviation - 72)
            if np.max(deviation) < insertTolerance["angle"]:
                ok = True
            else:
                comment = "angles between inserts not within tolerance"
        elif nfound == 4:  # if only 4 circles 1 should be 144 and 3 should be 72
            deviation2 = np.sort(deviation)
            deviation2[:3] = np.absolute(deviation2[:3] - 72)
            deviation2[-1] = np.absolute(deviation2[-1] - 144)
            if np.max(deviation2) < insertTolerance["angle"]:  # model position and size of 5th circle if only 4 found
                circles = np.array([circles[0, sortorder]])  # put in same order as angles
                dist = np.array([dist[0, sortorder]])
                index = np.argmax(deviation)
                if index == 0 | index == 3:
                    abpoints = np.array([0, 3])
                else:
                    abpoints = np.array([index - 1, index])
                # new diameter average of all others
                newdiameter = np.mean(circles[0, :, 2])
                # get coordinates of center of new circle
                newangle = angles[index] + deviation[index] / 2
                newangle = np.radians(newangle)
                newlength = np.mean(dist[0, abpoints])
                # note - the sin(newangle) is negative but we want to add it to standcenter not subtract it !
                newcircle = np.array(
                    [newlength * np.cos(newangle) + standCenter[0], standCenter[1] - newlength * np.sin(newangle),
                     newdiameter])
                circles = np.concatenate((circles[0,], [newcircle]), axis=0)
                circles = np.array([circles])
                found = np.concatenate((found, np.array([2])))  # modelled insert has code 2
                ok = True
            else:
                comment = "4 circles found, but 5th could not be modelled"
        else:
            comment = "4 or 5 inserts not found"
    else:
        comment = "distance between inserts and standard center not within tolerance"
    if ok:
        newcircle = np.mean(circles[0], axis=0)  # add another circle at the center
        circles = np.array([np.concatenate([circles[0,], [newcircle]], axis=0)])
        found = np.concatenate((found, np.array([3])))  # center has a code of 3
        circles = [circles, found]
        return circles, ""
    else:
        return None, comment


# 2017-07-25
def summaryCircles(imgname, circles,
                   shrink):  # get the average grey inside circles - and also averages for whatever is outside of standard frame
    found = circles[1]
    circles = circles[0]
    img = cv2.imread(imgname, -1)  # open as 16bit image
    gray = np.empty(circles.shape[1], dtype="int")
    circles[0][:, 2] = circles[0][:, 2] - circles[0][:, 2] * shrink
    circles = np.uint16(np.around(circles))
    for i in np.arange(circles.shape[1]):
        circle = circles[0, i, :]
        mask = np.zeros(img.shape, np.uint8)
        cv2.circle(mask, (circle[0], circle[1]), circle[2], 1, -1, 8, 0)
        maskimg = cv2.bitwise_and(img, img, mask=mask)
        gray[i] = np.mean(maskimg[maskimg > 0])
    gray = np.concatenate((circles[0], np.array([gray]).T), axis=1)
    gray = np.concatenate((gray, np.array([found]).T), axis=1)
    cells = gray[gray[:5, 3].argsort(-1)[::-1]]  # sort the cells (not the center) by grey from highest to lowest
    gray = np.vstack((cells, gray[5,]))
    return gray


# 2017-09-25
def getNoise(imgname, standCenter, standardRadius,
             noiseExpand):  # get the average grey ring just outsid the standard -use the real size of standard
    standardRadius = np.mean(standardRadius)  # the radius is a range - find average only
    standardRadius = standardRadius.astype("int16")
    img = cv2.imread(imgname, -1)
    mask = np.ones(img.shape, img.dtype)  # remove everything inside the standard
    mask = cv2.circle(mask, tuple(standCenter), int(standardRadius + standardRadius * noiseExpand[0]), 0, thickness=-1)
    img = img * mask
    mask = np.zeros(img.shape, img.dtype)  # remove everything outside
    mask = cv2.circle(mask, tuple(standCenter), int(standardRadius + standardRadius * noiseExpand[1]), 1, thickness=-1)
    img = img * mask
    # cv2.imwrite("outerring.tif",img)
    img = img[np.nonzero(img)]
    noise = [np.mean(img), np.std(img)]
    return noise


# 2017-07-25
def getStandardFrame(img, frameRadius, frameCutoff):  # get the standard outer frame
    coltable = np.histogram(img, 10)  # first remove most common gray values (up to frameCutoff)
    ind = coltable[0].argsort()[::-1]  # sort by frequency
    freq = coltable[0][ind]
    gray = coltable[1][ind]
    csums = np.cumsum(freq) / np.sum(freq)
    for cutoff in frameCutoff:
        ind = np.min(np.where(csums > cutoff))
        threshrange = np.array([gray[ind], np.max(img)], dtype="int64")
        ret, thresh = cv2.threshold(img, threshrange[0], 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # pdb.set_trace()
        # show the results for debugging
        # cimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR) #make it color
        # cv2.drawContours(cimg, contours, -1, (0,255,0), 3)
        # cv2.imwrite("findingstand_"+re.sub(r'\.','',str(cutoff))+".tif",cimg)
        areaRange = frameRadius ** 2 * np.pi
        keep = []
        for cnt in contours:  # only keep contours that are approximately circular and the correct size
            area = cv2.contourArea(cnt)
            if area > areaRange[0] and area < areaRange[1]:
                keep.append(cnt)
        if len(keep) == 1:  # there should only be one result
            keep = keep[0]
            standCenter, standRadius = cv2.minEnclosingCircle(keep)
            standCenter = np.uint16(standCenter)
            standRadius = np.uint16(standRadius)
            mask = np.zeros(img.shape, np.uint8)  # keep only the standard
            mask = cv2.drawContours(mask, [keep], -1, 1, -1)
            standimg = img * (mask.astype(img.dtype))
            return standCenter, standRadius, standimg, cutoff
            break
    return 0, 0, 0, 0


# get the ScanVoxelSize
# 2019-11-14 different fileformats
def getScanVoxelSize(infile, fileformat):
    metadata = np.genfromtxt(infile, delimiter='\t', dtype=None, encoding="UTF-8")  # leo changed it to tab delimited
    keys = [line.split(',')[0] for line in metadata[1:]]
    # keys = keys.astype("str")
    vsize = None
    if fileformat == "metadata_extract":
        vsize = metadata[1:, 2]
    if fileformat == "landmarks":
        vsize = metadata[1:, 1]
    if fileformat == 'Raw_volume_leo_avizo':
        print('file Leo Avizo')
        vsize = [line.split(',')[5] for line in metadata[1:]]

    vsize = [float(format(float(item),'.7f')) for item in vsize] #get float number with 7 decimal places
    voxelsize = dict(zip(keys[0:], vsize[0:]))
    return voxelsize


# return a list of directories in the given directory
def getDirectories(topdir):  # leo modified this in 2021 to only process scans that have not been touched yet
    dirs = []
    ignore = []
    selected_dirs = []
    target_name = "standard_calibration_results.csv"

    for path, subdirs, files in os.walk(topdir):
        for name in files:
            if name == target_name and os.path.getsize(os.path.join(path, name)) != 0:
                print(f"Found calibration results in {os.path.join(path, name)}")
                print(f"The following directory will be ignored")
                print(f"{os.path.dirname(path)} \n")
                ignore.append(os.path.dirname(path))
                continue

        dirs.append(subdirs)

    for item in dirs[0]:
        if os.path.join(topdir, item) not in ignore:
            selected_dirs.append(item)

    return selected_dirs

    #
    # dirs = []
    # files = os.listdir(topdir)
    # for f in files:
    #     if os.path.isdir(os.path.join(topdir, f)):
    #         dirs = dirs + [f]
    #


# 2017-07-26


def process_a_slice(fname, scanname, standardRadius, standardShrink, frameCutoff, param1, param2range, blursize,
                    insertTolerance, scancheckdir, indir, insertShrink, noiseExpand):
    # a kludge to work on "binned" stacks - open them as 16 bit if max value < 200
    img = cv2.imread(os.path.join(indir, fname), -1)  # open as-is image
    if np.amax(img) < 255:  # this is binned
        img = np.uint8(img)  # convert to uint8
    else:
        img = cv2.imread(os.path.join(indir, fname), 0)  # open as 8bit image
    img = cv2.medianBlur(img, blursize)
    status = "Frame Not Found"
    insertdiagnostics = ""

    standCenter, standRadius, standimg, cutoff = getStandardFrame(img, standardRadius[:, 0], frameCutoff)

    if standRadius > 0:  # found the frame
        status = "Standards Not Found"
        insertdiagnostics = ""
        cannyc = cv2.Canny(standimg, 2, 6)
        param2 = param2range[0]
        while param2 < param2range[1]:
            # print ("param2 is " + str(param2))
            circles = cv2.HoughCircles(cannyc, cv2.HOUGH_GRADIENT, 1, 20, param1=param1, param2=param2,
                                       minRadius=standardRadius[0, 1], maxRadius=standardRadius[1, 1])
            circles = cleanCircles(circles, insertTolerance, standCenter, standRadius, standardShrink)
            if circles is not None:
                okcircles, insertdiagnostics = checkCircles(circles, insertTolerance, standCenter)
                if okcircles is not None:  # keep the grey values
                    gray = summaryCircles(os.path.join(indir, fname), okcircles, insertShrink)
                    noise = getNoise(os.path.join(indir, fname), standCenter, standardRadius[:, 0], noiseExpand)
                    status = "OK"
                    break
                else:  # save the image for checking even though circles no good.
                    status = "Some Circles Found"
                    somecircles = circles
            param2 = param2 + param2range[2]

    outtext = [scanname, trimFileExtension(fname), status, cutoff, insertdiagnostics]
    outfile = re.sub(r'\.tif{1,2}', '', fname)

    if status == "OK":  # save the grays and circles
        outtext = outtext + noise + gray.flatten().tolist()
        cimg = drawResults(img, standCenter, standRadius, okcircles[0], insertShrink=insertShrink,
                           noiseExpand=noiseExpand, realStandRadius=standardRadius[:, 0])
        cv2.imwrite(os.path.join(scancheckdir, outfile + "_circles.tif"), cimg)
    elif status == "Standards Not Found":  # save the mask of the standard frame
        cv2.imwrite(os.path.join(scancheckdir, outfile + "_frame.tif"), standimg)
    elif status == "Some Circles Found":  # save the most recently found circles even if they were not ok
        cimg = drawResults(img, standCenter, standRadius, somecircles)
        cv2.imwrite(os.path.join(scancheckdir, outfile + "_badcircles.tif"), cimg)
    else:  # save the original (actually the blurred) file
        cv2.imwrite(os.path.join(scancheckdir, outfile + "_noframe.tif"), img)
    return status, outtext
