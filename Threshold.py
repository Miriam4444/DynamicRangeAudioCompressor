#This file is going to have all my methods for thresholding
import Constants
import numpy as np

class Threshold:
    def __init__(self, array):
        self.array = array

    #This method thresholds by setting all values above the threshold to the threshold
    def clippingNoKnee(self, threshold = None):
        if threshold == None: 
            threshold = Constants.THRESHOLD
        clippedArray = self.array.copy()
        for i in range(len(clippedArray)):
            if clippedArray[i] > threshold:
                clippedArray[i] = threshold
        return clippedArray
    
    #This method thresholds by applying the ratio to every value over the threshold
    def limitingNoKnee(self, threshold = None, ratio = None):
        if threshold == None:
            threshold = Constants.THRESHOLD
        if ratio == None:
            ratio = Constants.RATIO
        limitedArray = self.array.copy()

        for sound in limitedArray:
            if sound > threshold:
                sound = ((sound - threshold) / ratio) + threshold

        return limitedArray
    
    #This function determines whether a value is above, below, or in the knee region of the threshold
    #This function is used in the "divideWithThreshold" function 
    def getRegion(val, threshold = None, knee = None):
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
        
    def divideWithThreshold(self, threshold=None, knee=None):
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
        #This function is going to make a parabolic knee region
    def parabolaKnee(self, kneeListIndex, kneeListValues, beforKneeList, afterKneeList):
        endpointBefore1 = beforKneeList[-1]
        endpointBefore2 = beforKneeList[-2]
        endpointAfter1 = afterKneeList[0]
        endpointAfter2 = afterKneeList[1]

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
