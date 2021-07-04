from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from deta import Deta

from misc import read_pages


with open('key.txt', mode='r') as k_f:
    key = k_f.read()

app = FastAPI()

deta = Deta(key)
db = deta.Base('simpleDB')  # access your DB
drive = deta.Drive("images")


@app.post("/createpost/")
def create_post(title: str = Form(...), headerfile: UploadFile = File(...), content: str = Form(...), tags: str = Form(...), category: str = Form(...), contentfiles: str = Form(...)):
    return {'status': "All is well for now"}


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


@app.get('/items/{item_id}')
def read_item(item_id: int, q: Optional[str] = None):
    return {'item_id': item_id, 'q': q}
