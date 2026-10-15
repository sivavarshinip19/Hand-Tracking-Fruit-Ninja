
from PIL import Image, ImageDraw
import os
import math

OUT = os.path.join("assets", "fruits")
os.makedirs(OUT, exist_ok=True)

SIZE = 256

def new_canvas():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

def ellipse(draw, box, fill, outline=None, width=1):
    draw.ellipse(box, fill=fill, outline=outline, width=width)

def shine(draw, x, y, rx, ry):
    ellipse(draw, (x-rx, y-ry, x+rx, y+ry), (255, 255, 255, 125))

# APPLE
im = new_canvas()
d = ImageDraw.Draw(im)
ellipse(d, (48, 65, 139, 190), (225, 35, 52), (150, 20, 35), 4)
ellipse(d, (117, 65, 208, 190), (239, 45, 57), (150, 20, 35), 4)
ellipse(d, (62, 95, 194, 205), (230, 38, 51))
d.polygon([(119, 72), (132, 37), (143, 39), (135, 79)], fill=(104, 61, 30))
d.ellipse((133, 34, 178, 60), fill=(45, 165, 75))
shine(d, 82, 102, 10, 22)
im.save(os.path.join(OUT, "apple.png"))

# MANGO
im = new_canvas()
d = ImageDraw.Draw(im)
d.ellipse((43, 42, 213, 218), fill=(255, 175, 34), outline=(204, 105, 15), width=4)
d.ellipse((64, 53, 188, 208), fill=(255, 194, 48))
d.ellipse((60, 80, 145, 202), fill=(255, 100, 45))
d.ellipse((104, 44, 205, 155), fill=(255, 215, 61))
d.polygon([(130, 48), (139, 23), (148, 26), (144, 54)], fill=(102, 62, 29))
d.ellipse((139, 20, 190, 43), fill=(48, 164, 69))
shine(d, 86, 91, 10, 22)
im.save(os.path.join(OUT, "mango.png"))

# GRAPES
im = new_canvas()
d = ImageDraw.Draw(im)
d.line((125, 40, 137, 72), fill=(105, 66, 31), width=9)
d.ellipse((128, 25, 180, 53), fill=(46, 164, 70))
grapes = [
    (104, 68, 150, 114), (145, 72, 191, 118),
    (81, 105, 127, 151), (125, 111, 171, 157),
    (164, 111, 210, 157), (100, 148, 146, 194),
    (143, 151, 189, 197), (121, 183, 165, 227)
]
for i, b in enumerate(grapes):
    colors = [(126, 50, 195), (145, 62, 210), (106, 39, 177)]
    ellipse(d, b, colors[i % 3], (76, 26, 130), 3)
    x, y = b[0] + 13, b[1] + 13
    shine(d, x, y, 5, 8)
im.save(os.path.join(OUT, "grapes.png"))

# BANANA
im = new_canvas()
d = ImageDraw.Draw(im)
d.arc((25, 35, 226, 223), start=15, end=170, fill=(151, 103, 21), width=43)
d.arc((24, 31, 226, 219), start=15, end=170, fill=(255, 218, 55), width=34)
d.arc((35, 39, 211, 208), start=22, end=164, fill=(255, 238, 114), width=16)
d.line((35, 77, 25, 58), fill=(91, 66, 29), width=9)
d.line((208, 99, 224, 82), fill=(91, 66, 29), width=9)
d.line((58, 80, 54, 66), fill=(255, 250, 180), width=5)
im.save(os.path.join(OUT, "banana.png"))

# WATERMELON SLICE
im = new_canvas()
d = ImageDraw.Draw(im)
d.pieslice((25, 18, 231, 224), start=200, end=340, fill=(42, 151, 69))
d.pieslice((35, 28, 221, 214), start=200, end=340, fill=(247, 242, 193))
d.pieslice((43, 37, 213, 206), start=200, end=340, fill=(244, 48, 72))
for x, y in [(83, 96), (111, 83), (143, 78), (171, 91), (101, 119), (145, 116), (169, 126)]:
    d.ellipse((x-4, y-8, x+4, y+8), fill=(65, 35, 39))
im.save(os.path.join(OUT, "watermelon.png"))

print("Done! 5 fruit images created in assets/fruits/")
