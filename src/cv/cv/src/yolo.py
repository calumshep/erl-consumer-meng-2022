#!/usr/bin/python

# YOLO code initially adapted from https://www.codespeedy.com/yolo-object-detection-from-image-with-opencv-and-python/

import cv2
import numpy as np
import rospkg

class Yolo:
    def __init__(self):
        self.yolo_path = rospkg.RosPack().get_path('cv')+"/yolo/"
        self.init_yolo()
        
    def init_yolo(self):
        #Load YOLO Algorithm
        self.net=cv2.dnn.readNet(self.yolo_path+"yolov3.weights",self.yolo_path+"yolov3.cfg")
        #To load all objects that have to be detected
        self.classes=[]
        with open(self.yolo_path+"coco.names","r") as f:
            read=f.readlines()
        for i in range(len(read)):
            self.classes.append(read[i].strip("\n"))
        #Defining layer names
        self.layer_names=self.net.getLayerNames()
        self.output_layers=[]
        for i in self.net.getUnconnectedOutLayers():
            self.output_layers.append(self.layer_names[i[0]-1])

    def search_for_objects(self,img):
        height,width,channels=img.shape
        #Extracting features to detect objects
        blob=cv2.dnn.blobFromImage(img,0.00392,(416,416),(0,0,0),True,crop=False)
                                                                #Inverting blue with red
                                                                #bgr->rgb
        #We need to pass the img_blob to the algorithm
        self.net.setInput(blob)
        outs=self.net.forward(self.output_layers)
        #print(outs)
        #Displaying informations on the screen
        class_ids=[]
        confidences=[]
        boxes=[]
        for output in outs:
            for detection in output:
                #Detecting confidence in 3 steps
                scores=detection[5:]                #1
                class_id=np.argmax(scores)          #2
                confidence =scores[class_id]        #3
                if confidence >0.5: #Means if the object is detected
                    center_x=int(detection[0]*width)
                    center_y=int(detection[1]*height)
                    w=int(detection[2]*width)
                    h=int(detection[3]*height)
                    #Drawing a rectangle
                    x=int(center_x-w/2) # top left value
                    y=int(center_y-h/2) # top left value
                    boxes.append([x,y,w,h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        #Removing Double Boxes
        indexes=cv2.dnn.NMSBoxes(boxes,confidences,0.3,0.4)
        semantic_points=[]
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = self.classes[class_ids[i]]  # name of the objects
                img = self.draw_obj(img,label,x,y,w,h,(0,255,0))
                
                centerX,centerY = self.get_center_coords(x,y,w,h)

                point_dict={}
                point_dict["Point"]=[centerX,centerY]
                point_dict["Label"]=label
                semantic_points.append(point_dict)

        return semantic_points,img # Returns array of dictionaries consisting of Point and Label, and processed image.

    def get_center_coords(self,x,y,w,h):
        return int(x+0.5*w),int(y+0.5*h)

    def draw_obj(self,img,label, x,y,w,h,colour):
        cv2.rectangle(img, (x, y), (x + w, y + h), colour, 2)
        cv2.putText(img, label, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, colour, 2)
        
        # Draw center marker
        center_x,center_y = self.get_center_coords(x,y,w,h)
        cv2.circle(img, (center_x,center_y), radius=5, color=(0, 0, 255), thickness=-1)

        return img

    def is_target_obj(self,obj):
        return obj == self.target
