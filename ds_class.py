import cv2
import time

CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

class_names = []
with open("yolo.names", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

net = cv2.dnn.readNet("yolov4-tiny-3l_best.weights", "yolov4-tiny-3l.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

smoke_count = 0
## smoke process
from level_3 import tem, convert_temp,mask_img,leavel
def cut_img(image, classes, confs, boxes):
    cut_img_list = []
    for (classid, conf, box) in zip(classes, confs, boxes):
        x, y, w, h = box
        if x - 20 < 0:
            x = 21
        if y - 20 < 0:
            y = 21
        #cut_img = image[y - 30:y + h + 30, x - 18:x + w + 25]
        cut_img = image[y - 20: y + h + 30, x - 10: x + w + 10]
        cut_img_list.append(cut_img)
    return cut_img_list[0]

kelvin_table = {
    1000: (255,56,0),
    1500: (255,109,0),
    2000: (255,137,18),
    2500: (255,161,72),
    3000: (255,180,107),
    3500: (255,196,137),
    4000: (255,209,163),
    4500: (255,219,186),
    5000: (255,228,206),
    5500: (255,236,224),
    6000: (255,243,239),
    6500: (255,249,253),
    7000: (245,243,255),
    7500: (235,238,255),
    8000: (227,233,255),
    8500: (220,229,255),
    9000: (214,225,255),
    9500: (208,222,255),
    10000: (204,219,255)}
leavel_list = []
font = cv2.FONT_HERSHEY_PLAIN

# distribution
import math
import numpy as np
import plotly.graph_objects as go
def normal_distribution(x, mean, var, level_std):
    return np.exp(-1*(abs(x-mean)**2)/(2*(var)))/(math.sqrt(2*np.pi) * (level_std))

def draw(x1,y1):
    trace0 = go.Scatter(
        x=x1,
        y=y1,
        mode='markers',#+text
        name="normal_distribution",
        text=y1,
        textposition="top left",
        hovertemplate="<b>%{x}</b> 平均級別<br><b>%{y}</b> 常態分布級別",
    )
    fig = go.Figure([trace0])
    fig.update_layout(
        title_text='排放廢氣煙霧之等級畫分',
        title_font_size=30,
        title_x=0.5,
        xaxis_title="常態分布",
        xaxis_tickmode="linear",
        yaxis_title="等級",
        showlegend=True,
    )
    fig.show()
def draw2(x2,y2):
    trace1 = go.Bar(
            x=x2,
            y=y2,
            #+text,mode='markers'
            name="Bar",
            text=y2,
            textposition="outside",
            hovertemplate="<b>%{x}</b> 級別類別<br><b>%{y}</b> 等級",
        )
    fig = go.Figure([trace1])
    fig.update_layout(
        title_text='排放廢氣煙霧之等級畫分',
        title_font_size=30,
        title_x=0.5,
        xaxis_title="級別類別",
        xaxis_tickmode="linear",
        yaxis_title="等級",
        showlegend=True,
    )
    fig.show()
#
# save ori_image path
path_name="E:\\workspace\\project_\\dimg"
##

def ds(frame, smoke_count,h_min,s_min,v_min,h_max,s_max,v_max):
    start = time.time()
    classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    end = time.time()


    start_drawing = time.time()

    for (classid, score, box) in zip(classes, scores, boxes):
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %f" % (class_names[classid[0]], score)
        # smoke process
        if classes[0][0] == 0:
            cut = cut_img(frame, classes, scores, boxes)
            #print(classes[0][0])
            #smoke_count +=1
            #print(smoke_count)

            # 這裡(smoke_count)調整秒數 不確定所要要做實驗
            if smoke_count % 1 ==0:
                #print("smoke")
                smoke_img = cv2.resize(cut,(400,400))
                mask = tem(smoke_img,h_min,s_min,v_min,h_max,s_max,v_max)               
                ori,black  = mask_img(mask,smoke_img)
                cv2.imshow("ori",mask)
                
                # compute Level
                global smoke_level_re
                smoke_level_re = leavel(black,ori)
                leavel_list.append(smoke_level_re)
                print("判斷黑煙等級: {} ".format(smoke_level_re))
                global smoke_level_str
                smoke_level_str="Detected Smoke Leveal: "+str(smoke_level_re)
                # dimg
                img_name = '%s//%d.jpg'%(path_name, smoke_count)
                cv2.imwrite(img_name,smoke_img)
                # dimg
                
                    
                
    
        x,y,w,h = box[0],box[1],box[2],box[3]
        cv2.rectangle(frame, (x,y), (x+w,y+h), color, 1)
        cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    end_drawing = time.time()
    
    fps_label = "FPS: %.2f (excluding drawing time of %.2fms)" % (1 / (end - start), (end_drawing - start_drawing) * 1000)
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    try:
        cv2.putText(frame,smoke_level_str,(50, 50 -5), font, 2, [0,25,220], 1)
    except:
        pass
    return frame,leavel_list