from PIL import Image, ImageDraw, ImageFont
import os

def create_passport(id, fname, sname, bday):
    if os.path.isfile(f'./passports/passport_{id}.jpg'):
        os.remove(f'./passports/passport_{id}.jpg')

    im1 = Image.open('passport.jpg')
    im2 = Image.open(f'./photos/{id}.jpg')

    back_im = im1.copy()
    front_im = im2.copy()
    front_im = front_im.resize((252, 252), Image.ANTIALIAS)

    back_im.paste(front_im, (20, 20))


    idraw = ImageDraw.Draw(back_im)

    font = ImageFont.truetype("./segoeprint.ttf", size=36)
    idraw.text((420, 15), fname, font=font, fill=(0,0,0,255))
    idraw.text((500, 105), sname, font=font, fill=(0, 0, 0, 255))
    idraw.text((500, 200), bday, font=font, fill=(0, 0, 0, 255))

    back_im.save(f'./passports/passport_{id}.jpg', quality=100)

if __name__ == '__main__':
    create_passport("1372076472", "Андрей", "Савченко", "03.05.2002")