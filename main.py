import os
from typing import Optional, List

from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from deta import Deta, service

from misc import read_pages, replace_drive_link


app = FastAPI()

deta = Deta()
db = deta.Base('simpleDB')  # access your DB
art_db = deta.Base('articles')
drive = deta.Drive("images")
static_drive = deta.Drive("static")


def upload_static():
    with open('./static/site.css', 'r') as f:
        static_drive.put('site.css', f)

upload_static()

art_db_model = {
    "post_id": int,
    "title": str,
    "header_image": str,
    "content": str,
    "tags": str,
    "category": str,
    "published": bool,
    "thumbnail": str,
    "author": str,
    "member_only": bool

}

@app.post("/createpost/")
def create_post(title: str = Form(...), headerfile: UploadFile = File(...), content: str = Form(...), tags: str = Form(...), category: str = Form(...), contentfiles: List[UploadFile] = File(...)):
    result = []

    # save header file
    h_name = headerfile.filename
    f = headerfile.file
    res = drive.put(h_name, f)
    result.append(res)
    # save thumbnail of header file
    # other image files
    for file in contentfiles:
        name = file.filename
        ff = file.file
        res = drive.put(name, ff)
        result.append(res)

    # Fix the markdown
    content = replace_drive_link(content)

    # save to db
    res = art_db.put({
        "title": title,
        "header_image": '/images/'+h_name,
        "content": content,
        "tags": tags,
        "category": tags,
        "published": True,
        "member_only": False
    })

    result.append(res)

    return {'status': result, 'form': [title, content, tags, category]}


@app.post("/files/")
def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        name = file.filename
        f = file.file
        res = drive.put(name, f)

    return {"result": res, "filenames": [file.filename for file in files]}

@app.get('/')
def read_root():
    conts = read_pages('index.html')
    conts = conts.replace('{nav}', get_nav())
    return HTMLResponse(content=conts)


@app.get('/create/post')
def front_create_post():
    conts = read_pages("create_post.html")
    conts = conts.replace('{nav}', get_nav())
    return HTMLResponse(content=conts)

@app.get('/images/{name}')
def get_image(name: str):
    resp = drive.get(name)
    return StreamingResponse(resp.iter_chunks(1024), media_type='image/png')

@app.get('/static/{filename}')
def get_static(filename: str):
    resp = static_drive.get(filename)
    return StreamingResponse(resp.iter_chunks(1024), media_type='text/css')

def get_nav():
    nav_str = """<li>Python</li>
            <li>Qt</li>
            <li>QML</li>
            <li>FastAPI</li>"""

    return nav_str

@app.get('/items/{item_id}')
def read_item(item_id: int, q: Optional[str] = None):
    return {'item_id': item_id, 'q': q}

@app.get('/post/{title}')
def read_post(title: str):
    conts = read_pages('read_article.html')
    row = next(art_db.fetch({'title': title}))
    row = row[0]

    conts = conts.replace('{title}',  row['title'])
    conts = conts.replace('{header_image}', row['header_image'])
    conts = conts.replace('{content}', row['content'])

    # others
    conts = conts.replace('{nav}', get_nav())

    return HTMLResponse(content=conts)
