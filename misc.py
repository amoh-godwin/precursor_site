from io import BytesIO
import os

if not os.path.exists('./static'):
    os.makedirs('./static')

if not os.path.exists('./images'):
    os.makedirs('./images')


def read_pages(page: str):
    dir = './pages/'
    with open(dir+page, mode='r', encoding='utf-8') as p_o:
        contents = p_o.read()

    return contents


def save_image(name: str, fp: BytesIO):
    with open(name, 'wb') as ff:
        ff.write(fp.read())

    return name
