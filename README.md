# OSU_MostPlayedDownload_python
从OSU官网获取你的最多游玩谱面记录  
使用sayo镜像站下载你游玩过的谱面    
目前为单线程下载，因为我懒   

# To Do  
重构代码，尽可能使用异步处理  
使用异步实现同时进行3个下载任务  

# How to Use  
在python脚本文件所在位置创建一个 config.toml 文件  
按如下形式进行配置  

```
#设置你的用户ID，可以在个人主页的网址获得
userid = 2
#设置保存路径
savepath =  '''song'''
#是否需要视频/故事板
novideo = true

#从第几个记录开始下载
offset = 0
#读取多少个记录下载谱面（-1为最大）
maxindex = 0

#设定Sayo服务器。
#0 自动，1 电信，2 移动，3 联通，4 腾讯云，5 德国，6 美国
sayoserver = 1
```
