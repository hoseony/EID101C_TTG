from RPLCD.i2c import CharLCD
import time

# Replace 0x27 with your detected address
lcd_address = 0x27  

# Initialize LCD
lcd = CharLCD('PCF8574', lcd_address, cols=16, rows=2)

try:
    lcd.write_string("Hello, Pi!")
    time.sleep(2)
    lcd.clear()
    
    # Scroll text example
    message = "I2C LCD Test on Raspberry Pi 4"
    for i in range(len(message) - 15):
        lcd.write_string(message[i:i+16])
        time.sleep(0.3)
        lcd.cursor_pos = (0,0)
        
finally:
    lcd.clear()
