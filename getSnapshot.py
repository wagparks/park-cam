import json
import subprocess
import os
from PIL import Image, ImageDraw, ImageFont


def getSnapshot(direction):
    with open(".webcamData.json") as dataFile:
        webcamsData = json.load(dataFile)
        
    for webcam in webcamsData:
        if webcam["name"] == direction:
            webcamData = webcam
            break
    
    snapshotCommand = 'curl --silent --digest -u ' \
        + webcamData["userid"] + ':' + webcamData["password"] \
        + ' http://' + webcamData["ipAddress"] + '/cgi-bin/snapshot.cgi -o snapshot.jpg'

    grab = os.system(snapshotCommand)
    
    camImage = Image.open('snapshot.jpg')
    
    left = 384
    top = 216
    right = 3840 - 384
    bottom = 2160 - 216

    # Cropped image of above dimension 
    # (It will not change original image) 
    cropImage = camImage.crop((left, top, right, bottom))
    newsize = (1024, 768)
    
    resizeImage = cropImage.resize(newsize)
    
    resizeImage.save("camImage.jpg")
    
    
    return("camImage.jpg")
    
    




if __name__ == "__main__":
    snapshotPicFile = getSnapshot()
    subprocess.run(['sudo', 'cp', snapshotPicFile, '/var/www/html/snapshot.jpg'])