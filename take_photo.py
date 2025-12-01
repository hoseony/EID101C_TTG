# ...existing code...
from picamera2 import Picamera2
from time import sleep
from datetime import datetime
from libcamera import controls

picam = Picamera2()

config = picam.create_still_configuration({"size": (4608, 2592)})
picam.configure(config)

picam.start()
sleep(0.5)

picam.set_controls({
    "AfMode": controls.AfModeEnum.Auto,
    "AfRange": controls.AfRangeEnum.Normal,
    "AfSpeed": controls.AfSpeedEnum.Fast,
 })

picam.autofocus_cycle()

sleep(0.2)
def capture_photo():
    """
    Capture a still image and return the filename.
    Keeps the original behavior when run as script.
    """
    global picam  # reuse configured picam instance above
    # if picam isn't started/configured for some reason, configure minimally
    try:
        _ = picam
    except NameError:
        picam = Picamera2()
        config = picam.create_still_configuration({"size": (4608, 2592)})
        picam.configure(config)

    picam.start()
    sleep(0.5)
    try:
        picam.set_controls({
            "AfMode": controls.AfModeEnum.Auto,
            "AfRange": controls.AfRangeEnum.Normal,
            "AfSpeed": controls.AfSpeedEnum.Fast,
        })
        picam.autofocus_cycle()
        sleep(0.2)
    except Exception:
        pass

    filename = datetime.now().strftime("image_%Y-%m-%d_%H-%M-%S.jpg")
    picam.capture_file(filename)
    picam.stop()
    print(f"Photo saved: {filename}")
    return filename

if __name__ == "__main__":
    capture_photo()