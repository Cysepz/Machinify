# Build and Search symbolTable
# Optable class method：Insert、Search
# prebuild register translation in symbolTable
symbolTable = {'A': '0', 'X': '1', 'L': '2', 'B': '3', 'S': '4', 'T': '5', 'F': '6', 'PC': '8', 'SW': '9'}

def main():
    print("Please input label and address : ", end='')
    inputList = input().split(' ')
    buildMain(inputList)
    print("Search (Input a label) : ", end='')
    search(input())

# Build input into dictionary
def buildMain(inputList):
    global symbolTable
    print(symbolTable)
    keyList = []
    valueList = []
    for i in range(len(inputList)):
        # put even bumber in key
        # put odd number in value
        if(i % 2 == 0):
            # Duplicate error
            if (inputList[i] in keyList):
                print('\033[91m' + f"ERROR : Duplicate Label Error at {inputList[i]} {inputList[i+1]} \n" + '\033[0m')
                exit()
            else:
                keyList.append(inputList[i])
        else:
            valueList.append(inputList[i])
    symbolTable = dict(zip(keyList, valueList))

def build(label, loc):
    if label == '-----':
        return ''
    if(label in symbolTable):
        # print('\033[91m' + f"ERROR AT LINE {lineNum} : Duplicate Label at {label}" + '\033[0m')
        return f'Duplicate Label at {label}'
    else:
        symbolTable[label] = hex(loc)
        return ''

# Search Label in symbolTable
def search(input):
        if symbolTable.get(input) :
            # print("Address : " + symbolTable[input] + '\n')
            return symbolTable[input]
        else:
            # print('\033[91m' + "ERROR: Label Not Found \n" + '\033[0m')
            return 'Label Not Found'

def printSymbolTable():
    global symbolTable
    print('Symbol Table:')
    for key, value in symbolTable.items():
        if not value.isdigit():
            print(key, ':', value)
    print('\n')

if __name__ == '__main__':
    main()