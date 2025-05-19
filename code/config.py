import os.path
import toml

path = f"./config.toml"
base_config = {
    "media_library_path": [],
    "host": "127.0.0.1",
    "port": 8080,
}
if not os.path.exists(path):
    with open(path, 'w', encoding='utf-8') as config_file:
        toml.dump(base_config, config_file)
anime_config = toml.load(path)

# 创建必要文件夹
os.makedirs("./image/poster", exist_ok=True)