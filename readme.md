# Raspberry Pi Setup Summary

enable i2c

sudo apt install -y python3 python3-dev python3-pip build essential libffi-dev libssl-dev \
python3 -m venv venv \
source venv/bin/activate \
sudo apt install -y tesseract-ocr libtesseract-dev \
pip3 install pytesseract opencv-python-headless \
sudo apt install -y python3-rpi.gpio \
pip3 install gpiozero \
sudo apt install -y python3-smbus i2c-tools \
pip3 install adafruit-circuitpython-charlcd \
sudo apt install -y python3-picamera2 python3-libcamera libcamera-apps \
sudo apt install -y git

---

source venv/bin/activate
ssh thomasgeorge2@thomasgeorge2.local