import json
import copy
import functools
import maya.cmds as cmds

def createUI(pWindowTitle, pApplyCallback):
    
    windowID = 'jsonifyVertex'
    
    if cmds.window(windowID, exists=True):
        cmds.deleteUI(windowID)
        
    cmds.window(windowID, title=pWindowTitle, sizeable=False, resizeToFitChildren=True)
    
    cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1,75), (2,60), (3,60)], columnOffset= [(1, 'right',3)])
    
    cmds.text(label='Cell Size')
    
    cellSize = cmds.floatField(value=1.2)
    
    cmds.separator(h=10, style='none')
    
    cmds.text(label='Cell Padding')
    
    cellPadding = cmds.floatField(value=0.2)
    
    cmds.separator(h=10, style='none')
    
    cmds.text(label='JSON Path')
    
    jsonPath = cmds.textField()
    
    cmds.separator(h=10, style='none')
    
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    cmds.separator(h=10, style='none')
    
    cmds.separator(h=10, style='none')
    
    cmds.button(label='Apply', command=functools.partial(pApplyCallback, cellSize, cellPadding, jsonPath))
    
    def cancelCallback( *pArgs ):
        if cmds.window(windowID, exists=True):
            cmds.deleteUI(windowID)
            
    cmds.button(label='Cancel', command=cancelCallback)
            
    cmds.showWindow()




def checkSocket(jsonPath, verts, isVertical, cellSize):
    
    #The ID of the socket found
    foundID = "0"
    
    with open(str(jsonPath) + '\sockets.json', 'r') as f:
        sockets = json.load(f)
    
    
    vertsFound = False
    
    for socket in sockets['sockets']:
        #Get a mirrored version of each vert
        mirrorVerts = copy.deepcopy(verts)
        for vert in mirrorVerts:
            vert[0] = vert[0] * -1
            
        #Get each vert rotated 90 degrees
        rotVerts1 = copy.deepcopy(verts)
        for vert1 in rotVerts1:
            vert1[0] = vert[1]
            vert1[1] = vert[0] * -1
            
        #Get each vert rotated 180 degrees
        rotVerts2 = copy.deepcopy(verts)
        for vert2 in rotVerts2:
            vert2[0] = vert[0] * -1
            vert2[1] = vert[1] * -1
            
        #Get each vert rotated 270 degrees
        rotVerts3 = copy.deepcopy(verts)
        for vert3 in rotVerts3:
            vert3[0] = vert[1] * -1
            vert3[1] = vert[0]
            
        verts.sort()
        mirrorVerts.sort()
        rotVerts1.sort()
        rotVerts2.sort()
        rotVerts3.sort()    
            
        #Treat horizontal and vertical sockets differently. Horizontal sockets are based on symmetry. Vertical sockets are based on rotation
        if (isVertical == False and socket["vertical"] == False):
            if (verts == socket["verts"]):
                vertsFound = True
                #Check verts are symmetrical. If so, append an S to the found ID
                if (verts == mirrorVerts and len(verts) > 0):
                    foundID = str(socket["socketID"]) + "s"
                else:
                    foundID = str(socket["socketID"])
            elif (mirrorVerts == socket['verts']):
                #If *only* the mirror is found, append an f to the found ID 
                vertsFound = True
                foundID = str(socket["socketID"]) + "f"
        elif (isVertical == True and socket["vertical"] == True):
            #If the verts are found as they are, append the _0 rotation. 90 degrees is _1. 180 degrees is _2. 270 degrees is _3. If no ending is appended, there are no verts
            if (len(verts) == 0):
                vertsFound = True
                foundID = "1_0"
            elif (verts == socket["verts"]):
                vertsFound = True
                foundID = str(socket["socketID"]) + "_0"
            elif (rotVerts1 == socket["verts"]):
                vertsFound = True
                foundID = str(socket["socketID"]) + "_1"
            elif (rotVerts2 == socket["verts"]):
                vertsFound = True
                foundID = str(socket["socketID"]) + "_2"
            elif (rotVerts3 == socket["verts"]):
                vertsFound = True
                foundID = str(socket["socketID"]) + "_3"
               
            
    #If it's a new combination of verts, create a new socket profile
    if vertsFound == False:
        newID = int(sockets['sockets'][len(sockets['sockets'])-1]["socketID"]) + 1
        sockets['sockets'].append(copy.deepcopy(sockets['sockets'][0]))
        sockets['sockets'][newID]["socketID"] = newID
        sockets['sockets'][newID]["verts"] = verts
        sockets['sockets'][newID]["vertical"] = isVertical
        
        print("Generating new socket ID: " + str(newID) + " - " + str(verts))
        
        #Check verts are symmetrical. If so, append an S to the found ID
        if (isVertical == True):
            #If the verts are found as they are, append the _0 rotation. 90 degrees is _1. 180 degrees is _2. 270 degrees is _3. If no ending is appended, there are no verts
            if (len(verts) == 0):
                foundID = "1_0"
            else:
                foundID = str(newID) + "_0"
        elif (verts == mirrorVerts):
            foundID = str(newID) + "s"
        else:
            foundID = str(newID)
        
    # Serializing json
    json_object = json.dumps(sockets, indent=4)
        
    with open(str(jsonPath) + '\sockets.json', 'w') as f:
        f.write(json_object)
        
    return foundID

def rotateVerticalSocket(currentIndex, rotationIndex):
    splitIndex = currentIndex.split('_')
    currentIndexSocket = int(splitIndex[0])
    currentRotationIndex = int(splitIndex[1])
    
    #if the socket index is 1 (empty), simply return 1_0 with no additional rotation
    if(currentIndexSocket == 1):
        return "1_0"
    else:
        for i in range(rotationIndex):
            currentRotationIndex += 1
            if currentRotationIndex >= 4:
                currentRotationIndex = 0
        return str(currentIndexSocket) + "_" + str(currentRotationIndex)
        
        
        
def checkHorizontalValidity(socketIndex1, socketIndex2):
    
    if(socketIndex1 == "0" and socketIndex2 == "0"):
        return True
    
    lastChar1 = socketIndex1[len(socketIndex1) - 1]
    lastChar2 = socketIndex2[len(socketIndex2) - 1]
    
    if(lastChar1 == 's'):
        if(socketIndex1 == socketIndex2):
            return True
    else:
        if(lastChar1 == 'f' and lastChar1 != lastChar2 and socketIndex1[:-1] == socketIndex2):
            return True
        elif(lastChar2 == 'f' and lastChar1 != lastChar2 and socketIndex1 == socketIndex2[:-1]):
            return True
            
    return False
    
def checkVerticalValidity(socketIndex1, socketIndex2):
    if(socketIndex1 == socketIndex2):
        return True
    

def sortTiles(cellSize, cellPadding, jsonPath):
    
    with open(str(jsonPath) + '\prototypes.json', 'r') as f:
        prototypes = json.load(f)
    
    # Get Shape Selection
    shape = cmds.ls(selection=True, o=True)

    xNegVerts = []
    xPosVerts = []
    yNegVerts = []
    yPosVerts = []
    zNegVerts = []
    zPosVerts = []
    
    xNegSocket = "0"
    xPosSocket = "0"
    yNegSocket = "1_0"
    yPosSocket = "1_0"
    zNegSocket = "0"
    zPosSocket = "0"

    for i in range(len(shape)):
        # Get the total number of verts
        totalVerts = cmds.polyEvaluate(shape[i], vertex=True)
        
        # Get Position Of Each Vert
        for j in range(totalVerts):
            xformPos = cmds.xform(str(shape[i]) + '.vtx[' + str(j) + ']', q=True, worldSpace=True, t=True)
            
            #Process the verts
            xformPos[0] = round(xformPos[0],3)
            xformPos[0] = (xformPos[0] % (cellSize + cellPadding)) - cellSize/2
            xformPos[0] = round(xformPos[0],3)
            
            xformPos[1] = round(xformPos[1],3)
            xformPos[1] = (xformPos[1] % (cellSize + cellPadding)) - cellSize/2
            xformPos[1] = round(xformPos[1],3)
            
            xformPos[2] = round(xformPos[2],3)
            xformPos[2] = (xformPos[2] % (cellSize + cellPadding)) - cellSize/2
            xformPos[2] = round(xformPos[2],3)
            
            #print(shape[i] + ": " + str(j+1) + '. [' + str(xformPos[0]) + ', ' + str(xformPos[1]) + ', ' + str(xformPos[2]) + ']')
            
            #Determine the face the vert is along
            
            if (xformPos[0] == -cellSize/2):
                xNegVerts.append([xformPos[2], xformPos[1]])
                pass
            elif (xformPos[0] == cellSize/2):
                xPosVerts.append([xformPos[2] * -1, xformPos[1]])
                pass
            if (xformPos[1] == -cellSize/2):
                yNegVerts.append([xformPos[0], xformPos[2]])
                pass
            elif (xformPos[1] == cellSize/2):
                yPosVerts.append([xformPos[0], xformPos[2]])
                pass
            if (xformPos[2] == -cellSize/2):
                zNegVerts.append([xformPos[0], xformPos[1]])
                pass
            elif (xformPos[2] == cellSize/2):
                zPosVerts.append([xformPos[0], xformPos[1]])
                pass
                
        print("Analyzing sockets on shape: " + shape[i])
        xNegSocket = checkSocket(jsonPath, xNegVerts, False, cellSize)
        xPosSocket = checkSocket(jsonPath, xPosVerts, False, cellSize)
        yNegSocket = checkSocket(jsonPath, yNegVerts, True, cellSize)
        yPosSocket = checkSocket(jsonPath, yPosVerts, True, cellSize)
        zNegSocket = checkSocket(jsonPath, zNegVerts, False, cellSize)
        zPosSocket = checkSocket(jsonPath, zPosVerts, False, cellSize)
        print("- Complete")
        
        
        
        #rotation 0 
        newPrototype = dict()
        
        print("- Generating prototype: " + shape[i] + "_0")
        newPrototype['prototypeName'] = shape[i] + "_0"
        newPrototype['meshName'] = shape[i]
        newPrototype['meshRotation'] = 0
        newPrototype['negX'] = xNegSocket
        newPrototype['posX'] = xPosSocket
        newPrototype['negY'] = yNegSocket
        newPrototype['posY'] = yPosSocket
        newPrototype['negZ'] = zNegSocket
        newPrototype['posZ'] = zPosSocket
        newPrototype['weight'] = 1
        newPrototype['validNeighbors'] = copy.deepcopy(prototypes["prototypes"][0]["validNeighbors"])
        prototypes['prototypes'].append(newPrototype)
        
        #rotation 1 
        newPrototype = dict()
        
        print("- Generating prototype: " + shape[i] + "_1")
        newPrototype['prototypeName'] = shape[i] + "_1"
        newPrototype['meshName'] = shape[i]
        newPrototype['meshRotation'] = 1
        newPrototype['negX'] = zPosSocket
        newPrototype['posX'] = zNegSocket
        newPrototype['negY'] = rotateVerticalSocket(yNegSocket, 1)
        newPrototype['posY'] = rotateVerticalSocket(yPosSocket, 1)
        newPrototype['negZ'] = xNegSocket
        newPrototype['posZ'] = xPosSocket
        newPrototype['weight'] = 1
        newPrototype['validNeighbors'] = copy.deepcopy(prototypes["prototypes"][0]["validNeighbors"])
        prototypes['prototypes'].append(newPrototype)
        
        #rotation 2 
        newPrototype = dict()
        
        print("- Generating prototype: " + shape[i] + "_2")
        newPrototype['prototypeName'] = shape[i] + "_2"
        newPrototype['meshName'] = shape[i]
        newPrototype['meshRotation'] = 2
        newPrototype['negX'] = xPosSocket
        newPrototype['posX'] = xNegSocket
        newPrototype['negY'] = rotateVerticalSocket(yNegSocket, 2)
        newPrototype['posY'] = rotateVerticalSocket(yPosSocket, 2)
        newPrototype['negZ'] = zPosSocket
        newPrototype['posZ'] = zNegSocket
        newPrototype['weight'] = 1
        newPrototype['validNeighbors'] = copy.deepcopy(prototypes["prototypes"][0]["validNeighbors"])
        prototypes['prototypes'].append(newPrototype)
        
        #rotation 3 
        newPrototype = dict()
        
        print("- Generating prototype: " + shape[i] + "_3")
        newPrototype['prototypeName'] = shape[i] + "_3"
        newPrototype['meshName'] = shape[i]
        newPrototype['meshRotation'] = 3
        newPrototype['negX'] = zNegSocket
        newPrototype['posX'] = zPosSocket
        newPrototype['negY'] = rotateVerticalSocket(yNegSocket, 3)
        newPrototype['posY'] = rotateVerticalSocket(yPosSocket, 3)
        newPrototype['negZ'] = xPosSocket
        newPrototype['posZ'] = xNegSocket
        newPrototype['weight'] = 1
        newPrototype['validNeighbors'] = copy.deepcopy(prototypes["prototypes"][0]["validNeighbors"])
        prototypes['prototypes'].append(newPrototype)
        
        #Clear all of the verts lists and sockets for use in the next shape
        xNegVerts.clear()
        xPosVerts.clear()
        yNegVerts.clear()
        yPosVerts.clear()
        zNegVerts.clear()
        zPosVerts.clear()
        
        xNegSocket = 1
        xPosSocket = 1
        yNegSocket = 0
        yPosSocket = 0
        zNegSocket = 1
        zPosSocket = 1
        
    newPrototype = dict()
        
    newPrototype['prototypeName'] = "air"
    newPrototype['meshName'] = ""
    newPrototype['meshRotation'] = 0
    newPrototype['negX'] = "0"
    newPrototype['posX'] = "0"
    newPrototype['negY'] = "1_0"
    newPrototype['posY'] = "1_0"
    newPrototype['negZ'] = "0"
    newPrototype['posZ'] = "0"
    newPrototype['weight'] = 1
    newPrototype['validNeighbors'] = copy.deepcopy(prototypes["prototypes"][0]["validNeighbors"])
    prototypes['prototypes'].append(newPrototype)
    
    print("Generating neighbor lists")
    
    # All shapes have been added to the prototypes dictionary by this point
    # Fill out valid neighbors
    for prototype in prototypes['prototypes']:
        for comparePrototype in prototypes['prototypes']:
            if(prototype["prototypeName"] != "empty" and comparePrototype["prototypeName"] != "empty"):
                #-x
                if(checkHorizontalValidity(prototype["negX"], comparePrototype["posX"])):
                    prototype["validNeighbors"]["negX"].append(comparePrototype["prototypeName"])
                #+x
                if(checkHorizontalValidity(prototype["posX"], comparePrototype["negX"])):
                    prototype["validNeighbors"]["posX"].append(comparePrototype["prototypeName"])
                #-z
                if(checkHorizontalValidity(prototype["negZ"], comparePrototype["posZ"])):
                    prototype["validNeighbors"]["negZ"].append(comparePrototype["prototypeName"])
                #+z
                if(checkHorizontalValidity(prototype["posZ"], comparePrototype["negZ"])):
                    prototype["validNeighbors"]["posZ"].append(comparePrototype["prototypeName"])
                #-y
                #Check to see if below should only contain air. I'm gonna have to re-write this if I ever want to any geometry with overhangs
                if(prototype["negY"] == "1_0"):
                    prototype["validNeighbors"]["negY"].clear()
                    prototype["validNeighbors"]["negY"].append("air")
                elif(checkVerticalValidity(prototype["negY"], comparePrototype["posY"])):
                    prototype["validNeighbors"]["negY"].append(comparePrototype["prototypeName"])
                #+y
                #Check to see if above should only contain air. I'm gonna have to re-write this if I ever want to any geometry with overhangs
                if(prototype["posY"] == "1_0"):
                    prototype["validNeighbors"]["posY"].clear()
                    prototype["validNeighbors"]["posY"].append("air")
                elif(checkVerticalValidity(prototype["posY"], comparePrototype["negY"])):
                    prototype["validNeighbors"]["posY"].append(comparePrototype["prototypeName"])
        
    # Serializing json
    json_object = json.dumps(prototypes, indent=4)
    
    with open(str(jsonPath) + '\prototypes.json', 'w') as f:
        f.write(json_object)
        
    print("Finished!")
  



def applyCallback(pCellSizeField, pCellPaddingField, pJsonPath, *pArgs):
    
    cellSize = cmds.floatField(pCellSizeField, query=True, value=True)
    cellPadding = cmds.floatField(pCellPaddingField, query=True, value=True)
    jsonPath = cmds.textField(pJsonPath, fileName=True, query=True)
       
    sortTiles(cellSize, cellPadding, jsonPath)
    


createUI('JSON Verts', applyCallback)

