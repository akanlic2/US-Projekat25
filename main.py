from machine import Pin
import time

# Pocetni debounce
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

# PINOVI
senzor = Pin(21, Pin.IN)
buzzer = Pin(19, Pin.OUT)

zelena = Pin(12, Pin.OUT)  
crvena = Pin(14, Pin.OUT) 

taster1 = Pin(0, Pin.IN)
taster2 = Pin(1, Pin.IN)

# PIN konfiguracija
VALID_PIN = "3110"
MAX_ATTEMPTS = 3
LOCK_TIME = 30  # sekundi
attempts = 0
pasivni_mod = True
promjenaPinaFlag = False


def led_mod(pasivni):
    if pasivni:
        zelena.on()
        crvena.off()
        
    else:
        zelena.off()
        crvena.on()


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
        if key and key in '0123456789':
            entered += key
            print("*", end="")# maskirani unos
            time.sleep(0.3)
        time.sleep(0.05)
    print()# novi red
    return entered


def deaktivacija():
    global attempts, pasivni_mod

    print("POKRET DETEKTOVAN! Aktiviran alarm.")
    buzzer.on()

    while True:
        print("Unesi PIN za deaktivaciju: ")
        pin = enter_pin()

        if pin == VALID_PIN:
            print("PIN tačan! Alarm deaktiviran.")
            buzzer.off()
            attempts = 0
            pasivni_mod = True
            led_mod(True)
            break
        else:
            attempts += 1
            print(f"Pogrešan PIN! Preostalo pokušaja: {MAX_ATTEMPTS - attempts}")
            if attempts >= MAX_ATTEMPTS:
                print(f"Previše pokušaja. Sistem zaključan na {LOCK_TIME} sekundi.")
                time.sleep(LOCK_TIME)
                attempts = 0

    time.sleep(0.05)


def promijeni_pin(pin):
    global promjenaPinaFlag
    promjenaPinaFlag = True

    
def promjenaPina():
    global VALID_PIN,promjenaPinaFlag,pasivni_mod

    print("Unesi trenutni PIN:")
    stari = enter_pin()
    if stari != VALID_PIN:
        print("Netačan trenutni PIN. Promjena nije dozvoljena.")
        print("PASIVNI MOD")
        promjenaPinaFlag = False
        pasivni_mod = True
        return

    print("Unesi novi PIN:")
    novi = enter_pin()

    print("Potvrdi novi PIN:")
    potvrda = enter_pin()

    if novi == potvrda:
        VALID_PIN = novi
        print("PIN uspješno promijenjen!")
        print("PASIVNI MOD")
        promjenaPinaFlag = False
    else:
        print("PIN-ovi se ne poklapaju. Promjena otkazana.")
        promjenaPinaFlag = False
        print("PASIVNI MOD")

    pasivni_mod = True
       



def aktivniMod(pin):
    global pasivni_mod
    pasivni_mod = False
    

    
led_mod(True)
print("PASIVNI MOD")

taster1.irq(handler = aktivniMod,trigger = Pin.IRQ_RISING)
taster2.irq(handler = promijeni_pin,trigger = Pin.IRQ_RISING)

while True:

    if pasivni_mod and promjenaPinaFlag:
        print("PROMJENA PINA POKRENUTA...")
        promjenaPina()
    elif not pasivni_mod:
        print("AKTIVNI MOD")
        led_mod(pasivni_mod)
        while True:
            if senzor.value() == 1:
                # Ako je alarm aktiviran i senzor detektuje pokret
                deaktivacija()
                time.sleep(0.05)
                print("PASIVNI MOD")
                promjenaPinaFlag=False
                break

        time.sleep(0.05)

    
    time.sleep(0.005)
   

    
    
