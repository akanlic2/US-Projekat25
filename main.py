from machine import Pin
import time

#pocetni debounce
time.sleep(0.05)

# GPIO pinovi povezani na redove tastature (R1-R4)
row_pins = [Pin(16, Pin.OUT), Pin(15, Pin.OUT), Pin(17, Pin.OUT), Pin(18, Pin.OUT)]

# GPIO pinovi povezani na kolone tastature (C1-C4)
col_pins = [Pin(9, Pin.IN, Pin.PULL_DOWN), Pin(10, Pin.IN, Pin.PULL_DOWN), 
            Pin(11, Pin.IN, Pin.PULL_DOWN), Pin(13, Pin.IN, Pin.PULL_DOWN)]

# Mapa tastera [red][kolona]
keypad = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

senzor = Pin(21,Pin.IN)
buzzer = Pin(19,Pin.OUT)

VALID_PIN = "3110"
MAX_ATTEMPTS = 3
LOCK_TIME = 30  # sekundi


def scan_keypad():
    for row in range(4):
        # Aktiviraj samo trenutni red
        for r in range(4):
            row_pins[r].value(1 if r == row else 0)

        for col in range(4):
            if col_pins[col].value():
                return keypad[row][col]
    return None
    
def enter_pin():
    entered = ""
    while len(entered) < 4:
        key = scan_keypad()
        if key:
            if key in '0123456789':
                entered += key
                print("*", end="")  # maskirani unos
                time.sleep(0.1)
        time.sleep(0.05)
    print()  # novi red
    return entered


attempts = 0

print("Sistem je pasivan. Čeka pokret...")

while True:

    if(senzor.value() == 1):
        print("POKRET DETEKTOVAN! Aktiviran alarm.")
        buzzer.on()

        while True:
            print("Unesi PIN za deaktivaciju: ")
            pin = enter_pin()

            if pin == VALID_PIN:
                print("PIN tačan! Alarm deaktiviran.")
                buzzer.off()
                attempts = 0
                break
            else:
                attempts += 1
                print(f"Pogrešan PIN! Preostalo pokušaja: {MAX_ATTEMPTS - attempts}")
                if attempts >= MAX_ATTEMPTS:
                    print(f"Previše pokušaja. Sistem zaključan na {LOCK_TIME} sekundi.")
                    time.sleep(LOCK_TIME)
                    attempts = 0
            time.sleep(0.05)

    time.sleep(0.05)
    
   
    