import httpx
import py3_wget as wget
from pathlib import Path
import sys,time
import re
import tomllib

#Deepseek写的处理文件名
def sanitize_filename(filename: str) -> str:
    illegal_chars_pattern = r'[\\/:*?"<>|]'
    sanitized = re.sub(illegal_chars_pattern, '_', filename)
    sanitized = sanitized.strip()
    
    sanitized = re.sub(r'^\.+', '', sanitized)
    sanitized = re.sub(r'\.+$', '', sanitized)
    
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    
    if sanitized.upper() in reserved_names:
        sanitized = "_" + sanitized
    
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized

class osu_download:
    
    SayoServerList = {0:"auto",
                      1:"Telecom",2:"cmcc",3:"unicom",
                      4:"CDN",
                      5:"DE",6:"USA"}
    
    def __init__(self):
        self.offset : int = 0
        self.limit  : int = 50
        
        self.userid : int = 2
        self.savepath  = Path("Song")
        self.maxindex : float = float("inf")
        self.novideo  : bool = False
        self.sayoserver : str = "auto"

    def start_download(self):
        ReadNextList = True
        BeatmapIdList = set()
        
        while ReadNextList:
            print(f"用户ID:{self.userid}")
            mostplayedlist,ReadNextList = self.get_mostplayed()
            for beatmapdata in mostplayedlist:
                if beatmapdata["beatmapset"]["id"] in BeatmapIdList:
                    print("该记录为其他已下载歌曲的难度，跳过下载")
                    continue
                mapid = beatmapdata["beatmapset"]["id"]
                filename = sanitize_filename(f"{beatmapdata["beatmapset"]["id"]} {beatmapdata["beatmapset"]["artist"]} - {beatmapdata["beatmapset"]["title"]}.osz")
                self.download_beatmap(mapid, filename)
                BeatmapIdList.add(mapid)
                
        print(f"下载完成！已下载 {len(BeatmapIdList)} 个谱面")
        time.sleep(3)
    
    def download_beatmap(self, mapid:int, filename:str):
        try:
            if not self.savepath.is_dir():
                self.savepath.mkdir(parents=True,exist_ok=True)
                
            download_link = self.get_download_link(mapid)
            file_savepath  = self.savepath.joinpath(filename)
            wget.download_file(url=download_link, output_path=file_savepath, max_tries=3)
            
        except RuntimeError as e:
            print(f"{mapid} 下载失败！这可能是因为服务器故障或者歌曲被版权警告")

            
    def get_mostplayed(self) ->tuple[list,bool]:
        if (self.limit + self.offset) > self.maxindex:
            self.limit = self.maxindex - self.offset
        try:
            print(f"正在获取 No.{self.offset + 1} - No.{self.limit+self.offset} 历史游玩谱面数据列表")
            response = httpx.get(f'https://osu.ppy.sh/users/{self.userid}/beatmapsets/most_played?offset={self.offset}&&limit={self.limit}')
            response.raise_for_status()
            mostplayedlist = response.json()
            
            count = len(mostplayedlist)
            self.offset += count
            print("获取数据完成")
            if count < self.limit or self.offset >= self.maxindex:
                return (mostplayedlist, False)
            else:
                return (mostplayedlist, True)
            
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            sys.exit()
            
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            sys.exit()
    
    def get_download_link(self, mapid:int):
        if self.novideo:
            return f"https://txy1.sayobot.cn/beatmaps/download/novideo/{mapid}?server={self.sayoserver}"
        else:
            return f"https://txy1.sayobot.cn/beatmaps/download/{mapid}?server=auto{self.sayoserver}"
    
    def change_savepath(self, savepath_str:str):
        self.savepath = Path(savepath_str)
        
    def read_config(self,config_path):
        with open(Path(config_path),"rb") as f:
            config = tomllib.load(f)
            
        self.maxindex = config["maxindex"] if config["maxindex"] > 0 else float("inf")
        self.offset   = config["offset"]   if config["offset"] >= 0  else 0
        self.userid   = config["userid"]   if config["userid"] > 1   else 2
        
        self.savepath = Path(config["savepath"]) if config["savepath"] != "" else Path("Song")
        self.novideo  = config["novideo"]
        self.sayoserver  = self.SayoServerList.get(config["sayoserver"],"auto")

download_tool = osu_download()
download_tool.read_config("config.toml")
download_tool.start_download()