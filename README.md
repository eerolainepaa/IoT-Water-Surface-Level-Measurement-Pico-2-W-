# IoT Water Surface Level Measurement System using Pico 2 W

This is a self-designed and implemented IoT project that measures water surface level using a Raspberry Pi Pico 2 W and a potentiometer.

The goal of the project was to combine embedded programming, hardware design, and data visualization into a single working system.

---

## 🔧 Features

- Measures water level using a potentiometer  
- Reads analog values with Pico 2 W  
- Displays data:
  - on a local display  
  - in a web browser (using pico as a server) 
- Real-time measurement  

The potentiometer acts as a variable resistor, producing an analog signal that is read by the microcontroller.

---

## 🧠 How It Works

- The potentiometer simulates water level changes (analog signal)  
- Raspberry Pi Pico 2 W reads the value via ADC  
- The value is processed into usable data  
- Data is displayed:
  - on a physical display  
  - through a web interface

---

## 🛠️ Technologies

- MicroPython  
- Raspberry Pi Pico 2 W  
- Potentiometer (analog input)  
- HTML (simple web UI)  
- Built-in HTTP server (Pico W)

---

## 📦 Hardware

- Raspberry Pi Pico 2 W  
- Potentiometer  
- Breadboard and jumper wires  
- (Optional) display

## Circuit Diagram
<img width="692" height="384" alt="Diagram" src="https://github.com/user-attachments/assets/dbb6b8da-3938-4d2d-a7c3-d5908909b499" />

