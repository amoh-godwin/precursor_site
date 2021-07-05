
def replace_drive_link(md: str):
    return md.replace('./noneducational_', '/')


def read_pages(page: str):
    dir = './pages/'
    with open(dir+page, mode='r', encoding='utf-8') as p_o:
        contents = p_o.read()

    return contents
