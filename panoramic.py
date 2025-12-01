from robot_hat import Pin, PWM
import time
print("SCRIPT STARTED")
# Direction pins
in1 = Pin("D0")
in2 = Pin("D1")
in3 = Pin("D2")
in4 = Pin("D3")

# PWM pins
ena = PWM("P10")
enb = PWM("P11")
ena.freq(1000)
enb.freq(1000)

def motorA(speed):   # speed: -100 to 100
    if speed > 0:
        in1.on(); in2.off()
    elif speed < 0:
        in1.off(); in2.on()
    else:
        in1.off(); in2.off()
    ena.pulse_width_percent(abs(speed))

def motorB(speed):   # speed: -100 to 100
    if speed > 0:
        in3.on(); in4.off()
    elif speed < 0:
        in3.off(); in4.on()
    else:
        in3.off(); in4.off()
    enb.pulse_width_percent(abs(speed))

def stop_all():
    motorA(0)
    motorB(0)

# =====================
# Move for time
# =====================
def move(direction, seconds, speed):
    print(f"{direction} for {seconds} seconds at {speed}%")

    if direction == "forward":
        motorA(speed)
        motorB(speed)
    elif direction == "backward":
        motorA(-speed)
        motorB(-speed)
    else:
        print("Unknown direction")
        return
    
    time.sleep(seconds)
    stop_all()
    print("Done.\n")
print("setup over")
# =====================
# Demo
# =====================
if __name__ == "__main__":
    print("forward")
    move("forward", 2, 40)    # forward for 2 sec at 40% speed
    time.sleep(1)
    print("backwards")
    move("backward", 1.5, 30) # backward for 1.5 sec at 30% speed
    time.sleep(1)
    print("stop")
    stop_all()