from PIL import Image


def encode(img_path, res_path, text):
    img = Image.open(img_path)

    rgb_im = img.convert('RGB')
    width = img.size[0]
    height = img.size[1]

    binary_text = "".join(f"{ord(i):08b}" for i in text)

    print('text = {}'.format(text))
    print('binary repr = {}'.format(binary_text))

    rgb_pixels = []
    for i in range(width):
        for j in range(height):
            coords = (i, j)
            r, g, b = rgb_im.getpixel(coords)
            rgb_pixels.append([r, g, b])
            # print(r, g, b)

    binary_text += '1'
    while len(binary_text) < len(rgb_pixels) * 3:
        binary_text += '0'

    # print(len(binary_text), len(rgb_pixels))

    cur_bit = 0
    i = 0
    for i in range(len(binary_text)):
        r, g, b = rgb_pixels[i]
        r_bin = "{0:b}".format(r)
        g_bin = "{0:b}".format(g)
        b_bin = "{0:b}".format(b)

        r_bin = r_bin[:-1]
        r_bin += binary_text[cur_bit]
        cur_bit += 1
        rgb_pixels[i][0] = int(r_bin, 2)

        if cur_bit >= len(binary_text):
            break

        g_bin = g_bin[:-1]
        g_bin += binary_text[cur_bit]
        cur_bit += 1
        rgb_pixels[i][1] = int(g_bin, 2)

        if cur_bit >= len(binary_text):
            break

        b_bin = b_bin[:-1]
        b_bin += binary_text[cur_bit]
        cur_bit += 1
        rgb_pixels[i][2] = int(b_bin, 2)

        if cur_bit >= len(binary_text):
            break
        i += 1

    it = 0

    for i in range(width):
        for j in range(height):
            coords = (i, j)
            rgb_im.putpixel(coords, tuple(rgb_pixels[it]))
            it += 1

    rgb_im.save(res_path, format='PNG')


def decode(img_path):
    img = Image.open(img_path)

    rgb_im = img.convert('RGB')
    width = img.size[0]
    height = img.size[1]

    binary_text = ''
    for i in range(width):
        for j in range(height):
            coords = (i, j)
            r, g, b = rgb_im.getpixel(coords)
            binary_text += str(r % 2)
            binary_text += str(g % 2)
            binary_text += str(b % 2)

    binary_text = binary_text[:binary_text.rfind('1')]
    print(binary_text)

    res = ''
    for i in range(len(binary_text) // 8):
        res += chr(int(binary_text[i*8:i*8+8], 2))
    print(res)
