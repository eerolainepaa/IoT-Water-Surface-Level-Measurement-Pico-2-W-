import time
import urequests
import json
from machine import I2C, Pin, ADC
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# LCD-settings
I2C_ADDR     = 39
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Sensors
adc_voltage = ADC(Pin(26))
adc_temp = ADC(Pin(27))
button = Pin(15, Pin.IN, Pin.PULL_UP)

# LED
led = Pin("LED", Pin.OUT)

# Calibration
a = 22.222
b = -33.56
V0C = 0.4
TC = 0.0195
DEBOUNCE = 50

# BACKEND-SETTINGS
# --- CHANGE THIS TO YOUR IP! ---
BACKEND_URL = "http://192.168.0.140:5000/api/measurement"
SEND_INTERVAL = 5  # Send data every n seconds

# Zero
zero_point = None
last_send_time = 0
lcd.clear()


# Read average voltage from sensor
def read_average_voltage(samples, delay):
    total = 0
    for _ in range(samples):
        total += adc_voltage.read_u16()
        time.sleep_ms(delay)
    return total / samples * 3.3 / 65535

# Change voltage to height
def voltage_to_height(voltage):
    if zero_point is None:
        height = a * voltage + b
    else:
        delta_v = voltage - zero_point
        height = delta_v * a
    return round(height, 1)

# Read temperature
def read_temperature():
    raw_temp = adc_temp.read_u16()
    temperature = (((raw_temp / 65535) * 3.3) - V0C) / TC
    return round(temperature, 1)

# Check if reset button pressed
def check_button():
    global zero_point
    if button.value() == 0:
        time.sleep_ms(DEBOUNCE)  # Debounce
        if button.value() == 0:
            zero_point = read_average_voltage(30, 20)
            lcd.clear()
            lcd.putstr("NOLLAUS TEHTY")
            time.sleep(1.5)
            return True
    return False

# Send data to backend
def send_to_backend(height, temperature, voltage):
    try:
        data = {
            "height": height,
            "temperature": temperature,
            "voltage": voltage
        }
        
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(BACKEND_URL, json=data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            response.close()
            
            # Check alerts
            if result.get('alerts'):
                return result['alerts']
            return []
        else:
            print(f"Backend virhe: {response.status_code}")
            response.close()
            return None
            
    except Exception as e:
        print(f"Virhe lähetettäessä dataa: {e}")
        return None

# Blink LED for alert
def blink_alert_led(times=3):
    for _ in range(times):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)

# Show alert on LCD
def show_alert_on_lcd(alert_count):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("HALYTYS!")
    lcd.move_to(0, 1)
    lcd.putstr(f"{alert_count} halytyst")
    time.sleep(2)

# Main loop
print("Mittausjärjestelmä käynnissä")
lcd.clear()
lcd.putstr("Jarjestelma")
lcd.move_to(0, 1)
lcd.putstr("kaynnissa...")
time.sleep(2)

while True:
    try:
        # Check if reset button pressed
        if check_button():
            continue
        
        # Read sensor data
        avg_voltage = read_average_voltage(30, 20)
        height = voltage_to_height(avg_voltage)
        temperature = read_temperature()
        
        # Show data on LCD
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(f"Korkeus:{height:2.1f}cm")
        lcd.move_to(0, 1)
        lcd.putstr(f"Lampo: {temperature}C")
        
        # Send data to backend
        current_time = time.time()
        if current_time - last_send_time >= SEND_INTERVAL:
            print(f"Lähetetään: H={height}cm, T={temperature}C")
            
            alerts = send_to_backend(height, temperature, avg_voltage)
            
            if alerts is not None:
                print("Data lähetetty onnistuneesti")
                
                # Check for alerts
                if len(alerts) > 0:
                    print(f"HÄLYTYKSIÄ: {len(alerts)}")
                    for alert in alerts:
                        print(f"  - {alert['message']}")
                    
                    blink_alert_led(len(alerts))
                    show_alert_on_lcd(len(alerts))
            else:
                print("Virhe lähetettäessä dataa")
                # Show alert on LCD
                lcd.clear()
                lcd.putstr("Lahetysvirhe")
                time.sleep(1)
            
            last_send_time = current_time

        time.sleep(1) # Wait 1s before next measurement
        
    except Exception as e:
        print(f"Virhe pääsilmukassa: {e}")
        lcd.clear()
        lcd.putstr("VIRHE!")
        lcd.move_to(0, 1)
        lcd.putstr(str(e)[:16])
        time.sleep(2)