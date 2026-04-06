#This file is going to have all my methods for thresholding
import Constants
import numpy as np
import math

class Threshold:
    def __init__(self, array):
        self.array = array

    #This method thresholds by setting all values above the threshold to the threshold
    def clippingNoKnee(self, threshold : float = None):
        if threshold == None: 
            threshold = Constants.THRESHOLD
        clippedArray = self.array.copy()
        for i in range(len(clippedArray)):
            if clippedArray[i] > threshold:
                clippedArray[i] = threshold
        return clippedArray
    
    #This method thresholds by applying the ratio to every value over the threshold
    def limitingNoKnee(self, threshold : float = None, ratio : float  = None):
        if threshold == None:
            threshold = Constants.THRESHOLD
        if ratio == None:
            ratio = Constants.RATIO
        limitedArray = self.array.copy()

        for i in range(len(limitedArray)):
            if limitedArray[i] > threshold:
                limitedArray[i] = ((limitedArray[i] - threshold) / ratio) + threshold

        return limitedArray
    
    #This function determines whether a value is above, below, or in the knee region of the threshold
    #This function is used in the "divideWithThreshold" function 
    def getRegion(self, val, threshold : float = None, knee : float = None):
        if threshold is None:
            threshold = Constants.THRESHOLD
        if knee is None:
            knee = Constants.KNEE

        if val > threshold + knee:
            return "over"
        elif val < threshold - knee:
            return "under"
        else:
            return "knee"
        
    def divideWithThreshold(self, threshold : float = None, knee : float = None):
        if threshold is None:
            threshold = Constants.THRESHOLD
        if knee is None:
            knee = Constants.KNEE

        segments = []

        current_region = self.getRegion(self.array[0])
        current_segment = [self.array[0]]
        numLists = 1

        for i in range(1, len(self.array)):
            region = self.getRegion(self.array[i])
            if region == current_region:
                current_segment.append(self.array[i])
            else:
                segments.append({"index": numLists, "type": current_region, "values": current_segment})
                numLists += 1
                current_segment = [self.array[i]]
                current_region = region

        #last segment
        segments.append({"index": numLists, "type": current_region, "values": current_segment})

        return segments
        #okay so this method is going to return a dict with the index of the segment, the type of the segment (over, under, knee), and the values in that segment

    #I need to have applied the thresholding to the before and after knee segments before doing this function


    """
    outline of what i need to do for the parabola:

    okay so first im going to get two points, the last point before the knee and the first point after the knee (these are already thresholded)
    - The coordinates are going to be (decibal in, decibal out)

    then i do a change of basis to get these points (a,b) and (c,d) to map to (0,0) and (2,0)
    - I get the matrix that does the transformation from this 

    then i take the second point before the knee and the second point after the knee
    
    I apply the change of basis to get these points in terms of their new coordinate system

    I then do a line (parabola) of best fit to find the parabola of best fit for the knee 
    - there might be a slight discontinuity at the endpoints but bc the points are so close together it should be fine

    Now i have my parabola function 

    I then take the length of the knee list
    - this tells me how many entries i need in my parabola list

    I then take the difference between the two endpoints and divide it by the knee length

    Then I do the first endpoint + ((endpoint1-endpoint2)/kneeLength) * i for i in range(kneeLength) to get the x values for my parabola
    - I then apply the parabola function to these x values to get the y values for my parabola

    Then i apply the inverse change of basis to get these points back in terms of the original coordinate system
    """

    #I need to make a function to turn values into coordinates
    def convertValuesToCoordinates(self, inputVal: float, outputVal: float):
        #The inputVal is the value going in so like the og sound and the output value is the result
        #if the value is under the threshold and knee the inputVal = outputVal
        coordinate = [inputVal, outputVal]

        return coordinate


        #im going to assume that both before and after knee list values need to be thresholded even though one doesnt
        #This function is going to make a parabolic knee region
    def parabolaKnee(self, kneeListIndex : int, kneeListValues : list, beforKneeListPreThresh : list, beforeKneeListPostThresh : list, afterKneeListPreThresh : list, afterKneeListPostThresh : list):
        endpointBefore1 = convertValuesToCoordinates(beforKneeListPreThresh[-1], beforeKneeListPostThresh[-1])
        endpointBefore2 = convertValuesToCoordinates(beforKneeListPreThresh[-2], beforeKneeListPostThresh[-2])
        endpointAfter1 = convertValuesToCoordinates(afterKneeListPreThresh[0], afterKneeListPostThresh[0])
        endpointAfter2 = convertValuesToCoordinates(afterKneeListPreThresh[1], afterKneeListPostThresh[1])

        a = endpointBefore1[0]
        b = endpointBefore1[1]
        c = endpointAfter1[0]
        d = endpointAfter1[1]

        M = np.array([[1, 3], [1, 1]]) @ np.linalg.inv(np.array([[a, c], [b, d]]))

        #transform all 4 points into the new basis
        p1 = M @ np.array([a, b])
        p2 = M @ np.array([c, d])
        p3 = M @ np.array([endpointBefore2[0], endpointBefore2[1]])
        p4 = M @ np.array([endpointAfter2[0], endpointAfter2[1]])

        #fit parabola in transformed space
        coeffs = np.polyfit([p1[0], p2[0], p3[0], p4[0]], [p1[1], p2[1], p3[1], p4[1]], 2)
        coeffA = coeffs[0]
        coeffB = coeffs[1]
        coeffC = coeffs[2]

        #generate x values in transformed space
        kneeLength = len(kneeListValues)
        xValues = [p1[0] + ((p2[0] - p1[0]) / kneeLength) * i for i in range(kneeLength)]
        yValues = [coeffA * x**2 + coeffB * x + coeffC for x in xValues]

        #transform points back to original space
        inverseM = np.linalg.inv(M)
        parabolaPoints = [inverseM @ np.array([xValues[i], yValues[i]]) for i in range(kneeLength)]

        #return just the y values of the parabola points
        return [point[1] for point in parabolaPoints]

    #This function is going to make the knee linear

    def linearKnee(self, kneeListIndex : int, kneeListValues : list, beforKneeListPreThresh : list, beforeKneeListPostThresh : list, afterKneeListPreThresh : list, afterKneeListPostThresh : list):
        #get two points
        endpointBefore = convertValuesToCoordinates(beforKneeListPreThresh[-1], beforeKneeListPostThresh[-1])
        endpointAfter = convertValuesToCoordinates(afterKneeListPreThresh[0], afterKneeListPostThresh[0])

        #y-y1 = m(x-x1)
        #m = (y - y1/x - x1)
        #y = m(x-x1) + y1

        slope = (endpointBefore[1]-endpointAfter[1])/(endpointBefore[0] - endpointAfter[0])

        #generate x values
        kneeLength = len(kneeListValues)

        xValues = [endpointBefore[0] + ((endpointAfter[0] - endpointBefore[0]) / kneeLength) * i for i in range(kneeLength)]
        yValues = [(slope * (endpointBefore[0] - x)) + endpointBefore[1] for x in xValues]

        return yValues

        

    #This function is going to just take every item in the knee and clip it in sections

    '''
    What this function needs to do:
    take in list of sounds
    take in number of sections
    take in the lowest value above the knee
    take in the highest value below the knee

    function should find lowest sound in list
    function should find the highest sound in the list

    figure out how wide each section should be: 
        sectionWidth = (highest sound - lowest sound)/number of sections

    valueWidth = (valAboveKnee - valBelowKnee)/numSections
    
    clippedValue = []

    for i in numBins:
        clippedValue[i] = valBelowKnee + (i * valueWidth) + valueWidth/2

    figure out which bin everything belongs in -> 

    for sound in list: 
        binNumber = ceiling((sound - lowest sound)/sectionWidth)

        binNumber = min(binNumber, number of sections)

        sound = clippedValue[binNumber]

    return list of sounds

    '''

    def clipKneeBySection(self, kneeList, beforeKneeList, AfterKneeList, numSections=None):
        valAboveKnee = max(beforeKneeList[0], AfterKneeList[0])
        valBelowKnee = min(beforeKneeList[-1], AfterKneeList[-1])

        if numSections is None:
            numSections = Constants.NUMSECTIONS

        lowestSound = min(kneeList)
        highestSound = max(kneeList)

        sectionWidth = (highestSound - lowestSound) / numSections
        valueWidth = (valAboveKnee - valBelowKnee) / numSections

        clippedValues = [valBelowKnee + (i * valueWidth) + valueWidth / 2 for i in range(numSections)]

        result = kneeList.copy()
        for i in range(len(result)):
            binNumber = min(math.ceil((result[i] - lowestSound) / sectionWidth), numSections - 1)
            result[i] = clippedValues[binNumber]

        return result







    

