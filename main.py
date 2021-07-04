import os
from typing import Optional, List

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from deta import Deta, service

from misc import read_pages, save_image


with open('key.txt', mode='r') as k_f:
    key = k_f.read()

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name="static")
app.mount('/images', StaticFiles(directory='images'), name="images")

deta = Deta(key)
db = deta.Base('simpleDB')  # access your DB
art_db = deta.Base('articles')
drive = deta.Drive("images")


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
    res = save_image('./images/'+h_name, f)
    result.append(res)
    # save thumbnail of header file
    # other image files
    for file in contentfiles:
        name = file.filename
        ff = file.file
        res = save_image('./images/'+name, ff)
        result.append(res)

    # save to db
    res = art_db.put({
        "title": title,
        "header_image": 'images'+h_name,
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
    return HTMLResponse(content=read_pages('index.html'))


@app.get('/create/post')
def front_create_post():
    return HTMLResponse(content=read_pages("create_post.html"))

@app.get('/items/{item_id}')
def read_item(item_id: int, q: Optional[str] = None):
    return {'item_id': item_id, 'q': q}
