########################################
# 10821039_朱珮瑜_Two Pass SIC/XE
# All loc count by decimal int, change form only at printing
########################################
import string
import opTable
import symbolTable

originalFile = open('.\input\SICXE_COPY.txt', mode='r') # your input file here
intermediateFile = open('intermediateFile.txt', mode='w+')
pseudoCode = ['START', 'END', 'RESW', 'RESB', 'BYTE', 'WORD', 'BASE']
errorList = []

# Pass 1 variable
start = False
lineNum = 0
progName = ''
progLen = 0
startLoc = 0
curLoc = 0
end = False

# Pass 2 variable
objectProgram = []
base = 0
pc = 0

def main():
    global lineNum
    # build opTable
    opTable.build()
    # Pass 1
    while end == False:
        line = originalFile.readline().partition('.')[0].strip()
        lineNum += 1
        if len(line) == 0: 
            continue
        else:
            if (start == False) & (not 'START' in line) :
                errorList.append([1, lineNum, '程式開頭必須包含 START'])
            else:
                judgeToken(line)

    # print immediate file
    intermediateFile.seek(0)
    lineNum = 1
    for line in intermediateFile:
        print(f'{lineNum} \t {line}', end='')
        lineNum += 1
    print()

    # Pass 2
    intermediateFile.seek(0)
    # symbolTable.printSymbolTable()
    objProgram(intermediateFile)

    # print errorList
    for e in errorList:
        print('\033[91m' + f"(PASS {e[0]}) ERROR AT LINE {e[1]} : {e[2]}" + '\033[0m')

    # print object program if no error
    if len(errorList) == 0:
        for e in objectProgram:
            for f in e:
                if f != '':
                    print('\033[92m' + f'{f}' + '\033[0m', end=' ')
                else: continue
            print()

########################################

# Pass 1
# remove comment
# generate intermediate file
#   1. intermediate file format
#       LineNum, loc, symbol, opcode/pseudo, operand, opcode, addrMode
#   2. don't write in intermediate file if error

########################################

def judgeToken(line):
    global start
    global progName
    global end
    global curLoc
    
    line = cutLine(line)
    match len(line):
        case 3: # with symbol
            symbol = line[0]
            opcode = line[1]
            operand = line[2]
            if opcode == 'RSUB':
                errorList.append([1, lineNum, 'RSUB 不能有 operand'])
                operand = '-----'
        case 2: # without symbol
            symbol = '-----'
            opcode = line[0]
            operand = line[1]
            # adjust error case (without operand)
            tmpOpcode = opcode.lstrip('+')
            [findOpcode, result] = opTable.findOpcode(opcode.lstrip('+'))
            if (findOpcode == False) & (not tmpOpcode in pseudoCode):
                tmpOpcode = operand
                if (opTable.findOpcode(tmpOpcode)[0]) | (tmpOpcode in pseudoCode):  # when operand is actually opcode => lost operand
                    symbol = line[0]
                    opcode = line[1]
                    if opcode == 'RSUB':
                        operand = ''
                    else:
                        errorList.append([1, lineNum, '*Lost operand'])
                        operand = '-----'
            # error case: RSUB [operand]
            elif (tmpOpcode == 'RSUB') & (operand != ''):
                errorList.append([1, lineNum, 'RSUB 不能有 operand'])
                operand = '-----'
                    
        case 1:
            symbol = '-----'
            opcode = line[0]
            operand = ''
            if opcode != 'RSUB':
                errorList.append([1, lineNum, '**Lost operand'])
                operand = '-----'
        case _:
            errorList.append([1, lineNum, '此行無法正確切割'])
            return 
    
    tmpOpcode = opcode.lstrip('+')
    # pseudoCode
    if tmpOpcode in pseudoCode:
        match opcode:
            case 'START':
                caseSTART(curLoc, symbol, opcode, operand)
            case 'END':
                caseEND(curLoc, symbol, opcode, operand)
                end = True
                return
            case 'BYTE':
                caseBYTE(curLoc, symbol, opcode, operand)
            case 'BASE':
                retMsg = symbolTable.build(symbol, curLoc)
                if retMsg != '':
                    errorList.append([1, lineNum, retMsg])
                    return
                else:
                    writeFile('-----', symbol, opcode, operand, '     ', '')
            case _:
                caseELSE(curLoc, symbol, opcode, operand)

    # mnemonic
    else:
        retMsg = symbolTable.build(symbol, curLoc)
        if retMsg != '':
            errorList.append([1, lineNum, retMsg])                    
        [findOpcode, errorMsg] = opTable.findOpcode(tmpOpcode)
        if findOpcode == False:
            errorList.append([1, lineNum, errorMsg])

        else:
            writeFile(curLoc, symbol, opcode, operand, opTable.answer, addressingMode(operand))
            match opcode:
                case var if '+' in var:
                    curLoc += 4
                case 'CLEAR' | 'COMPR' | 'ADDR' | 'TIXR' | 'SVC' | 'DIVR' | 'RMO' | 'MULR':# FIXME: 指令 format 2 要修訂
                    curLoc += 2
                    # register 會有 1或2個暫存器
                    # FIXME: compr
                case _:
                    curLoc += 3
                # FIXME: format 1
                # sol: 

def cutLine(line):
    line = line.split()
    for i in range(len(line)):
        if line[i] == ',':
            joinOperand = ''.join(line[i-1:])
            del(line[i-1:])
            line.append(joinOperand)
            break
        elif line[i].endswith(','):
            joinOperand = ''.join(line[i:])
            del(line[i:])
            line.append(joinOperand)
            break
    return line

def caseSTART(loc, symbol, opcode, operand):
    global start
    global startLoc
    global lineNum
    global progName
    global curLoc

    if start == False:
        start = True
    else:
        errorList.append([1, lineNum, 'More than one START appear'])
        return
    if symbol == '-----':
        errorList.append([1, lineNum, 'Without Program Name'])
    if not operand.isdigit():
        errorList.append([1, lineNum, 'Invalid start location'])
    else:
        writeFile('-----', symbol, opcode, operand, '     ', '')
        progName = symbol    # get program name
        curLoc = int(operand, 16) # convert hex to int
        startLoc = curLoc   # initial startAddress

def caseEND(loc, symbol, opcode, operand):
    global progLen    
    writeFile(curLoc, symbol, opcode, operand, '     ', '')
    progLen = loc - startLoc # count and store program length    

def caseBYTE(loc, symbol, opcode, operand):
    global lineNum
    global curLoc

    splitOperand = operand.split("'")
    type = splitOperand[0]
    content = splitOperand[1]
    
    retMsg = symbolTable.build(symbol, curLoc)
    if retMsg != '':
        errorList.append([1, lineNum, retMsg])
        return
    else:
        if (len(splitOperand) != 3):
                errorList.append([1, lineNum, "BYTE 內容前後需有引號"])
                return
        if (splitOperand[2] != ''):
                errorList.append([1, lineNum, "Illegal BYTE content"])
                return
        if content == '':
                errorList.append([1, lineNum, "BYTE 內容不可為空"])
                return
        if (type == 'X'):
            if operand[0] == 'X':
                if len(content)%2 != 0:
                    errorList.append([2, lineNum, 'BYTE type of X should have even number content.'])
                elif all(c in string.hexdigits for c in content):
                    writeFile(curLoc, symbol, opcode, operand, '     ', '')
                else:
                    errorList.append([1, lineNum, "Illegal BYTE content(type X should followed by hex)"])
            curLoc += (len(content))//2
        elif (type == 'C'):
            writeFile(curLoc, symbol, opcode, operand, '     ', '')
            curLoc += (len(content))
        else:
            errorList.append([1, lineNum, "Illegal BYTE type(BYTE should followed by recognizable char 'X' or 'C')"])
            return

def caseELSE(loc, symbol, opcode, operand):
    global curLoc
    retMsg = symbolTable.build(symbol, curLoc)
    if retMsg != '':
        errorList.append([1, lineNum, retMsg])  
        return
    else:
        if not operand.isdigit():
            errorList.append([1, lineNum, f'{opcode} should followed by integer'])
            return
        else:
            writeFile(curLoc, symbol, opcode, operand, '     ', '')
            match opcode:
                case 'RESW':
                    curLoc = curLoc + 3 * int(operand)
                case 'RESB':
                    curLoc = curLoc + int(operand)
                case 'WORD':
                    curLoc += 3

def writeFile(loc, symbol, opCode, operand, opCodeAns, mode):
    global lineNum
    if loc == '-----':
        wLoc = '-----'
    else:
        wLoc = str(str('%04x' % loc))
        # wLoc = str(hex(loc)).strip('0x').rjust(4, '0')
    intermediateFile.writelines([
                    str(lineNum), '\t\t',
                    wLoc, '\t\t',
                    symbol, '\t\t',
                    opCode, '\t\t',
                    str(operand), '\t\t',
                    opCodeAns, '\t\t',
                    mode, '\n'])

def addressingMode(operand):
    if operand == '-----':   # no operand, then no addrMode
        mode = '-----'
    elif operand == '':
        mode = ''
    else:   # judge addrMode
        if(',' in operand): mode = 'index'
        elif('#' in operand):   mode =  'immediate'
        elif('@' in operand):   mode = 'indirect'
        else:   mode = 'simple'
    return mode

########################################

# Pass 2
# read intermediate file
#   intermediate file format
#       loc, symbol, opcode/pseudo, operand, opcode, addrMode
# generate object program

########################################

def objProgram(intermediateFile):
    global lineNum
    global objectProgram
    global base
    global pc
    f = intermediateFile.readlines()
    TLen = 0
    TList = []
    resLine = 0

    for i in range(len(f)):
        line = f[i].split()
        # print every line
        # print(f'{i+1}:  {line}')
        lineNum = line[0]
        loc = line[1]
        opcode = line[3]
        operand = line[4]

        # store pc loc
        if i != len(f) -1 :
            if f[i+1].split()[1] != '-----':
                pc = f[i+1].split()[1]
            else:
                pc = f[i+2].split()[1]

        match opcode:
            # H Record
            case 'START':
                objCode = ''
                objectProgram.append([])
                objectProgram[resLine] = ['H', progName, operand.rjust(6, "0"), adjustF(6, hex(progLen), 16)]
                resLine += 1
            # E Record
            case 'END':
                objCode = ''
                # make sure TList is all printed
                tmpList = []
                tmpList.append('T')
                for i in range(len(TList)):
                    if i == 0:
                        tmpList.append(TList[i].rjust(6, "0"))
                        tmpList.append(adjustF(2, hex(TLen), 16))
                    else:
                        tmpList.append(TList[i])
                objectProgram.append([])
                objectProgram[resLine] = tmpList
                resLine += 1
                TList.clear()
                TLen = 0

                objectProgram.append([])
                res = symbolTable.search(operand)
                if res == 'Label Not Found':
                    errorList.append([2, lineNum, res])
                else:
                    objectProgram[resLine] = ['E', adjustF(6, symbolTable.search(line[4]), 16)]
            # T Record(count objCode)
            case _:
                match opcode:
                    case 'RESW' | 'RESB':   # print & clear TList
                        objCode = ''
                    case 'BASE':    # store base loc
                        base = symbolTable.search(operand)
                        objCode = ''
                    case 'RSUB':
                        if operand != '-----':                        
                            objCode = adjustF(2, hex(int(operand, 16) + int('3', 16)), 16).ljust(6, '0')
                    case 'WORD':
                        objCode = adjustF(6, operand, 16)
                    case 'BYTE':
                        content = operand[2:-1]
                        if operand[0] == 'X':
                            objCode = operand.strip("X'")
                        else:
                            tmpObjCode = []
                            for i in range(len(content)):
                                tmpObjCode.append(hex(ord(content[i]))[2:])
                            objCode = ''.join(tmpObjCode).rjust(6, '0')
                    case _:
                        objCode = countObjcode(line)

                # collect T Record
                tmpTLen = TLen + len(objCode)//2
                if (opcode == 'RESW') | (opcode == 'RESB'):
                    if TLen == 0:
                        continue
                    tmpList = []
                    tmpList.append('T')
                    for i in range(len(TList)):
                        if i == 0:
                            tmpList.append(TList[i].rjust(6, "0"))
                            tmpList.append(adjustF(2, hex(TLen), 16))
                        else:
                            tmpList.append(TList[i])
                    objectProgram.append([])
                    objectProgram[resLine] = tmpList
                    resLine +=1
                    TList.clear()
                    TLen = 0
                elif TLen == 0:
                    TList.append(loc)
                    TList.append(objCode)
                    TLen = len(objCode) // 2
                elif tmpTLen <= 30 :
                    TList.append(objCode)
                    TLen = tmpTLen
                else:
                    # when TList bomb, print it and clear it up
                    tmpList = []
                    tmpList.append('T')
                    for i in range(len(TList)):
                        if i == 0:
                            tmpList.append(TList[i].rjust(6, "0"))
                            tmpList.append(adjustF(2, hex(TLen), 16))
                        else:
                            tmpList.append(TList[i])
                    objectProgram.append([])
                    objectProgram[resLine] = tmpList
                    resLine += 1
                    TList.clear()
                    TLen = 0

                    # do things as TLen == 0
                    TList.append(loc)
                    TList.append(objCode)
                    TLen = len(objCode) // 2


def adjustF(bit, input, f):
    # bit: fill form to how many bit
    # f: present input in what base (hex or decimal)
    if f == 16: f = 'X' # upperSize
    else:   f = 'd'
    joinList = ['%', '0', str(bit), f]
    tmpVar = ''.join(joinList)

    if (type(input) == int):
        result =  str(f'{tmpVar}' % input)
    elif ('0x' in input) | (not input.isdigit()):    # convert string in hex form into decimal
        result = str(f'{tmpVar}' % int(input, base=16))
    elif (type(input) == str):
        result =  str(f'{tmpVar}' % int(input))
    else:
        print('\033[91m' + "ERROR at adjustF: Cannot convert to right adjustFormat \n" + '\033[0m')
    return result

def countObjcode(line):
    opcode = line[3]
    operand = line[4]
    opAns = line[5]
    if operand == '-----':
        return 'XXXXXX'
    else:
        match opcode:
            # format 2 (2 register)
            case 'ADDR' | 'COMPR':
                objCode = [None] * 2
                objCode[0] = opAns    # (1) (2) : opcode
                objCode[1] = ''         # (3) (4) : register loc
                tmpOperand = operand.split(',')
                if len(tmpOperand) == 2:
                    for i in operand.split(','):
                        if i == '':
                            errorList.append([2, lineNum, f'{opcode} should have 2 registers operand'])
                        objCode[1] += symbolTable.search(i)
                else:
                    errorList.append([2, lineNum, f'{opcode} should have only 2 registers operand'])
                    return 'XXXXXX'
            case 'TIXR' | 'CLEAR' :
                objCode = [None] * 2
                objCode[0] = opAns    # (1) (2) : opcode
                objCode[1] = ''         # (3) (4) : register loc
                objCode[1] += symbolTable.search(operand).ljust(2, "0")
            # format 4
            case var if '+' in var:
                objCode = [None] * 3
                match line[6]:
                    case 'indirect':
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('2', 16)), 16)    # nixbpe = 100001
                        objCode[1] = '1'
                        tmpOperand = operand.strip('@')
                        if tmpOperand.isdigit():
                            objCode[2] = hex(int(tmpOperand))[2:].rjust(5, '0')
                        else:
                            objCode[2] = symbolTable.search(tmpOperand)[2:].rjust(5, "0")
                    case 'immediate':
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('1', 16)), 16)   # nixbpe = 010001
                        objCode[1] = '1'
                        tmpOperand = operand.strip('#')
                        if tmpOperand.isdigit():
                            objCode[2] = hex(int(tmpOperand))[2:].rjust(5, '0')
                        else:
                            objCode[2] = symbolTable.search(tmpOperand)[2:].rjust(5, "0")
                    case 'index':
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('3', 16)), 16)    # nixbpe = 111001
                        # FIXME
                        objCode[1] = '1'
                        tmpOperand = operand.split(',')[0]
                        if tmpOperand.isdigit():
                            objCode[2] = tmpOperand.rjust(5, '0')
                        else:
                            objCode[2] = symbolTable.search(tmpOperand)[2:].rjust(5, "0")
                    case _:
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('3', 16)), 16)    # nixbpe = 110001
                        objCode[1] = '1'
                        if line[3].isdigit():
                            objCode[2] = operand.rjust(5, '0')
                        else:
                            objCode[2] = symbolTable.search(operand)[2:].rjust(5, "0")
            case 'RSUB':
                objCode = [None] * 2
                objCode[0] = opAns
                objCode[1] = '0000'
            # format 3
            case _:
                objCode = [None] * 3
                # (1) (2): n i
                # (3): xbpe
                # (4) (5) (6): operand
                match line[6]:
                    case 'indirect':
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('2', 16)), 16)
                        tmpOperand = operand.strip('@')
                        if tmpOperand.isdigit():    # nixbpe = 100000
                            objCode[1] = '0'
                            objCode[2] = tmpOperand.rjust(3, '0')
                        else:   # nixbpe = 10
                            result = judgeBP(tmpOperand)
                            objCode[1] = hex(int('0' + result[0] + '0', 2))[2:]
                            objCode[2] = result[1][2:].rjust(3, '0')
                    case 'immediate':
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('1', 16)), 16)   # nixbpe = 010000
                        objCode[1] = '0'
                        tmpOperand = operand.strip('#')
                        if tmpOperand.isdigit():
                            objCode[2] = tmpOperand.rjust(3, '0')
                        else:
                            [bp, res] = judgeBP(tmpOperand)
                            objCode[1] = hex(int('0' + bp + '0', 2))[2:]
                            objCode[2] = res[2:].rjust(3, '0')
                    case 'index':
                        # nixbpe = 111 _ _ 0
                        tmpOperand = operand.split(',')[0]
                        [bp, res] = judgeBP(tmpOperand)
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('3', 16)), 16)
                        objCode[1] = hex(int('1' + bp + '0', 2))[2:]
                        objCode[2] = res[2:].rjust(3, '0')
                    case 'simple':
                        objCode[0] = adjustF(2, hex(int(opAns, 16) + int('3', 16)), 16)    # nixbpe = 110000
                        if operand.isdigit():
                            objCode[1] = operand.rjust(4, '0')
                        else:
                            [bp, res] = judgeBP(operand)
                            if bp != 'XX':
                                objCode[1] = hex(int('0' + bp + '0', 2))[2:]
                                objCode[2] = res[2:].rjust(3, '0')
                            else:
                                return 'XXXXXX'
        return ''.join(objCode)

def judgeBP(operand):
    # PC_relative = -2048 ~ 2047
    # base_relative = 0 ~ 4096
    # displacement = loc(operand) - (PC)
    global base
    global pc
    res = symbolTable.search(operand)
    if res != 'Label Not Found':
        loc = res.lstrip('0x').rjust(4, '0')
    else:
        errorList.append([2, lineNum, res])
        return 'XX', 'XXXX'
    # try pc
    ans = int(loc, 16) - int(pc, 16)
    if (ans < 2047) & (ans > -2048):
        if ans < 0:
            ans  = int(bin2(ans), 2)
        return '01', hex(ans)
    else:   # try base
        ans = int(loc, 16) - int(base, 16)
        if (ans >= 0) & (ans <= 4096):
            return '10', hex(ans)
        else:
            print('\033[91m' + '***** Error: BP judging out of range *****' + '\033[0m')
            return 'XX' , 'XXXX'

def bin2(x):
    bits = 12      # 計算位元數
    n = (1 << bits) - 1            # 相同位元數全為 1 的數
    x2 = n & x                     # & 運算
    if x < 0:
        return f"{x2:#{bits+2}b}"  # 2 進位表示
    else:
        return f"{x2:#0{bits+2}b}" # 正數補上正負號位元

if __name__ == '__main__':
    main()
    originalFile.close()
    intermediateFile.close()
    print()