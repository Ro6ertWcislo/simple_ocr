from scipy import ndimage
import numpy as np
from character_parser import CharacterParser
from image_parser import ImageParser


def main(file_path, font_path, font_size):
    image = ndimage.imread(file_path, flatten=True)
    inv_image = 255 - image

    inv_image[inv_image < 1.5 * (inv_image.min())] = 0
    characters = CharacterParser().parse(font_path, font_size)
    image_parser = ImageParser(characters, inv_image,min_correlation=0.70)

    result = image_parser.parse()
    print(result)
    image_parser.print_characters_stats()
np.warnings.filterwarnings('ignore')
main("serif.png",'DejaVuSerifCondensed-Bold.ttf',42)



# b=34 c =58