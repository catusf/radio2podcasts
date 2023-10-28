"""This content utils to generate cover images for podcasts
"""
from PIL import Image, ImageDraw, ImageFont

TITLE_FONT_FILE = './fonts/STENCIL.TTF'
DESC_FONT_FILE = './fonts/calibrib.ttf'


def text_wrap(text, font, canvas, max_width, max_height):
    """ Utility function to break line of input text
    """
    lines = [[]]
    words = text.split()
    for word in words:
        # try putting this word in last line then measure
        lines[-1].append(word)
        (l, t, w, h) = canvas.multiline_textbbox((0,0), 
            '\n'.join([' '.join(line) for line in lines]), font=font)
        if w > max_width:  # too wide
            # take it back out, put it on the next line, then measure again
            lines.append([lines[-1].pop()])
            (l, t, w, h) = canvas.multiline_textbbox((0, 0),
                '\n'.join([' '.join(line) for line in lines]), font=font)
            if h > max_height:  # too high now, cannot fit this word in, so take out - add ellipses
                lines.pop()
                # try adding ellipses to last word fitting (i.e. without a
                # space)
                lines[-1][-1] += '...'
                # keep checking that this doesn't make the textbox too wide,
                # if so, cycle through previous words until the ellipses can
                # fit
                # TODO: Fix this
                # while canvas.multiline_textsize('\n'.join(
                #         [' '.join(line) for line in lines]), font=font)[0] > max_width:
                #     lines[-1].pop()
                #     lines[-1][-1] += '...'
                break
    return '\n'.join([' '.join(line) for line in lines])


def create_image(title, description, filenpath, width=3000, height=3000, title_height=1000,
                 desc_height=500, title_color=(235, 30, 35), desc_color=(46, 48, 148), back_color=(255, 255, 255),
                 title_font_file=TITLE_FONT_FILE, desc_font_file=DESC_FONT_FILE):
    """ Generates cover image for a podcast
    """
    bg = Image.new('RGB', (width, height), color=back_color)
    # bg = Image.open('test/my_background.png')
    # ws = Image.open('test/my_overlay_with_alpha.png')

    left = width/10
    top1 = height/15
    desc_spacing = desc_height/4

    top2 = top1 + title_height + 0*desc_spacing
    canvas = ImageDraw.Draw(bg)

    title_font = ImageFont.truetype(title_font_file, size=title_height)
    desc_font = ImageFont.truetype(desc_font_file, size=desc_height)

    wrapped_width = width - 2*left
    description_wrapped = text_wrap(
        description, desc_font, canvas, wrapped_width, height)

    # write title and description
    canvas.rectangle([(0, 0), (width, height)], outline=title_color, width=10)
    canvas.text((left, top1), title, font=title_font, fill=title_color)
    canvas.multiline_text(
        (left, top2), description_wrapped, font=desc_font,
        fill=desc_color, spacing=desc_spacing)

    # out = Image.alpha_composite(bg,ws)
    bg.save(filenpath)

    # print('Done.')


def main():
    """ Test function
    """
    create_image('RADIO', 'Test Radio Station', 'RADIO.png')


if __name__ == "__main__":
    main()
