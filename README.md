# 阿里云盘 webdav Python 版

阿里云盘 webdav 有更好的实现：[messense/aliyundrive-webdav](https://github.com/messense/aliyundrive-webdav)

此项目用 python 实现，并额外添加了一些特殊功能

> 注意：目前项目仅处于能用的阶段，可能存在许多 bug

## 特殊功能

- 播放 tar 打包的视频文件

局限性：

- 使用文件后缀名来判断是否为打包的视频。目前后缀名为：`[".mp4.tar", ".mkv.tar"]`
- 只能读取 tar 文件的第一个视频
- tar 好像只能打包最大 8GB 文件（这里没有验证），所以最好打包单个电视剧集
- 你打包好的视频需要自己上传，所以需要大一点的上传带宽。上传文件可以使用：[alidrive-uploader](https://github.com/aoaostar/alidrive-uploader)

打包时最好去掉个人信息，比如下面的 tar 命令

```bash
tar -cvf video.mp4.tar --owner=0 --group=0 video.mp4
```

## 启动

1. 修改 `app.py` 里的一些参数
2. 根目录添加 `refresh_token` 文件，输入阿里云盘网页版的 `refresh_token`。[图文步骤](https://github.com/messense/aliyundrive-webdav#%E8%8E%B7%E5%8F%96-refresh_token)
3. `python app.py` 启动

## 新增加密模式

在 `exts` 目录下新增两个文件，分别为 `{modeName}_check.py` 和 `{modeName}.py`. `modeName` 为你的加密模式名称

`{modeName}_check.py` 模板

```py
# {modeName}_check.py 文件模板。必须有
# 1. encryption_mode 加密模式名称（无需修改赋值encryption_mode的代码）
# 2. check 方法

encryption_mode = (os.path.splitext(
    os.path.basename(__file__))[0]).rstrip('_check')

def check(file_item: FileItem) -> Optional[FileItem]:
    if not condition:
        # 如果判断后不是加密文件，直接返回None
        return None

    # 复制原file_item，修改属性不影响原file_item。也可以直接修改原file_item，返回None
    copied = file_item.copy()
    # 使用不同的名字防止冲突
    copied.name = 'new_name'
    # 不要忘记赋值encryption_mode
    copied.encryption_mode = encryption_mode
    return copied

```

`{modeName}.py` 模板

```py
# {modeName}.py 文件模板。必须有
# 1. encryption_mode 加密模式名称（无需修改赋值encryption_mode的代码）
# 2. file_class 导出的类，这个类需要继承AliyunDriveFile

class AliyunDriveTarfile(AliyunDriveFile):

    def get_content_length(self):
        pass

    def get_content(self):
        pass

    ...

encryption_mode = os.path.splitext(os.path.basename(__file__))[0]
file_class = AliyunDriveTarfile
```
