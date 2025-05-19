from web import run_refresh_data, run_uvicorn
from threading import Thread

if __name__ == "__main__":
    t1 = Thread(target=run_refresh_data)
    t1.start()
    t2 = Thread(target=run_uvicorn)
    t2.start()

    # with open("./Thread.json", "w", encoding="UTF-8") as file:
    #     file.write(json.dumps({"state": "run"}))
    # while True:
    #     with open("./Thread.json", "r", encoding="UTF-8") as file:
    #         json_data = json.loads(file.read())
    #     if json_data["state"] != "run":
    #         ctypes.pythonapi.PyThreadState_SetAsyncExc(t1.ident, ctypes.py_object(SystemExit))
    #         ctypes.pythonapi.PyThreadState_SetAsyncExc(t2.ident, ctypes.py_object(SystemExit))
    #     time.sleep(10)
