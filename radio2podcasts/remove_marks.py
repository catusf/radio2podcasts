""" Utility to remove Vietnamese specific characters from file names and titles
"""

import re
import unidecode


def remove_marks(marked):
    '''
    Remove Vietnamese specific characters with Latin characters for safe file
    names. Also remove spaces.
    '''

    return ''.join(c for c in unidecode.unidecode(marked) if c.isalnum())


def initials(marked, max_len=10):
    '''
    Creates string of initial letters.
    '''
    words = re.split('[^a-zA-Z0-9]', unidecode.unidecode(marked)
                     )  # Remove marks and splits to words

    return "".join([w[0] for w in words if w])


def main():
    """ Test method
    """
    print(remove_marks('Bèo dạt mây trôi chốn xa xôi Anh ơi em vẫn đợi bèo dạt'))


if __name__ == "__main__":
    main()
