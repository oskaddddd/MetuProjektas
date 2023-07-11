from tkinter import *
import PIL.Image
import numpy as np
import json
import DotMatrixSmoother as dms
import time

imageName = ''
with open('ImageName.txt', 'r') as f:
    imageName = f.read()
    
    imageName = imageName[:imageName.index('.')+1]+'png' \
    if imageName[imageName.index('.')+1:] != 'png' \
    else imageName
    print(imageName)


cali = []
try:
    with open('CoordinateCalibration.json',) as f:
        cali = json.load(f)
        if cali == [[[0, 0], 0], [[0, 0], 0]]:
            #print('Please set 2 calibration coordinates in Calibration.py')
            exit()
        print(cali)
except:
    print('Please set 2 calibration coordinates in Calibration.py')
    exit()
cali[0]['GPS'].reverse()
cali[1]['GPS'].reverse()
print(cali)
k = [(cali[0]['Pixel'][0]-cali[1]['Pixel'][0])/(float(cali[0]['GPS'][0])-float(cali[1]['GPS'][0])),
     (cali[0]['Pixel'][1]-cali[1]['Pixel'][1])/(float(cali[0]['GPS'][1])-float(cali[1]['GPS'][1]))]
print(k)
b = [cali[0]['Pixel'][0]-(k[0]*float(cali[0]['GPS'][0])),
     cali[0]['Pixel'][1]-(k[1]*float(cali[0]['GPS'][1]))]
print(b)

def Decode(cords:list):
    return [round(float(cords[1])*k[0]+b[0]), round(float(cords[0])*k[1]+b[1])]

data = []
mapData = []

image = PIL.Image.open(imageName)
def ShowPoints():
    imageArr = np.array(image)
    for x in mapData:
        imageArr[x["Pixel"][1]][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]+1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]-1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]+1] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]-1] = [255, 0, 0, 255]
    PIL.Image.fromarray(imageArr).show()

def Smooth(points):
    t1 = time.time()
    points = [[x["Pixel"][0], x["Pixel"][1], x["Value"]] for x in points]
    
    m = max([x[2] for x in points])
    m = 255/m
    
    tri = dms.ravioliFindTriangles(np.array(points), showTriangles=True)
    imageArr = np.array(image)
    v = image.size[1]/100
    t = time.time()
    for i1, y in enumerate(imageArr):
        for i2, x in enumerate(y):
            if x[3] == 255:
                raw = dms.TestRunTri(tri, [i2, i1], test=True, setPoints=points)
                if raw!= None:
                    val = round(raw *m)
                    #print(val, 'adad')
                    if val < 0 and val > 255:
                        print(val)
                    imageArr[i1][i2] =  np.array([val, val, val, 255])
        if int(i1%v) == 0:
            p = round(i1//v)
            print(f"  {p}% [{'#'*int(p/5)}{'-'*int((100-p)/5)}]", '\033[F')
    print(time.time()-t, time.time()-t1)
    return np.array(np.uint8(imageArr))
    
with open('data.json', 'r') as f:
    data = json.load(f)
    print(data) 
for x in data:
    t = {}
    t["Pixel"] = Decode(x["GPS"])
    t["Value"] = x["Value"]
    if t["Pixel"][0] < image.size[0] and t["Pixel"][1] < image.size[1] and t["Pixel"][0] > 0 and t["Pixel"][1] > 0:
        mapData.append(t)
    print(t)
arr = Smooth(mapData)
PIL.Image.fromarray(arr).show()
print(mapData, 'waaaw')
ShowPoints()
    

root = Tk()

hello = Label(root, text="Hello world")  