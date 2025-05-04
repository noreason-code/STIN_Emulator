# STIN_Emulator

[TOC]

## 1. 使用

### 1.0 安装基础依赖

模拟器依赖Docker、Python3、NodeJS(如果需要启动前端)、Go(如果需要启动数据采集器)进行构建和运行

在Ubuntu下已自带Python3、NodeJS解释器
Docker可以使用以下命令进行安装

```bash

sudo apt install docker.io

```

Go可以使用snap进行安装

```bash

sudo snap install --classic go1.20

```

如果是server版本系统，请在 [All Release - The Go Programming Language](https://go.dev/dl/)找到对应的`tar.gz`包下载后进行安装

### 1.1 构建镜像

进入container-base目录下, 依次进入

1. `build_ubuntu`
2. `build_python`
3. `satellite_node_docker`

文件夹，执行`./build_dockerfile.sh`脚本
如果提示`no such file or directory`, 请为其添加可执行权限
```bash

sudo chmod +x ./build_dockerfile.sh

```

如果需要启动监控器，请进入`sub-modules/satellite-monitor-master`文件夹

依次执行
```bash

make build
make wrap

```

### 1.2 安装项目依赖

项目的控制器和前端需要安装项目依赖

安装控制器依赖, 进入`node-manager`文件夹, 运行

```bash

sudo pip3 install -r requiremnents.txt

```

如果需要启动前端，则需要安装前端依赖，进入`ui`文件夹, 运行

```bash

npm install

```

### 1.3 启动

启动控制器需要进入控制器文件夹`node-manager`, 执行

```bash
sudo python3 main.py
```

如果需要启动前端, 则新开一个终端, 进入`ui`文件夹, 执行

```bash

npm run start
# 如果需要不同机器访问，则执行
# npm run start 0.0.0.0

```
