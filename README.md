该项目实现门禁系统的人脸识别，隶属于 2020年重庆理工大学科研立项项目 “人脸识别与指纹识别控制加密门锁微信小程序” KLB20079  

# 运行环境

* 树梅派 4B 4G （[官方64位系统20210507](https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-05-28/)）

* 启用摄像头
```bash
sudo raspi-config

[3 Interface Options]->[P1 Camera]->[是]->[确定]
```

* 基础开发工具
```bash
sudo apt install cmake build-essential git
```

* Python 3.8.11
```bash
####################################
# 安装依赖
####################################
sudo apt install libssl-dev libffi-dev

# tcl 8.6.11
tar xvf tcl8.6.11-src.tar.gz

cd tcl8.6.11/unix

./configure

sudo make install -j4

cd -

# tk 8.6.11
tar cvf tk8.6.11.1-src.tar.gz

cd tk8.6.11/unix

./configure

sudo make install -j4

cd -

####################################
# 安装 Python
####################################

tar xvf Python-3.8.11.tgz

cd Python-3.8.11

./configure

sudo make install -j4

cd -

# 换源（北京外国语大学）
pip3 config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple

sudo pip3 config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple

# 升级 pip
pip3 install pip -U
```

* NumPy 1.21.2
```bash
pip3 install numpy==1.21.2
```

* [OpenCV 4.5.3 源码编译安装教程](https://blog.iyatt.com/%e5%bc%80%e5%8f%91/2021/07/19/dlib%e7%bc%96%e8%af%91%e5%ae%89%e8%a3%85/)

* [dlib 19.22 源码编译安装教程](https://blog.iyatt.com/%e5%bc%80%e5%8f%91/2021/07/19/dlib%e7%bc%96%e8%af%91%e5%ae%89%e8%a3%85/)

* face_recognition 1.2.2
```bash
git clone https://github.com/ageitgey/face_recognition.git --branch=v1.2.2 --depth=1

cd face_recognition

sudo python3 setup.py install
```

* RPi.GPIO 0.7.0
```bash
pip3 install RPi.GPIO==0.7.0
```
