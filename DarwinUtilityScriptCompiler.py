from ast import Num
from hashlib import new
from operator import contains


ErrorMsg = ""
variables = {}
arrays = {}
arraySize = {}
sFunLocalVariables = {}
sFunLocalArrays = {}
activeFunctions = ""
resolvableIDs = []
sFunNames = []
locId = {}
ifIdCounter = 0
loopIdCounter = 0

def splitStr(Str:str):
    global ErrorMsg
    splited = []
    word = ""
    index = 0
    openBrackets = 0
    while index < len(Str):
        i = Str[index]
        if i == "(":
            openBrackets += 1
        elif i == ")":
            if openBrackets == 0:
                ErrorMsg = "Unintented \")\" symbol"
                print("Error")
                return
            openBrackets -= 1

        if openBrackets > 0:
            word = word + i
        
        if openBrackets > 0:
            pass
        elif i == " ":
            if word != "":
                splited.append(word.strip())
                word = ""
        elif isSplitable(i):
            if word != "":
                splited.append(word.strip())
                word = ""
            splited.append(i)
        else: word = word + i
        index += 1
        
    if word != "": splited.append(word.strip())

    return splited

def isSplitable(i):
    splitables = []
    for j in splitables:
        if i == j:
            return True
    return False

def isVarNameValid(varName):
    invalidNames = [
        "set",
        "var",
        "if",
        "loop",
        "call",
        "return"
    ]
    validCharacters = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if len(varName) <= 0: return False
    if varName in invalidNames: return False
    for character in varName:
        if not character in validCharacters: return False
    if varName[0] in "0123456789": return False
    return True

def extractVariableDetails(word:str):
    vName = ""
    i = 0

    while(i < len(word)):
        if word[i] == "[":
            i += 1
            arrSize = 0
            while (i < len(word)):
                if word[i] == "]":
                    if i+1 == len(word): return {
                        "Name": vName,
                        "Array": True,
                        "Size": arrSize
                    }
                    else: return None
                if not word[i] in "0123456789": return None
                arrSize = arrSize*10 + int(word[i])
                i += 1
            return None
        vName = vName+word[i]
        i += 1
    
    return {
        "Name": vName,
        "Array": False,
        "Size": 0
    }

def var_GenerateBin(newVars: list, BinList:list):
    global ErrorMsg
    BinList.append("JMP 0 0")
    changable = len(BinList)
    BinList.append("DT 0 0")
    newVars.pop(0)
    for newVar in newVars:
        VarDetails = extractVariableDetails(newVar)

        if VarDetails == None:
            ErrorMsg = "Syntax error: \""+newVar+"\""
            return
        if not isVarNameValid(VarDetails["Name"]):
            ErrorMsg = "Invalid varriable name: \""+VarDetails["Name"]+"\""
            return
        
        if VarDetails["Array"]:
            if VarDetails["Size"] <= 0:
                ErrorMsg = "Invalid Array size: \""+VarDetails["Size"]+"\""
                return

            BinList.append("DT 0 "+str(VarDetails["Size"]))

            arrays[VarDetails["Name"]] = str(len(BinList))
            arraySize[VarDetails["Name"]] = VarDetails["Size"]

            for i in range(VarDetails["Size"]): BinList.append("DT 0 0")
        else:
            variables[VarDetails["Name"]] = str(len(BinList))
            BinList.append("DT 0 0")
    
    BinList[changable] = "DT 0 "+str(len(BinList))

def isVariable(varName: str):
    if varName in variables: return True
    if varName in sFunLocalVariables: return True
    if varName in arrays: return True
    if varName in sFunLocalArrays: return True
    return False

def set_GenerateBin(InstructionSet: list, offset:int, BinList:list):
    global ErrorMsg

    #Retriving parameters
    p1 = extractVariableDetails(InstructionSet[offset])
    p2 = extractVariableDetails(InstructionSet[offset+1])
    p3 = {"Name":"", "Array": False, "Size": 0}

    if p2 == "add":
        if len(InstructionSet) == offset+2:
            p2 = p1
            p3 = {
                "Name": "1",
                "Array": False,
                "Size": 0
            }
        elif len(InstructionSet) == offset+3:
            p2 = p1
            p3 = extractVariableDetails(InstructionSet[offset+2])
        else:
            p2 = extractVariableDetails(InstructionSet[offset+2])
            p3 = extractVariableDetails(InstructionSet[offset+3])
    
    #BinGeneration:
    #p1

    p1_isPointer = False
    
    if p1["Name"][0] == "*":
        p1["Name"] = p1["Name"].replace("*", "")
        p1_isPointer = True
    
    if not isVariable(p1["Name"]):
        ErrorMsg = "No such variable Found: "+p1["Name"]
        return
        
    BinList.append("DATA 0 0")
    if p1["Name"] in variables: BinList.append("DT 0 "+variables[p1["Name"]])
    elif p1["Name"] in sFunLocalVariables: BinList.append("DT 0 "+sFunLocalVariables[p1["Name"]])
    elif p1["Name"] in arrays: BinList.append("DT 0 "+str(int(arrays[p1["Name"]])+p1["Size"]))
    else: BinList.append("DT 0 "+str(int(sFunLocalArrays[p1["Name"]])+p1["Size"]))
     
    if p1_isPointer: BinList.append("LD 0 0")


    #p2 Analysis
    p2_isVar = True
    p2_isPointer = False
    p2_isNegated = False

    if p2["Name"][0] == "-":
        p2["Name"] = p2["Name"].replace("-", "")
        p2_isNegated = True
    
    if p2["Name"][0] == "*":
        p2["Name"] = p2["Name"].replace("*", "")
        p2_isPointer = True
    
    if p2["Name"].isdigit(): p2_isVar = False
    elif not isVariable(p2["Name"]):
        ErrorMsg = "No such variable :"+p2["Name"]
        return
    
    #p3 Analysis
    p3_isVar = True
    p3_isPointer = False
    p3_isNegated = False
    
    if p3["Name"] != "":
        if p3["Name"][0] == "-":
            p3["Name"] = p3["Name"].replace("-", "")
            p3_isNegated = True
    
        if p3["Name"][0] == "*":
            p3["Name"] = p3["Name"].replace("*", "")
            p3_isPointer = True

        if p3.isdigit(): p3_isVar = False
        elif not isVariable(p3["Name"]):
            ErrorMsg = "No such variable :"+p3["Name"]
            return

    #BinGeneration
    BinList.append("DATA 0 1")
    if p2_isVar:
        if p2["Array"]:
            if p1["Name"] in arrays: BinList.append("DT 0 "+str(int(arrays[p2["Name"]])+p2["Size"]))
            else: BinList.append("DT 0 "+str(int(sFunLocalArrays[p2["Name"]])+p2["Size"]))
        else:
            if p1["Name"] in variables: BinList.append("DT 0 "+variables[p2["Name"]])
            else: BinList.append("DT 0 "+sFunLocalVariables[p2["Name"]])
        BinList.append("LD 1 1")
    else: BinList.append("DT 0 "+p2["Name"])

    if p2_isPointer: BinList.append("LD 1 1")
    if p2_isNegated:
        BinList.append("DATA 0 3")
        BinList.append("DT 0 1")
        BinList.append("NOT 1 1")
        BinList.append("ADD 3 1")
        BinList.append("FLG 0 0")
    
    if p3["Name"] != "":
        BinList.append("DATA 0 2")
        if p3_isVar:
            if p3["Array"]:
                if p3["Name"] in arrays: BinList.append("DT 0 "+str(int(arrays[p3["Name"]])+p3["Size"]))
                else: BinList.append("DT 0 "+str(int(sFunLocalArrays[p3["Name"]])+p3["Size"]))
            else:
                if p3["Name"] in variables: BinList.append("DT 0 "+variables[p3["Name"]])
                else: BinList.append("DT 0 "+sFunLocalVariables[p3["Name"]])
            BinList.append("LD 2 2")
        else: BinList.append("DT 0 "+p3["Name"])
        if p3_isPointer: BinList.append("LD 2 2")
        if p3_isNegated:
            BinList.append("DATA 0 3")
            BinList.append("DT 0 1")
            BinList.append("NOT 2 2")
            BinList.append("ADD 3 2")
            BinList.append("FLG 0 0")
        BinList.append("ADD 2 1")
        BinList.append("FLG 0 0")
    
    BinList.append("ST 0 1")


def condition_GenerateBin(InstructionSet: list, offset:int, BinList:list, Id:str):
    global ErrorMsg
    rt_offset = offset
    if InstructionSet[offset] == "(":
        rt_offset = condition_GenerateBin(InstructionSet, rt_offset+1, BinList, Id)
    else:
        #Values Are Loaded
        BinList.append("DATA 0 0")
        if str(InstructionSet[rt_offset]).isdigit(): BinList.append("DT 0 "+InstructionSet[rt_offset])
        elif InstructionSet[rt_offset] in variables:
            BinList.append("DT 0 "+str(variables[InstructionSet[rt_offset]]))
            BinList.append("LD 0 0")
        else: ErrorMsg = "No such variable: "+InstructionSet[rt_offset]
        BinList.append("DATA 0 1")
        if str(InstructionSet[rt_offset+2]).isdigit(): BinList.append("DT 0 "+InstructionSet[rt_offset+2])
        elif InstructionSet[rt_offset+2] in variables:
            BinList.append("DT 0 "+str(variables[InstructionSet[rt_offset+2]]))
            BinList.append("LD 1 1")
        else: ErrorMsg = "No such variable: "+InstructionSet[rt_offset+2]
        
        if InstructionSet[rt_offset+1] == "-gt" or InstructionSet[rt_offset+1] == "-lt" or InstructionSet[rt_offset+1] == "-eq":
            #CPM command to determine whether it is lt or gt only
            if InstructionSet[rt_offset+1] == "-gt": BinList.append("CMP 0 1")
            else: BinList.append("CMP 1 0")

            #JMPIF command to determine whether it is -eq or not
            if InstructionSet[rt_offset+1] == "-eq": BinList.append("JMPIF 0 E ")
            else: BinList.append("JMPIF 0 A")
            BinList.append("DT 0 "+str(len(BinList)+3))

            #Tale of if command for else jump
            BinList.append("JMP 0 0")
            BinList.append("DT 0 "+Id+"end")
        elif InstructionSet[rt_offset+1] == "-ge" or InstructionSet[rt_offset+1] == "-le":
            ##CPM command to determine whether it is lt or gt only
            if InstructionSet[rt_offset+1] == "-ge": BinList.append("CMP 0 1")
            else: BinList.append("CMP 1 0")

            #JMPIF command
            BinList.append("JMPIF 0 AE")
            BinList.append("DT 0 "+str(len(BinList)+3))

            #Tale of if command for else jump
            BinList.append("JMP 0 ")
            BinList.append("DT 0 "+Id+"end")
        elif InstructionSet[rt_offset+1] == "-ne":
            BinList.append("CMP 1 0")
            BinList.append("JMPIF 0 E")
            BinList.append("DT 0 "+str(len(BinList)+3))
            BinList.append("JMP 0 0")
            BinList.append("DT 0 "+str(len(BinList)+3))
            BinList.append("JMP 0 0")
            BinList.append("DT 0 "+Id+"end")
        rt_offset += 3
    
    if len(InstructionSet)>rt_offset:
        if InstructionSet[rt_offset] == ")":
            return rt_offset+1
        elif InstructionSet[rt_offset] == "-and":
            rt_offset += 1
            rt_offset = condition_GenerateBin(InstructionSet, rt_offset, BinList, Id)
        elif InstructionSet[rt_offset] == "-or":
            rt_offset += 1
            BinList.pop()
            BinList.pop()
            Changable = len(BinList)-1
            rt_offset = condition_GenerateBin(InstructionSet, rt_offset, BinList, Id)
            BinList[Changable] = "DT 0 "+str(len(BinList))
    
    return rt_offset

def sFunCreate_GenerateBin (sFunName: str, ParamList: list, BinList: list):

    #Creating variables
    global ErrorMsg
    sFunLocalVariables.clear()
    
    BinList.append("JMP 0 0")
    BinList.append("DT 0 "+("@id/sfun_"+sFunName+"end"))

    for variableName in ParamList:
        print (variableName)

    for variableName in ParamList:
        if not isVarNameValid(variableName):
            ErrorMsg = "Invalid varriable name: \""+variableName+"\""
            print(ErrorMsg)
            return
        sFunLocalVariables[variableName] = str(len(BinList))
        BinList.append("DT 0 0")
    
    rtLocMem = len(BinList)
    BinList.append("DT 0 0") #For return Location saving

    #Return Locaion Saved
    BinList.append("DATA 0 2")
    BinList.append("DT 0 "+str(rtLocMem))
    BinList.append("ST 2 3")

    #Copying Data from parameter array of function to in-function Mem Locations
    BinList.append("DATA 0 1")
    BinList.append("DT 0 1")
    BinList.append("DATA 0 2")
    BinList.append("DT 0 "+str(rtLocMem+1))

    for i in range(len(ParamList)):
        BinList.append("LD 0 3")
        BinList.append("ST 2 3")
        BinList.append("ADD 1 2")
        BinList.append("ADD 1 0")
    

binList = []
sourceCodeList = []

def main():
    global ErrorMsg, locId, resolvableIDs, ifIdCounter, loopIdCounter
    for i, line in enumerate(sourceCodeList):
        words = splitStr(line)
        
        if ErrorMsg != "":
            print("Error in line "+str(i)+":\n\t"+line+"\n"+ErrorMsg)
            return
        elif words[0] == "var": var_GenerateBin(words, binList)
        elif words[0] == "set": set_GenerateBin(words, 1, binList)
        elif words[0] in ["if", "loop"]:
            if len(words) != 3: ErrorMsg = words[0]+" statement syntax error: Condition must be in \"()\""
            
            newId = ""
            if words[0] == "if":
                newId = "@id/if"+str(ifIdCounter)
                ifIdCounter += 1
            else:
                newId = "@id/loop"+str(loopIdCounter)
                loopIdCounter += 1

            resolvableIDs.append(newId)
            locId[newId] = len(binList)

            conditionList = []

            splited = []
            word = ""
            for i in words[1]:
                if i == " ":
                    if word != "":
                        splited.append(word.strip())
                        word = ""
                elif i == "(" or i == ")" :
                    if word != "":
                        splited.append(word.strip())
                        word = ""
                    splited.append(i)
                else: word = word + i
        
            if word != "": splited.append(word.strip())

            conditionList = splited
            
            condition_GenerateBin(conditionList, 0, binList, newId)
            
            if 3 < len(words): ErrorMsg = "Expected the next instruction in next line"
            elif 3 > len(words): ErrorMsg = "Expected the \'{\' symbol"
        elif words[0] == "sfun":
            global activeFunctions
            word = ""
            splited = []

            newId = "@id/sfun_"+words[1]
            resolvableIDs.append(newId)
            sFunNames.append(words[1])
            activeFunctions = words[1]

            #Retriving parameters from the function
            for i in words[2]:
                if i == "(" or i == ")" :
                    if word != "":
                        splited.append(word.strip())
                        word = ""
                elif i == ",":
                    if word != "":
                        splited.append(word.strip())
                        word = ""
                else: word = word + i
            if word != "": splited.append(word.strip())

            locId[newId] = len(binList) + len(splited) + 3

            sFunCreate_GenerateBin(words[1], splited, binList) # Used to create binaries for function local variables
        elif words[0] == "call":
            pass #To be continued

        elif words[0] == "}":
            if len(resolvableIDs) > 0:
                id = resolvableIDs.pop()
                if "@id/if" in id and not "el" in id and len(words) > 1 and words[1] == "else":
                    binList.append("JMP 0 0")
                    binList.append("DT 0 "+id+"elend")
                    resolvableIDs.append(id+"el")
                elif "@id/loop" in id:
                    binList.append("JMP 0 0")
                    binList.append("DT 0 "+str(locId[id]))
                elif "@id/sfun" in id:
                    binList.append("DATA 0 3")
                    binList.append("DT 0 "+str(locId[id]-1))
                    binList.append("LD 3 3")
                    binList.append("JMPR 0 3")
                locId[id+"end"] = len(binList)
        else:
            print("Invalid keyword: "+words[0])
            return
        
        if ErrorMsg != "":
            print("Error in line "+str(i)+":\n\t"+line+"\n"+ErrorMsg)
            return

    
    for i, instruction in enumerate(binList):
        parameters = splitStr(instruction)
        for j, parameter in enumerate(parameters):
            if "@" in parameter:
                print(parameter)
                print(locId)
                if parameter in locId:
                    print("Done")
                    instruction = instruction.replace(parameter, str(locId[parameter]))
                    binList[i] = instruction
    

def compile(iFileLocation:str, oFileLocation:str):
    sourceCodeList.clear()
    binList.clear()

    global ErrorMsg
    ErrorMsg = ""

    iFile = open(iFileLocation, "r")
    sourceCode = iFile.read()
    iFile.close()

    for item in sourceCode.splitlines(): sourceCodeList.append(item)

    #Validating the list by eliminating none lines and polishing for better compatibility
    i = 0
    while (i < len(sourceCodeList)):
        sourceCodeList[i] = sourceCodeList[i].strip()
        if sourceCodeList[i] == "": sourceCodeList.pop(i)
        else: i += 1

    main()

    binaryCode = ""
    for i in binList:
        binaryCode = binaryCode+i+"\n"

    oFile = open(oFileLocation, "w")
    oFile.write(binaryCode)
    oFile.close()
