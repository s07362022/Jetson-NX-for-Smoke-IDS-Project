# \file    peak_opencv.py
# \author  IDS Imaging Development Systems GmbH
# \date    2021-06-21
# \since   1.2.0
#
# \brief   This application demonstrates how to use the device manager to open a camera
#
# \version 1.0.0
#
# Copyright (C) 2021, IDS Imaging Development Systems GmbH.
#
# The information in this document is subject to change without notice
# and should not be construed as a commitment by IDS Imaging Development Systems GmbH.
# IDS Imaging Development Systems GmbH does not assume any responsibility for any errors
# that may appear in this document.
#
# This document, or source code, is provided solely as an example of how to utilize
# IDS Imaging Development Systems GmbH software libraries in a sample application.
# IDS Imaging Development Systems GmbH does not assume any responsibility
# for the use or reliability of any portion of this document.
#
# General permission to copy or modify is hereby granted.

def empty(a):
    pass

from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
import numpy as np
import cv2
import keyboard
'''
## HSV
cv2.namedWindow("TrackBars")
cv2.resizeWindow("TrackBars",640,240)
cv2.createTrackbar("Hue Min","TrackBars",89,179,empty)
cv2.createTrackbar("Hue Max","TrackBars",179,179,empty)
cv2.createTrackbar("Sat Min","TrackBars",39,255,empty)
cv2.createTrackbar("Sat Max","TrackBars",255,255,empty)
cv2.createTrackbar("Val Min","TrackBars",0,255,empty)
cv2.createTrackbar("Val Max","TrackBars",185,255,empty)
##
'''
p1,p2,p3,p4,p5,p6=[],[],[],[],[],[]

VERSION = "1.0.0"

def hsv_ids():
    print("open_camera Sample v" + VERSION)

    # initialize library
    ids_peak.Library.Initialize()

    # create a device manager object
    device_manager = ids_peak.DeviceManager.Instance()

    try:
        # update the device manager
        device_manager.Update()

        # exit program if no device was found
        if device_manager.Devices().empty():
            print("No device found. Exiting Program.")
            return

        # list all available devices
        for i, device in enumerate(device_manager.Devices()):
            print(str(i) + ": " + device.ModelName() + " ("
                  + device.ParentInterface().DisplayName() + "; "
                  + device.ParentInterface().ParentSystem().DisplayName() + "v."
                  + device.ParentInterface().ParentSystem().Version() + ")")

        # select a device to open
        selected_device = None
        while True:
            try:
                # selected_device = int(input("Select device to open: ")) #selected_device 輸入裝置
                selected_device =0
                if selected_device in range(len(device_manager.Devices())):
                    break
                else:
                    print("Invalid ID.")
            except ValueError:
                print("Please enter a correct id.")
                continue

        # open selected device
        device = device_manager.Devices()[selected_device].OpenDevice(ids_peak.DeviceAccessType_Control)

        # get the remote device node map
        nodemap_remote_device = device.RemoteDevice().NodeMaps()[0]

        # print model name and user ID
        print("Model Name: " + nodemap_remote_device.FindNode("DeviceModelName").Value())
        print("User ID: " + nodemap_remote_device.FindNode("DeviceUserID").Value())

        # print sensor information, not knowing if device has the node "SensorName"
        try:
            print("Sensor Name: " + nodemap_remote_device.FindNode("SensorName").Value())
        except ids_peak.Exception:
            print("Sensor Name: " + "(unknown)")

        # print resolution
        print("Max. resolution (w x h): "
              + str(nodemap_remote_device.FindNode("WidthMax").Value()) + " x "
              + str(nodemap_remote_device.FindNode("HeightMax").Value()))

        max_fps = nodemap_remote_device.FindNode("AcquisitionFrameRate").Maximum()
        nodemap_remote_device.FindNode("AcquisitionFrameRate").SetValue(max_fps)

        print("Max Framerate: " + str(max_fps))

        # open the data stream
        dataStream = device.DataStreams()[0].OpenDataStream()
        #allocate and announce image buffers
        payloadSize = nodemap_remote_device.FindNode("PayloadSize").Value()
        bufferCountMax = dataStream.NumBuffersAnnouncedMinRequired()
        for bufferCount in range(bufferCountMax):
            buffer = dataStream.AllocAndAnnounceBuffer(payloadSize)
            dataStream.QueueBuffer(buffer)

        # Get image information for opencv image format
        height = nodemap_remote_device.FindNode("Height").Value()
        width = nodemap_remote_device.FindNode("Width").Value()
        cvPixelFormat = cv2.CV_8U
        
        # prepare for untriggered continuous image acquisition
        nodemap_remote_device.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        nodemap_remote_device.FindNode("TriggerMode").SetCurrentEntry("On")
        nodemap_remote_device.FindNode("TriggerSource").SetCurrentEntry("Software")

        # start acquisition
        print("Image acquistion starting...")
        dataStream.StartAcquisition()
        nodemap_remote_device.FindNode("AcquisitionStart").Execute()

        # process the acquired images
        i = 0
        # while i < 100:

        cv2.namedWindow("TrackBars")
        cv2.resizeWindow("TrackBars",640,240)
        cv2.createTrackbar("Hue Min","TrackBars",89,179,empty)
        cv2.createTrackbar("Hue Max","TrackBars",179,179,empty)
        cv2.createTrackbar("Sat Min","TrackBars",39,255,empty)
        cv2.createTrackbar("Sat Max","TrackBars",255,255,empty)
        cv2.createTrackbar("Val Min","TrackBars",0,255,empty)
        cv2.createTrackbar("Val Max","TrackBars",185,255,empty)

        while (True):
            nodemap_remote_device.FindNode("TriggerSoftware").Execute()
            # get buffer from datastream 
            buffer = dataStream.WaitForFinishedBuffer(5000)

            raw_image = ids_peak_ipl.Image_CreateFromSizeAndBuffer(buffer.PixelFormat(), buffer.BasePtr(), buffer.Size(), buffer.Width(), buffer.Height())
            color_image = raw_image.ConvertTo(ids_peak_ipl.PixelFormatName_BGR8) #color format for U3-3680XCP-C
            #color_image = raw_image.ConvertTo(ids_peak_ipl.PixelFormatName_RGB8)
            # frmid = buffer.FrameID()
            # conver to numpy array
            np_image = color_image.get_numpy_3D()
            img = cv2.resize(np_image ,(400,400))

            imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
            h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
            s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
            s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
            v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
            v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
            #print(h_min,h_max,s_min,s_max,v_min,v_max)
            lower=np.array([h_min,s_min,v_min])
            upper=np.array([h_max,s_max,v_max])
            mask=cv2.inRange(imgHSV,lower,upper)
            imgResult = cv2.bitwise_and(img,img,mask=mask)
            cv2.imshow('image_ori', np_image)
            cv2.imshow("hsv",imgHSV)
            cv2.imshow("mask",mask)
            cv2.imshow("imgResult",imgResult)
            cv2.waitKey(1)
            # queue buffer
            dataStream.QueueBuffer(buffer)
            if cv2.waitKey(10) &keyboard.is_pressed("q"): #& 0xFF == ord('q'):
                break
            #frmid = buffer.FrameID()
            #i+=1
            #print(i)
            #print(frmid)
                        
            
    except Exception as e:
        print("Exception: " + str(e) + "")

    finally:
        cv2.destroyAllWindows()
        #p1.append(h_min)
        #p2.append(h_max)
        #p3.append(s_min)
        #p4.append(s_max)
        #p5.append(v_min)
        #p6.append(v_max)
        print("h_min,h_max,s_min,s_max,v_min,v_max",h_min,h_max,s_min,s_max,v_min,v_max)#,p1,p2,p3,p4,p5, p6)
        return h_min,h_max,s_min,s_max,v_min,v_max
        input("Press Enter to continue...")
        ids_peak.Library.Close()


#print(hsv_ids())
