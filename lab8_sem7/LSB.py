from PIL import Image


def encode(img_path, text):
    img = Image.open(img_path)

    red_template = img.split()[0]
    green_template = img.split()[1]
    blue_template = img.split()[2]

    width = img.size[0]
    height = img.size[1]
