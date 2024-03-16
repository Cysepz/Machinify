# Search mnemonic in opTable
global opTable
def main():
    print("Search (Input a mnemonic) : ", end='')
    findOpcode(input())

def build():
    global opTable
    f = open("opCode.txt", mode='r')
    opTable = {}
    for line in f:
        (k, v) = line.split()
        opTable[k] = v


def findOpcode(input):
    global answer
    global opTable
    # Build input file into dictionary

    # search
    if input.isalpha() == False :
        return False, 'Illegal Mnemonic Input'
    else :
        if opTable.get(input) :
            answer = opTable[input]
            # print('opcode : ' + answer)
            outputAns()
            return True, ''
        else:
            # print('\033[91m' + "ERROR : Mnemonic Not Found \n" + '\033[0m')
            return False, f'Mnemonic {input} Not Found'
        
def outputAns():
    global answer
    return answer

if __name__ == '__main__':
    main()