
#To functions are created for converting Numeric Codes to dict codes and vise versa
#Program is incomplete, Need to implement the recently created methods to DATA, JMP, JMPIF

InstructionSet = [
    "LD",
    "ST",
    "DATA",
    "JMPR",
    "JMP",
    "JMPIF",
    "FLG",
    "IO",
    "ADD",
    "SHL",
    "SHR",
    "AND",
    "OR",
    "NOT",
    "XOR",
    "CMP",
    "DT"
]
Register = [0, 0, 0, 0, 0, 0, 0, 0]
runtimeMem = {}
carry = False
zero = False
greater = False
equal = False

def extractInstructions(List:list):
    rList = []
    for i in List:
        tokens = i.split()
        Instructions = {}
        Instructions["Ins"] = tokens[0]
        Instructions["P1"] = tokens[1]
        Instructions["P2"] = tokens[2]
        rList.append(Instructions)
    return rList

def errorFree(List: list):
    for i in List:
        if not i["Ins"] in InstructionSet: return False
        if not str(i["P2"]).isdigit():
            for j in str(i["P2"]):
                if not j in "CAEZ": return False
            return True
        if not str(i["P1"]).isdigit(): return False
    return True

def convertToInstructionCode(NumberCode:str) -> dict:
    VerifiedNumCode = int(NumberCode) % 65536
    InstructionBits = VerifiedNumCode >> 12
    p1 = str((VerifiedNumCode & 0b11110000) >> 4)
    p2 = ""
    TempNum = VerifiedNumCode & 0b1111
    if InstructionBits != 5: p2 = str(TempNum)
    else:
        if (TempNum & 8) > 0: p2 = p2 + "C"
        if (TempNum & 4) > 0: p2 = p2 + "A"
        if (TempNum & 2) > 0: p2 = p2 + "E"
        if (TempNum & 1) > 0: p2 = p2 + "Z"
    return {
        "Ins": InstructionSet[InstructionBits],
        "P1": str(p1),
        "P2": str(p2)
    }

def convertToNumerics(iSet:dict) -> int:
    if iSet["Ins"] == "DT": return int(iSet["P2"])%65536
    InstructionBit = InstructionSet.index(iSet["Ins"])
    p1 = int(iSet["P1"])
    p2 = 0
    if str(iSet["P2"]).isdigit(): p2 = int(iSet["P2"])
    else:
        if "C" in str(iSet["P2"]): p2 += 8
        if "A" in str(iSet["P2"]): p2 += 4
        if "E" in str(iSet["P2"]): p2 += 2
        if "Z" in str(iSet["P2"]): p2 += 1
    
    return ((((InstructionBit << 8) + p1) << 4) + p2)%65536


def LD(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    if Register[int(P1)] < len(sList):
        if Register[int(P1)] in runtimeMem: Register[int(P2)] = runtimeMem[Register[int(P1)]]%65536
        else: Register[int(P2)] = convertToNumerics(sList[Register[int(P1)]])#only return 16bit
    elif Register[int(P1)] in runtimeMem: Register[int(P2)] = runtimeMem[Register[int(P1)]]%65536
    else: Register[int(P2)] = 0
    
def ST(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    runtimeMem[Register[int(P1)]] = Register[int(P2)]
    if Register[int(P1)] < len(sList): sList[Register[int(P1)]] = convertToInstructionCode(Register[int(P2)])
    
def DATA(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%65536
    Register[int(P1)] = P2

def ADD(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    global carry, zero
    Register[int(P2)] += Register[int(P1)]
    if carry:
        Register[int(P2)] += 1
        carry = False
    if Register[int(P2)] >= 65536:
        carry = True
        Register[int(P2)] %= 65536
    zero = Register[int(P2)] == 0

def SHL(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    global carry
    v1 = Register[int(P1)]
    v1 = v1 << 1
    if carry: v1 += 1
    if v1 >= 65536:
        v1 %= 65536
        carry = True
    else: carry = False
    Register[int(P2)] = v1
    global zero
    zero = Register[int(P2)] == 0

def SHR(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    global carry
    v1 = Register[int(P1)]
    if carry: v1 += 65536
    if v1 % 2 == 1: carry = True
    else: carry = False
    v1 = v1 >> 1
    Register[int(P2)] = v1
    global zero
    zero = Register[int(P2)] == 0

def AND(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    Register[int(P2)] = Register[int(P1)] & Register[int(P2)]
    global zero
    zero = Register[int(P2)] == 0

def OR(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    Register[int(P2)] = Register[int(P1)] | Register[int(P2)]
    global zero
    zero = Register[int(P2)] == 0

def NOT(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    Register[int(P2)] = (~Register[int(P1)])%65536
    global zero
    zero = Register[int(P2)] == 0

def XOR(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    v1 = Register[int(P1)]
    v2 = Register[int(P2)]

    Register[int(P2)] = (v1 | v2) & ~(v1 & v2)
    global zero
    zero = Register[int(P2)] == 0

def CMP(P1, P2):
    P1 = int(P1)%8
    P2 = int(P2)%8
    v1 = Register[int(P1)]
    v2 = Register[int(P2)]
    
    global equal, greater, zero

    equal = v1 == v2
    greater = v1 > v2
    zero = True

def runProcessor():
    global equal, greater, zero, carry
    i = 0
    while(i < len(sList)):
        iSet = sList[i]
        i += 1
        if iSet["Ins"] == "LD": LD(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "ST": ST(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "DATA":
            p2 = 0
            if i < len(sList): p2 = convertToNumerics(sList[i])#only returns 16bit
            DATA(iSet["P2"], p2)
            i += 1
        elif iSet["Ins"] == "JMPR": 
            i = Register[int(iSet["P2"])]
        elif iSet["Ins"] == "JMP":
            if i in runtimeMem: i = runtimeMem[i]
            elif i < len(sList): i = convertToNumerics(sList[i])
            else: i = 0
        elif iSet["Ins"] == "JMPIF":
            ConditionStr = iSet["P2"]
            iSet = sList[i]
            i += 1
            if carry and "C" in ConditionStr: i = convertToNumerics(iSet)
            elif greater and "A" in ConditionStr: i = convertToNumerics(iSet)
            elif equal and "E" in ConditionStr: i = convertToNumerics(iSet)
            elif zero and "Z" in ConditionStr: i = convertToNumerics(iSet)
        elif iSet["Ins"] == "FLG":
            if int(iSet["P1"]) == 0 and int(iSet["P2"]) == 0:
                carry = False
                zero = False
                greater = False
                equal = False
        elif iSet["Ins"] == "ADD": ADD(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "SHL": SHL(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "SHR": SHR(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "AND": AND(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "OR": OR(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "NOT": NOT(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "XOR": XOR(iSet["P1"], iSet["P2"])
        elif iSet["Ins"] == "CMP": CMP(iSet["P1"], iSet["P2"])
        #showLog(iSet)

def showLog(hMap: dict):
    logStr = ""
    for i in Register:
        logStr = logStr + str(i) + "\t"
    logStr = logStr + hMap["Ins"] + " " + hMap["P1"] + " " + hMap["P2"]
    print(logStr.strip())   

def run(InsLst:list):
    global sList
    sList = extractInstructions(InsLst)
    if errorFree(sList): runProcessor()
    else: print("Error")
