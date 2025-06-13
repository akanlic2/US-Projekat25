from machine import Pin,SPI,PWM
import time
from ili934xnew import ILI9341, color565
import tt24

# Pocetni debounce
time.sleep(0.05)

#TFT displej
TFT_CLK_PIN = 18
TFT_MOSI_PIN = 19
TFT_MISO_PIN = 16
TFT_CS_PIN = 17
TFT_RST_PIN = 20
TFT_DC_PIN = 15

spi = SPI(
    0,
    baudrate=62500000,
    miso=Pin(TFT_MISO_PIN),
    mosi=Pin(TFT_MOSI_PIN),
    sck=Pin(TFT_CLK_PIN))

display = ILI9341(
    spi,
    cs=Pin(TFT_CS_PIN),
    dc=Pin(TFT_DC_PIN),
    rst=Pin(TFT_RST_PIN),
    w=320,
    h=240,
    r=2)

display.init()

def displayMessage(msg):
    display.erase()
    display.set_font(tt24)
    display.set_color(color565(255, 255, 255), color565(0, 0, 0))
    display.set_pos(10, 50)
    display.print(msg)
    time.sleep(0.5)

# GPIO pinovi povezani na redove tastature (R1-R4)
row_pins = [Pin(21, Pin.OUT), Pin(22, Pin.OUT), Pin(26, Pin.OUT), Pin(27, Pin.OUT)]

# GPIO pinovi povezani na kolone tastature (C1-C4)
col_pins = [Pin(0, Pin.IN, Pin.PULL_DOWN), Pin(1, Pin.IN, Pin.PULL_DOWN),
            Pin(2, Pin.IN, Pin.PULL_DOWN), Pin(3, Pin.IN, Pin.PULL_DOWN)]


# Mapa tastera [red][kolona]
keypad = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# PINOVI
senzor = Pin(7, Pin.IN)
buzzer = PWM(Pin(28))

buzzer.freq(2300)
buzzer.duty_u16(0)


zelena = Pin(12, Pin.OUT)  
crvena = Pin(14, Pin.OUT)

taster1 = Pin(10, Pin.IN, Pin.PULL_DOWN)
taster2 = Pin(13, Pin.IN, Pin.PULL_DOWN)

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
                key = keypad[row][col]
                time.sleep(0.1)
                while col_pins[col].value():
                    time.sleep(0.01)
                return key
    return None


def enter_pin():
    entered = ""
    while len(entered) < 4:
        key = scan_keypad()
        if key and key in '0123456789':
            entered += key
            displayMessage("Unos: " + "*" *len(entered))# maskirani unos
    print()# novi red
    return entered


def deaktivacija():
    global attempts, pasivni_mod

    displayMessage("POKRET DETEKTOVAN! Aktiviran alarm.")
    buzzer.duty_u16(32767)

    while True:
        displayMessage("Unesi PIN za deaktivaciju: ")
        pin = enter_pin()

        if pin == VALID_PIN:
            displayMessage("PIN tacan! Alarm deaktiviran.")
            buzzer.duty_u16(0)
            attempts = 0
            pasivni_mod = True
            led_mod(True)
            break
        else:
            attempts += 1
            displayMessage("Pogresan PIN! Preostalo pokusaja: " + str(MAX_ATTEMPTS - attempts))
            if attempts >= MAX_ATTEMPTS:
                displayMessage("Previse pokusaja. Sistem zakljucan na 30 sekundi.")
                time.sleep(LOCK_TIME)
                attempts = 0

    time.sleep(0.05)


def promijeni_pin(pin):
    global promjenaPinaFlag
    promjenaPinaFlag = True

   
def promjenaPina():
    global VALID_PIN,promjenaPinaFlag,pasivni_mod

    displayMessage("Unesi trenutni PIN:")
    stari = enter_pin()
    if stari != VALID_PIN:
        displayMessage("Netacan trenutni PIN. Promjena nije dozvoljena.")
        displayMessage("PASIVNI MOD")
        promjenaPinaFlag = False
        pasivni_mod = True
        return

    displayMessage("Unesi novi PIN:")
    novi = enter_pin()

    displayMessage("Potvrdi novi PIN:")
    potvrda = enter_pin()

    if novi == potvrda:
        VALID_PIN = novi
        displayMessage("PIN uspjesno promijenjen!")
        displayMessage("PASIVNI MOD")
        promjenaPinaFlag = False
    else:
        displayMessage("PIN-ovi se ne poklapaju. Promjena otkazana.")
        promjenaPinaFlag = False
        displayMessage("PASIVNI MOD")

    pasivni_mod = True
       



def aktivniMod(pin):
    global pasivni_mod
    pasivni_mod = False
   

   
led_mod(True)
displayMessage("PASIVNI MOD")

taster1.irq(handler = aktivniMod,trigger = Pin.IRQ_RISING)
taster2.irq(handler = promijeni_pin,trigger = Pin.IRQ_RISING)

while True:

    if pasivni_mod and promjenaPinaFlag:
        displayMessage("PROMJENA PINA POKRENUTA...")
        promjenaPina()
    elif not pasivni_mod:
        displayMessage("AKTIVNI MOD")
        led_mod(pasivni_mod)
        while True:
            if senzor.value() == 1:
                # Ako je alarm aktiviran i senzor detektuje pokret
                deaktivacija()
                time.sleep(0.05)
                displayMessage("PASIVNI MOD")
                promjenaPinaFlag=False
                break

        time.sleep(0.05)

   
    time.sleep(0.005)

