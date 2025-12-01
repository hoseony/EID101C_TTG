from robot_hat import Pin, PWM
import time

ena = PWM("P10")
ena.freq(1000)
ena.pulse_width_percent(50)  # set motor A to 50% duty cycle

time.sleep(2)
ena.pulse_width_percent(0)
print("PWM test done")
