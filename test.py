import numpy as np
import serial
import cv2

sr = serial.Serial('/dev/ttyACM0',9600)
print sr.read()
while(True):
    sr.write('3')
    h = sr.readline()
    a = cv2.waitKey(100)
    sr.flushInput()
    if a=='a':
        cv2.imwrite('out.jpg',bin)
    if a==27:
        break

cv2.destroyAllWindows()
