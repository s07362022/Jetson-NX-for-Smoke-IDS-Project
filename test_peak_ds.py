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



from ids_peak import ids_peak
from ids_peak_ipl import ids_peak_ipl
import numpy as np
import cv2
# SQL
# import sql_01
import sql_02
#
# smoke process strat
import ds_class
base_img=cv2.imread("./smoke_base.jpg")
import keyboard
# smoke process end

VERSION = "1.0.0"

def test_sdls(h_min,s_min,v_min,h_max,s_max,v_max):
    print("open_camera Sample v" + VERSION)
    h_min,s_min,v_min,h_max,s_max,v_max=h_min,s_min,v_min,h_max,s_max,v_max
    # initialize library
    ids_peak.Library.Initialize()
    smoke_count =0
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
                # selected_device = int(input("Select device to open: ")) # 選擇裝置
                selected_device = 0
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
        import imutils
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
            np_image=cv2.resize(np_image,(680,600))
            # smoke process start
            try:
                frame,level_list = ds_class.ds(frame=np_image,smoke_count=smoke_count,h_min=h_min,s_min=s_min,v_min=v_min,h_max=h_max,s_max=s_max,v_max=v_max)
                print("h_min,h_max,s_min,s_max,v_min,v_max",h_min,h_max,s_min,s_max,v_min,v_max)
                smoke_count+=1
                cv2.imshow('image', imutils.resize(frame, width=460,height=460))
                if int(len(level_list))%5==0:
                    counts = np.bincount(level_list)
                    level_count = np.argmax(counts)       # 最終等級
                    level_mean = np.mean(level_list)
                    level_var = np.var(level_list,ddof=1)
                    level_std = np.std(level_list,ddof=1)
                    print("mean=",level_mean,"variance=",level_var)
                    ll=np.array(level_list)
                    y2 = [np.count_nonzero(ll==0),np.count_nonzero(ll==1),np.count_nonzero(ll==2),np.count_nonzero(ll==3),np.count_nonzero(ll==4),np.count_nonzero(ll==5)]
                    y2=np.array(y2)                       # 70張所有等級
                    # 另一張圖顯示70張影像最終之結果
                    str_base = "Level = %s  mean = %s var = %s".format(level_count,level_mean,level_var)
                    cv2.putText(base_img, str_base, (400,150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1, 2)
                    cv2.imshow("Level",base_img)
                    x1 = np.linspace(level_mean - 6*level_std, level_mean + 6*level_std, 100)
                    x2 = np.linspace(1,6,6)
                    y1=ds_class.normal_distribution(x=x1,mean=level_mean,var=level_var,level_std=level_std)
                    # 畫圖 normal dist, counts Bar
                    ds_class.draw(x1=x1,y1=y1)
                    ds_class.draw2(x2,y2)
                    # MySQL
                    # sql_01.insert(len(level_list),y2[0],y2[1],y2[2],y2[3],y2[4],y2[5],int(level_count),level_mean=level_mean,level_std=level_std)
                    # Influxdb
                    sql_02.in_sql(level_count)
                    
            # smoke process end
            except:
                cv2.imshow('image', imutils.resize(np_image, width=460,height=460))
            #cv2.imshow('image', np_image)
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
        nine=0
        return nine
        input("Press Enter to continue...")
        ids_peak.Library.Close()
        



