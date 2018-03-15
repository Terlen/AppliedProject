from smartcard.System import readers
from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes
from smartcard.Exceptions import *


reader = readers()[0]
print ("Currently attached reader: ",reader)
connection = reader.createConnection()

try:
    connection.connect()
    print ("Smart card detected!")
except NoCardException:
    print ("No smart card detected!")
    exit()

input("Press enter to continue")
print ("\nLoading authentication key [FF FF FF FF FF FF] to reader")
DATA = [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
response, sw1, sw2 = connection.transmit(DATA)
print ("Reader response code: ",toHexString([sw1]),toHexString([sw2]))
if sw1 == 144:
    print ("Key loading successful!")
elif sw1 == 99:
    print ("Key loading failed, please try again.")

while True:
    operation = input("Would you like to read or write? (R/W)").upper()
    if operation == "R":
        blockAddress = input ("Please enter the address of the block you would like to read: (0x00 - 0x3E)(0xXX)")
        blockAddress = int(blockAddress, 16)
        DATA = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, blockAddress, 0x60, 0x00]
        response, sw1, sw2 = connection.transmit(DATA)
        if sw1 == 144:
            print("Authentication with block ",hex(blockAddress)," successful!")
        elif sw1 == 99:
            print("Authentication error, please try again.")
            continue
        DATA = [0xFF, 0xB0, 0x00, blockAddress, 0x10]
        response, sw1, sw2 = connection.transmit(DATA)
        if sw1 == 144:
            print ("Read successful: ",toHexString(response))
        if sw2 == 99:
            print ("Read error, try again.")
            continue
    elif operation == "W":
        blockAddress = input ("Please enter the address of the block you would like to write: (0x00 - 0x3E)(0xXX)")
        blockAddress = int(blockAddress, 16)
        DATA = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, blockAddress, 0x60, 0x00]
        response, sw1, sw2 = connection.transmit(DATA)
        if sw1 == 144:
            print("Authentication with block ",hex(blockAddress)," successful!")
        elif sw1 == 99:
            print("Authentication error, please try again.")
            continue
        writeData = int(input("Please enter the value you want to write to the block: (0xXX): "),16)
        DATA = [0xFF, 0xB0, 0x00, blockAddress, 0x10]
        response, sw1, sw2 = connection.transmit(DATA)
        oldData = response
        DATA = [0xFF, 0xD6, 0x00, blockAddress, 0x10, writeData, writeData, writeData, writeData, writeData, writeData, writeData, writeData, writeData,
                writeData, writeData, writeData, writeData, writeData, writeData, writeData]
        response, wsw1, wsw2 = connection.transmit(DATA)
        DATA = [0xFF, 0xB0, 0x00, blockAddress, 0x10]
        response, sw1, sw2 = connection.transmit(DATA)
        newData = response
        if wsw1 == 144:
            print ("Write successful!\nOld Data: ",toHexString(oldData),"\nNew Data: ",toHexString(newData))
        if wsw2 == 99:
            print ("Write error, try again.")
            continue
    else:
        continue
    while True:
        confirm = input("\nPerform another operation? (Y/N)").upper()
        if confirm == "Y":
            break
        elif confirm == "N":
            exit()
        else:
            continue
