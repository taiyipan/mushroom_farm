import numpy as np
import cv2 as cv
import time
from time import sleep
from datetime import datetime
from pySerialTransfer import pySerialTransfer as txfer
import pandas as pd 
import sys
import os

port = 'ttyACM0'

class struct(object):
    soilMoisture = -1
    temp = -1
    humidity = -1 
    envTemp = -1 
    envHumidity = -1 

def read_sensors(argv):
    try:
        # initiate serial communication with Arduino microcontroller
        data = struct
        link = txfer.SerialTransfer(port=port)
        
        link.open()
        sleep(5)

        # create pandas dataframe
        fname = ''.join(['log/', datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f'), '.csv'])
        df = pd.DataFrame(data=None, index=None, columns=[
            'Timestamp', 
            'Soil_Moisture(%)', 
            'Temperature(C)', 
            'Humidity(%)', 
            'Environment_Temperature(C)',
            'Environment_Humidity(%)'])
        print(df.head())

        # define variables
        cam_port = int(argv[1])
        width = 640
        height = 480

        # open camera object
        cam = cv.VideoCapture(cam_port)
        cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        prev_frame_time, new_frame_time = time.time(), time.time()

        # graceful fail
        if not cam.isOpened():
            print('Cannot open camera...')
            exit()

        # create img directory 
        if not os.path.exists('./img'):
            os.mkdir('./img')
        # create log directory 
        if not os.path.exists('./log'):
            os.mkdir('./log')

        # main control loop
        count = 0
        while True:
            # obtain timestamp 
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
            # obtain frame
            ret, frame = cam.read()
            if not ret:
                print('Failed to obtain frame')
                break

            # flip frame
            # frame = cv.flip(frame, 0)

            # receive serial data package 
            if link.available():
                print('---------------------------------------')
                print(timestamp)
                
                recSize = 0
                
                data.soilMoisture = link.rx_obj(obj_type='l', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['l']
                print('Soil moisture: {}%'.format(data.soilMoisture))

                data.temp = link.rx_obj(obj_type='l', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['l']
                print('Temperature: {}C'.format(data.temp))

                data.humidity = link.rx_obj(obj_type='l', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['l']
                print('Humidity: {}%'.format(data.humidity))

                data.envTemp = link.rx_obj(obj_type='l', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['l']
                print('Environment Temperature: {}C'.format(data.envTemp))

                data.envHumidity = link.rx_obj(obj_type='l', start_pos=recSize)
                recSize += txfer.STRUCT_FORMAT_LENGTHS['l']
                print('Environment Humidity: {}%'.format(data.envHumidity))

            elif link.status < 0:
                if link.status == txfer.CRC_ERROR:
                    print('ERROR: CRC_ERROR')
                elif link.status == txfer.PAYLOAD_ERROR:
                    print('ERROR: PAYLOAD_ERROR')
                elif link.status == txfer.STOP_BYTE_ERROR:
                    print('ERROR: STOP_BYTE_ERROR')
                else:
                    print('ERROR: {}'.format(link.status))

            # read sensors once per minute 
            count += 1 
            if count >= 30*60:
                cv.imwrite('img/{}.jpg'.format(timestamp), frame)
                count = 0 
                print('Image saved at {}'.format(timestamp))

                # add sensor readings to dataframe and save to csv 
                df.loc[len(df.index)] = [
                    timestamp,
                    data.soilMoisture,
                    data.temp,
                    data.humidity,
                    data.envTemp,
                    data.envHumidity
                ]
                df.to_csv(fname, index=False)
                print('CSV saved at {}'.format(fname))

            # calculate fps
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time
            # add annotations
            cv.putText(frame, 'Cam {} fps: {}'.format(cam_port, str(int(fps))), (30, 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv.putText(frame, 'Time: {}'.format(datetime.now()), (30, 50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # display frame
            cv.imshow('frame', frame)

            # escape protocol
            k = cv.waitKey(1)
            if k%256 == 27: # ESC pressed
                print('Escaping...')
                break

        # cleanup
        cam.release()
        cv.destroyAllWindows()

    except KeyboardInterrupt:
        link.close()

def main(argv):
    read_sensors(argv)

if __name__ == '__main__':
    main(sys.argv)
