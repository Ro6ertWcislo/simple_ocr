from collections import defaultdict
from functools import reduce

import numpy as np
from scipy import signal


class ImageParser(object):
    def __init__(self, characters, image, min_correlation=0.85):
        self.characters = characters
        self.image = image
        self.char_positions = {}
        char_width, _ = self.characters['0'].shape
        # epsilon chosen by experimenting
        self.epsilon = char_width / 5
        self.min_correlation = min_correlation
        self.result =None

    def compute_correlation(self, image, pattern):
        fi = np.fft.fft2(image)
        fp = np.fft.fft2(np.rot90(pattern, 2), fi.shape)
        m = fi * fp
        correlation = np.fft.ifft2(m) / signal.correlate2d(pattern, pattern).max()
        correlation = correlation.astype(float)
        correlation[correlation < self.min_correlation] = 0

        return correlation

    def match_characters(self, character, character_arr):
        positions = []
        correlation = self.compute_correlation(self.image, character_arr)
        char_width, char_height = self.characters[character].shape
        last_i, last_j = (-1 * char_width, -1 * char_height)
        for (i, j), value in np.ndenumerate(correlation):
            if value > 0.0 and not (last_i + char_width > i and last_j + char_height > j):
                positions.append((i, j))
                last_i, last_j = i, j
        self.erase_character_occurences(character, positions)
        self.char_positions[character] = positions

    def parse(self):
        for character, character_arr in self.characters.items():
            self.match_characters(character, character_arr)

        line_clusters = self.group_chars_into_lines()
        lines = [self.lines_to_string(line) for line in line_clusters.values()]
        result = reduce(lambda acc, string: acc + "\n" + string, lines)
        self.result =result
        return result

    def group_chars_into_lines(self):

        # get only x coordinates of all found matches
        x_y_char_list = self.merge_char_with_coords()
        x_y_char_list = sorted(x_y_char_list, key=lambda x_y_char: x_y_char[0])
        # cluster is only x coordinate
        last_cluster = x_y_char_list[0][0]
        line_clusters = defaultdict(list)
        line_clusters[last_cluster].append(x_y_char_list[0])

        for x, y, char in x_y_char_list[1:]:
            if abs(x - last_cluster) < self.epsilon:
                line_clusters[last_cluster].append((x, y, char))
            else:
                line_clusters[x].append((x, y, char))
                last_cluster = x
        return line_clusters

    def erase_character_occurences(self, character, positions):
        """ After all occurences of a character are found, we should erase it from the image,
            otherwise, they could be matched by other, similar characters  """

        for x, y in positions:
            char_width, char_height = self.characters[character].shape
            self.image[x - char_width:x, y - char_height:y] = 0

    def merge_char_with_coords(self):
        result = []
        for char, positions in self.char_positions.items():
            result += [(x, y, char) for x, y in positions]
        return result

    def lines_to_string(self, line):
        line = sorted(line, key=lambda x_y_char: x_y_char[1])
        # first char
        result = line[0][2]
        last_y = line[0][1]
        for x, y, char in line[1:]:
            if abs(y - last_y) > self.epsilon + self.characters[char].shape[0] / 2:
                result += " "
            result += char
            last_y = y
        return result

    def print_characters_stats(self):
        for char, positions in self.char_positions.items():
            if len(positions)>0:
                print(char,len(positions))

    def compare_result(self,text):
        print("original text size: "+str(len(text))+"\n")
        print("parsed text size:"+str(len(self.result))+"\n")
        bad_counter=0
        good_counter=0
        for char1,char2 in zip(self.result,text):
            if char1==char2:
                good_counter+=1
            else:
                bad_counter+=1
        print("correct characters: "+str(good_counter)+"\n")
        print("incorrect characters: " + str(bad_counter) + "\n")