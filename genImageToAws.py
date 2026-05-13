import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import boto3
from getWeather import getWeather
from getSnapshot import getSnapshot

def opaqueBox_on_jpeg(image_path, output_path, box_coords, fill_color):
    # Open the image
    img = Image.open(image_path).convert("RGBA")

    # Create an overlay for drawing
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)


    # Draw the opaque rectangle
    draw.rectangle(box_coords, fill=fill_color)

    # Alpha composite the overlay onto the original image
    combined_img = Image.alpha_composite(img, overlay)

    # Convert to RGB for saving as JPEG
    final_img = combined_img.convert("RGB")

    # Save the modified image
    final_img.save(output_path)

def text_on_jpeg(image_path, text, output_path, font_path, font_size, text_color, position):
    # Writes text on a JPEG image.

    # Args:
    #     image_path: Path to the JPEG image.
    #     text: The text to write.
    #     output_path: Path to save the modified image.
    #     font_path: Path to the font file (optional).  If None, a default font is used.
    #     font_size: Size of the font in points.
    #     text_color: Color of the text as an RGB tuple (e.g., (0, 0, 0) for black).
    #     position: (x, y) coordinates of the text's top-left corner.
    
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        if font_path:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                print(f"Could not load font {font_path}. Using default font.")
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()
        draw.text(position, text, font=font, fill=text_color)
        img.save(output_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        

def main():
    
    now = datetime.now()
    picFormattedString = now.strftime("%b-%d-%Y %H:%M")
    
    with open('lastImage.txt', 'r') as file:
        lastPicDirection = file.readline()
        
    with open('.webcamData.json', 'r') as file:
        webCamData = json.load(file)
        
    for webCam in webCamData:
        if webCam["name"] != lastPicDirection:
            picDirection = webCam["name"]
            awsFileName = webCam["awsUploadImageName"]
            with open('lastImage.txt', 'w') as file:
                file.writelines(picDirection)
            break
    
    
    imagePath = getSnapshot(picDirection)
    outputPath = "writeDemo-" + now.strftime("%s") +".jpeg"
     
    
    # create opaque top box
    boxCoords = (0, 0, 600, 85)
    fillColor = (0, 0, 0, 128)
    opaqueBox_on_jpeg(imagePath, outputPath, boxCoords, fillColor)
    
    imagePath = outputPath
    
    
    # create opaque bottom box
    boxCoords = (0, 700, 400, 900)
    fillColor = (255, 255, 255, 128)
    opaqueBox_on_jpeg(imagePath, outputPath, boxCoords, fillColor)
    
    # write text

    text = "Whitefish Montana Dog Park"
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_size = 30
    text_color = (255, 255, 255)
    position = (10, 10)
    text_on_jpeg(imagePath, text, outputPath, font_path, font_size, text_color, position)
    
    font_size = 20
    position = (10, 50)
    text = "www.whitefishdogpark.org. Instagram: @whitefishdogpark"
    text_on_jpeg(imagePath, text, outputPath, font_path, font_size, text_color, position)
    font_size = 20
    text_color = (0, 0, 0)
    position = (10, 700)
    stationWeatherData = getWeather()
    stationTemp = str(stationWeatherData["temperature"])
    stationWindSpeed = str(stationWeatherData["windSpeed"])
    stationWindDir = str(stationWeatherData["windDirection"])
    stationPrecipToday = str(stationWeatherData["precToday"])
    stationUv = str(stationWeatherData["uv"])
    stationFeelsLike = str(stationWeatherData["feelsLike"])
    text = "Temp: " + stationTemp + "F Wind: " + stationWindSpeed + "mph " + stationWindDir + "\nToday's Prec: " + stationPrecipToday + "in. Feels Like: " + stationFeelsLike +  "F\n" + picFormattedString
    text_on_jpeg(imagePath, text, outputPath, font_path, font_size, text_color, position)
    
    # copy files to local web server
    
    subprocess.run(["sudo", "cp", outputPath, "/var/www/html/"])
    subprocess.run(["sudo", "unlink", "/var/www/html/writeDemo.jpeg"])
    subprocess.run(["sudo", "ln", "-s",  "/var/www/html/" + outputPath, "/var/www/html/writeDemo.jpeg"])
    
    
    #copy files to s3
    
    s3 = boto3.resource('s3')
    s3Bucket = "whitefish-dog-park-cam"

    # s3.Bucket(s3Bucket).upload_file(outputPath, outputPath)
    s3.Bucket(s3Bucket).upload_file(outputPath, awsFileName)
    s3.Bucket(s3Bucket).upload_file(outputPath, "images/currentImage.jpeg")
    
    
    subprocess.run(["rm", outputPath])
    
    

if __name__ == "__main__":
    main()

