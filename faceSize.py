def getBoxArea(aBox): # actually rectangle not box
    return (aBox[1] - aBox[3]) * (aBox[2] - aBox[0])


def getBiggestBoxInList(allBoxes): # returns box in array
    if len(allBoxes) == 0:
        return allBoxes
    elif len(allBoxes) == 1:
        return allBoxes
    biggestBoxInAList = []
    currentBiggest = allBoxes[0]
    currentBiggestArea = getBoxArea(currentBiggest)
    for i in range(1, len(allBoxes)):
        areaOfABox = getBoxArea(allBoxes[i])
        if currentBiggestArea < areaOfABox:
            currentBiggestArea = areaOfABox
            currentBiggest = allBoxes[i]
    biggestBoxInAList.append(currentBiggest)
    return biggestBoxInAList