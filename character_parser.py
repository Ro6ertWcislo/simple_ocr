from PIL import Image, ImageFont, ImageDraw
import numpy as np

max_color = 255
def reduce_noise(parsed_characters, noise_limit):
    def reduce(arr:np.ndarray):
        arr[arr<noise_limit]=0
        arr[arr>=noise_limit]=max_color
        return arr
    return {k:reduce(v) for k,v in parsed_characters.items()}


class CharacterParser(object):
    default_characters =['0','d', '2', '3', '4', '5', '6', '7', '8','g', '9','a', 'b', 'c',
                      'e', 'f',  'h', 'j', 'k',  'm', 'n', 'o', 'p', 'q', 'r',
                      's','t','l','1', 'u', 'i','y', 'v', 'w', 'x', 'z']

    # kolejnosc ma znaczenie!!! ^
    def parse(self, font_path, font_height, characters=default_characters,noise_limit =0.5)->dict:
        font = ImageFont.truetype(font_path,font_height)
        parsed_characters ={}
        for character in characters:
            # 'L' -> (8-bit pixels, black and white), (width,height), color =black
            image =Image.new('L', (font.getsize(character)[0], font.font.height), 0)
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), character, font=font, fill=255)
            # add normalized array to dictionary. Max value is 255 so normalization is devision by 255
            parsed_characters[character]=np.array(image) / max_color
        return reduce_noise(parsed_characters,noise_limit)

