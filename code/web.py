import asyncio
import os.path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from nonebot import logger
import nonebot
import sqlite3
import xml.etree.ElementTree as ET
from PIL import Image
import uvicorn
from config import anime_config

app = FastAPI()
nonebot.init(log_level="DEBUG")

# 数据库
anime_db = {
    "anime_list": {
        "观看中": [],
        "待看": [],
        "已看": [],
        "放弃": [],
        "未分类": [],
    },
    "anime_data": {}
}


def load_from_library():
    path_list = anime_config["media_library_path"]
    library_files = {path: {} for path in path_list}
    logger.debug("开始读取文件目录")
    for library_path in library_files.keys():
        os.makedirs(library_path, exist_ok=True)
        library_files[library_path] = {name: [] for name in os.listdir(library_path)}
        for name in library_files[library_path].keys():
            library_files[library_path][name] = os.listdir(f"{library_path}/{name}")

    logger.debug("读取数据库")
    conn = sqlite3.connect("./media.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    datas = cursor.fetchall()
    tables = [data[1] for data in datas if data[1] != "sqlite_sequence"]
    if "animation" not in tables:
        cursor.execute(
            'create table animation (media_id varchar(10) primary key, title varchar(10), '
            'status varchar(10), rating varchar(10), detail varchar(10))')
    cursor.execute('select * from animation')
    datas = cursor.fetchall()
    cursor.close()
    conn.close()

    logger.debug("匹配数据库")
    conn = sqlite3.connect("./media.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    datas = cursor.fetchall()
    tables = [data[1] for data in datas if data[1] != "sqlite_sequence"]
    if "animation" not in tables:
        cursor.execute(
            'create table animation (media_id varchar(10) primary key, title varchar(10), '
            'status varchar(10), rating varchar(10), detail varchar(10))')
    cursor.execute('select * from animation')
    datas = cursor.fetchall()
    db_id_list = [str(data[0]) for data in datas]

    for library_path in library_files.keys():
        for name in library_files[library_path].keys():
            in_db = False
            for data in datas:
                if data[1] == name:
                    in_db = True
            if in_db is True:
                continue
            anime_name = name

            anime_id = 0
            path = f"{library_path}/{name}/tvshow.nfo"
            if os.path.exists(path):
                tree = ET.parse(path)
                root = tree.getroot()
                for i in root:
                    if i.tag == "imdb_id":
                        anime_id = i.text.removeprefix("tt")
                        break
            if anime_id == 0:
                anime_id = 1
                while str(anime_id) in db_id_list:
                    anime_id += 1
            db_id_list.append(str(anime_id))
            logger.info(f"添加入库： {anime_name}（{anime_id}）")
            cursor.execute(f'replace into animation(media_id,title) '
                           f'values("{anime_id}","{anime_name}")')
            datas.append((anime_id, anime_name))

    conn.commit()
    cursor.close()
    conn.close()

    logger.debug("拷贝图片")
    for data in datas:
        image_path = f"./image/poster/{data[0]}.jpg"
        anime_name = data[1]
        if os.path.exists(image_path):
            continue
        poster_path = None
        for library_path in library_files.keys():
            if poster_path is not None:
                break
            if anime_name in library_files[library_path].keys():
                for file_name in ["folder", "poster", "season01-poster", "season02-poster"]:
                    if poster_path is not None:
                        break
                    for file_type in ["webp", "jpg", "jpeg", "png"]:
                        if f"{file_name}.{file_type}" in library_files[library_path][anime_name]:
                            poster_path = f"{library_path}/{anime_name}/{file_name}.{file_type}"
                            break
        if poster_path is not None:
            logger.debug(f"保存图片： {anime_name}： {image_path} <- {poster_path}")
            image = Image.open(poster_path)
            image.save(image_path)


def load_db():
    conn = sqlite3.connect("./media.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    datas = cursor.fetchall()
    tables = [data[1] for data in datas if data[1] != "sqlite_sequence"]
    if "animation" not in tables:
        cursor.execute(
            'create table animation (media_id varchar(10) primary key, title varchar(10), '
            'status varchar(10), rating varchar(10), detail varchar(10))')
    cursor.execute('select * from animation')
    datas = cursor.fetchall()
    cursor.close()
    conn.close()

    anime_db["anime_data"] = {}
    for data in datas:
        anime_data = {
            "anime_id": str(data[0]),
            "name": str(data[1]),
            "outline": str(data[4]) if data[2] is not None else "简介...",
            "poster": f"/image/poster/{data[0]}.jpg",
            "rating": int(data[3]) if data[3] is not None else 0,
            "alias": [],
            "status": str(data[2]) if data[2] is not None else "未分类"
        }
        anime_db["anime_data"][str(data[0])] = anime_data


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("./index.html", "r", encoding="UTF-8") as file:
        html = file.read()
    # user_agent = request.headers.get("user-agent")
    # # 判断设备类型
    # if "iPhone" in user_agent:
    #     platform = "iPhone"
    # elif "iPad" in user_agent:
    #     platform = "iPad"
    # elif "Windows" in user_agent:
    #     platform = "Windows"
    # else:
    #     platform = "None"
    #
    # # 设置大小

    return html


@app.get("/image/{image_name}")
@app.get("/image/{image_path}/{image_name}")
async def get_anime_list(image_path: str = None, image_name: str = None):
    if image_name is None:
        logger.error("async def get_anime_list:  image_name is None")
        raise ""
    path = "./image"
    if image_path is not None:
        path_list = image_path.split("-")
        for p in path_list:
            path += f"/{p}"
    path += f"/{image_name}"
    if os.path.exists(path):
        return FileResponse(path)
    if image_path == "poster":
        return FileResponse("./image/none.jpg")
    logger.error(f"图片文件不存在： {path}")
    return JSONResponse({"code": 1, "message": "error"})


@app.get("/api/anime_list")
async def get_anime_list():
    anime_list = {}
    for state in anime_db["anime_list"].keys():
        anime_list[state] = []
    sorted_items = sorted(anime_db["anime_data"].items(), key=lambda item: item[1]['rating'], reverse=True)
    sorted_dict = {k: v for k, v in sorted_items}
    for anime_id in sorted_dict.keys():
        anime_list[anime_db["anime_data"][anime_id]["status"]].append(anime_db["anime_data"][anime_id])
    return anime_list


@app.get("/api/search")
async def search(name: str):
    search_list = []
    for anime_id in anime_db["anime_data"].keys():
        if (name == anime_db["anime_data"][anime_id]["name"]
                or name in anime_db["anime_data"][anime_id]["alias"]):
            if anime_id not in search_list:
                search_list.append(anime_id)
    for anime_id in anime_db["anime_data"].keys():
        if name in anime_db["anime_data"][anime_id]["name"]:
            if anime_id not in search_list:
                search_list.append(anime_id)
        for a in anime_db["anime_data"][anime_id]["alias"]:
            if name in a:
                if anime_id not in search_list:
                    search_list.append(anime_id)
    search_data = [anime_db["anime_data"][anime_id] for anime_id in search_list]
    return search_data


@app.get("/api/anime")
async def get_anime(anime_id: int | str | None = None):
    anime_id = str(anime_id)
    # 返回详细数据
    anime_data = {
        "anime_id": "0",
        "name": "None",
        "outline": "Npne",
        "poster": "/image/none.jpg",
        "rating": 0,
        "status": "未分类"
    }
    if anime_id in anime_db["anime_data"].keys():
        return anime_db["anime_data"][anime_id]
    return anime_data


@app.get("/api/update")
@app.post("/api/update")
async def update_item(anime_id: int | str, anime_type: str, value: int | str):
    # 更新数据库逻辑
    if anime_id not in anime_db["anime_data"].keys():
        return {"code": 1, "message": "番剧不在数据库"}
    if anime_type not in ["rating", "status"]:
        return {"code": 1, "message": "无此类型"}
    if value not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"] and value not in anime_db[
        "anime_list"].keys():
        return {"code": 1, "message": "value错误"}
    anime_db["anime_data"][anime_id][anime_type] = int(value) if anime_type == "rating" else str(value)

    conn = sqlite3.connect("./media.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    datas = cursor.fetchall()
    tables = [data[1] for data in datas if data[1] != "sqlite_sequence"]
    if "animation" not in tables:
        cursor.execute(
            'create table animation (media_id varchar(10) primary key, title varchar(10), '
            'status varchar(10), rating varchar(10), detail varchar(10))')
    cursor.execute(f"SELECT * FROM animation WHERE media_id='{anime_id}'")
    data = cursor.fetchone()
    if data is not None:
        if anime_type == "rating":
            cursor.execute(f'replace into animation(media_id,title,status,rating,detail) '
                           f'values("{data[0]}","{data[1]}","{data[2]}","{value}","{data[4]}")')
        elif anime_type == "status":
            cursor.execute(f'replace into animation(media_id,title,status,rating,detail) '
                           f'values("{data[0]}","{data[1]}","{value}","{data[3]}","{data[4]}")')
    conn.commit()
    cursor.close()
    conn.close()

    # load_db()
    return {"status": "success"}


def run_refresh_data():
    logger.debug("开启定时读取")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(refresh_data())


async def refresh_data():
    while True:
        load_from_library()
        load_db()
        await asyncio.sleep(3600 * 24)


def run_uvicorn():
    logger.debug("开启网页")
    uvicorn.run(app, host=anime_config["host"], port=anime_config["port"])
