# force_plate  

Program for force measurement of force plate using 6-axis force sensor  
force sensor: Leptrino FFS080YS102U6  

![IMG_5479](https://github.com/open-rdc/force_plate/assets/5755200/bf0a058e-21c4-4410-991e-aef468ef53ca)

## Environment  
Ubuntu1804  
python2.7  
python3.6  

## Install  

git clone https://github.com/open-rdc/force_plate  
pip install PyQt5 matplotlib

## Execute  

1) connect USB Cable L -> R  
3) Check if `/dev/ttyACM0` and `/dev/ttyACM1` exists  
3) cd force_plate
4) python force_plate.py
