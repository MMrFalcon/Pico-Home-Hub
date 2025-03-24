import machine
import json

# 3 - ID - GPIO number.
LED = machine.Pin("LED", machine.Pin.OUT)
SWITCH_ONE = machine.Pin(3, machine.Pin.OUT)
SWITCH_TWO = machine.Pin(4, machine.Pin.OUT)
SWITCH_THREE = machine.Pin(5, machine.Pin.OUT)
SWITCH_FOUR = machine.Pin(6, machine.Pin.OUT)

def ledOn():
    LED.value(1)

def ledOff():
    LED.value(0)

def switchOneOn():
    SWITCH_ONE.value(1)

def switchOneOff():
    SWITCH_ONE.value(0)

def switchTwoOn():
    SWITCH_TWO.value(1)

def switchTwoOff():
    SWITCH_TWO.value(0)

def switchThreeOn():
    SWITCH_THREE.value(1)

def switchThreeOff():
    SWITCH_THREE.value(0)

def switchFourOn():
    SWITCH_FOUR.value(1)

def switchFourOff():
    SWITCH_FOUR.value(0)

def reportSwitchState():
    switchStates = {
        "SWITCH_ONE": SWITCH_ONE.value(),
        "SWITCH_TWO": SWITCH_TWO.value(),
        "SWITCH_THREE": SWITCH_THREE.value(),
        "SWITCH_FOUR": SWITCH_FOUR.value()
    }
    return json.dumps(switchStates)