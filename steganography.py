from PIL import Image, ImageDraw
from random import randint
from re import findall
from wand.image import Image as Img
import os
from main import *


def stega_encrypt(name, text):
    img = Image.open(name)
    draw = ImageDraw.Draw(img)
    width, height = img.size[0], img.size[1]
    pix = img.load()
    f = open(f'{name.split(".")[0]}keys.txt', 'w')

    for elem in ([ord(elem) for elem in text]):
        key = (randint(1, width-10), randint(1, height-10))

        print(pix[key])

        g, b = pix[key][1:3]
        draw.point(key, (elem, g, b))
        f.write(str(key)+'\n')

    img.save(f"{name.split('.')[0]}.png", "PNG")
    f.close()


def stega_decrypt(image_name, keys_file):
    a = []
    keys = []
    img = Image.open(image_name)
    pix = img.load()
    f = open(keys_file, 'r')
    y = str([line.strip() for line in f])

    for i in range(len(findall(r'\((\d+)\,', y))):
        keys.append((int(findall(r'\((\d+)\,', y)[i]), int(findall(r'\,\s(\d+)\)', y)[i])))
    for key in keys:
        a.append(pix[tuple(key)][0])

    return ''.join([chr(elem) for elem in a])


def tranparent_watermark(filename, watermark, t, le, top, n1):
    with Img(filename=filename) as background:
        with Img(filename=watermark) as watermark:
            background.watermark(image=watermark, transparency=(t / 100), left=le, top=top)
        background.save(filename=n1)


def full_screen_watermark(filename, watermark, t, n1):
    with Img(filename=filename) as res:
        with Img(filename=filename) as background:
            with Img(filename=watermark) as watermark:
                for i in range(0, background.height // watermark.height, 2):
                    for j in range(0, background.width // watermark.width, 2):
                        res.watermark(image=watermark, transparency=(t / 100),
                                      left=(watermark.width * j + 10), top=(watermark.height * i + 10))
        res.save(filename=n1)
