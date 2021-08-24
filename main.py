#!/usr/bin/env python3.8
'''
Filename: main.py
brief: 人脸识别，检测到预存的人脸，通过 GPIO 发出信号

Author: IYATT-yx
Email: 2514374431@qq.com

Copyright (C) 2021 IYATT-yx
基于 AGPL-3.0 许可
'''
import cv2 as cv
from face_recognition import *
import os
import sys
import signal
import pathlib
import time
import numpy as np


# 调试版本标志
debug = False

# 暂停工作标志
stop = False

# 图像缩小比例
factor = 0.5

# 程序文件绝对路径
filePath = os.path.dirname(os.path.abspath(__file__))

def quitHandler(signum=None, frame=None):
    global debug
    if debug:
        print('\n[debug]已释放资源，执行退出！')

    # 停止工作循环
    global stop
    stop = True
    
    # 关闭摄像头
    cam.release()

    exit()

def showMenu():
    '''显示配置菜单
    '''
    print('配置菜单'.center(20, '-'))
    print()
    print('1 新增数据'.center(20, ' '))
    print('2 清空数据'.center(20, ' '))
    print('3 查看数据'.center(20, ' '))
    print('4 删除数据'.center(20, ' '))
    print('0 退出菜单'.center(20, ' '))

def faceNamesWrite(faceNames, faceNamePaths):
    '''配置刷新
    预存人脸数据修改后更新到配置文件
    '''
    with open(filePath + '/faceNames.ini', 'w') as f: # 重写人名配置
        for faceName in faceNames:
            f.write(faceName + '\n')

    for root, dirs, files in os.walk(filePath + '/faces'): # 删除无人名匹配的图片
        for file in files:
            path = root + '/' + file
            if file.strip('.jpg') in faceNames:
                continue
            else:
                os.remove(path)
    
if __name__ == '__main__':
        # 捕捉终止信号
        signal.signal(signal.SIGINT, quitHandler)
        signal.signal(signal.SIGQUIT, quitHandler)
        signal.signal(signal.SIGTERM, quitHandler)

        # 打开摄像头及检查
        cam = cv.VideoCapture(0)
        if not cam.isOpened():
            print('[Error] 摄像头打开失败！')
            exit()

        # 开启调试信息显示
        if 'debug' in sys.argv:
            debug = True
            print('[调试]')
        # 正常模式
        else:
            debug = False
            print('[正常模式]')
        # 配置模式
        if 'config' in sys.argv:
            # 人脸路径检测
            if os.path.exists(filePath + '/faces') and pathlib.Path(filePath + '/faces').is_dir():
                pass
            else:
                os.mkdir(filePath + '/faces')
            # 加载名字
            faceNames = list()
            try:
                with open(filePath + '/faceNames.ini', 'r') as f:
                    for line in f:
                        if line.count('\n') == len(line) or line.count(' ') == len(line) - line.count('\n'):
                            continue # 消除空行
                        faceNames.append(line.strip('\n'))
            except FileNotFoundError:
                with open(filePath + '/faceNames.ini', 'w') as f:
                    pass
            faceNamePaths = [filePath + '/faces/' + faceName + '.jpg' for faceName in faceNames] # 人脸绝对路径
            # 清除名字对应无图片的
            removeLists = list()
            for i in range(len(faceNamePaths)):
                img =  cv.imread(faceNamePaths[i], cv.IMREAD_GRAYSCALE)
                try:
                    img.shape
                except:
                    removeLists.append(faceNames[i])
            for removeList in removeLists:
                faceNames.remove(removeList)
            faceNamePaths = [filePath + '/faces/' + faceName + '.jpg' for faceName in faceNames]
            # 菜单循环
            while True:
                showMenu()
                choice = input('请输入您要进行的操作：')
                if choice == '1':
                    while True:
                        ret, src = cam.read()
                        # 前期处理
                        small = cv.resize(src, (0, 0), fx=factor, fy=factor)
                        rgb = small[:, :, ::-1]
                        # 检测人脸
                        location = face_locations(rgb)
                        # face_recognition [(上,右,底,左)]
                        # OpenCV [上:底, 左:右]
                        if not location:
                            pass
                        else:
                            (top, right, bottom, left) =  location[0]
                            face = small[top:bottom, left:right]
                            # 人脸框出
                            cv.rectangle(small, (left, top), (right, bottom), (0, 0, 255), 1)
                        # 预览
                        cv.imshow('face', small)
                        # 操作捕获
                        # Esc 退出
                        # Space 截取
                        key = cv.waitKey(40)
                        if key == 27:
                            print('退出人脸录入！')
                            cv.destroyAllWindows()
                            break
                        elif key == 32:
                            if not location: # 无人脸
                                print('未检测到人脸，请重新录入!')
                                continue
                            name = input('请输入名字(不支持中文): ') # 中文名字图片无法被导入识别库，也尚未测试此处输入中文会发生什么
                            savePath = filePath + '/faces/' + name + '.jpg'
                            if cv.imwrite(savePath, face):
                                print('录入人脸成功')
                                faceNames.append(name)
                                faceNamePaths.append(savePath)
                                cv.destroyAllWindows()
                                break
                    faceNamesWrite(faceNames, faceNamePaths)

                elif choice == '2':
                    confirm = input('确定清空数据？（\'y\' or \'n\'）(\'n\')')
                    if confirm == 'y':
                        faceNames = []
                        faceNamePaths = []
                        faceNamesWrite(faceNames, faceNamePaths)
                        print('\n已清空数据\n')

                elif choice == '3':
                    print('\n已录入人脸:')
                    for faceName in faceNames:
                        print(faceName)
                        faceNamePath = filePath + '/faces/' + faceName + '.jpg'
                        img = cv.imread(faceNamePath, cv.IMREAD_COLOR)
                        cv.imshow(faceName, img)
                        key = cv.waitKey(0)
                        if key == 27:
                            break
                    cv.destroyAllWindows()
                elif choice == '4':
                    while True:
                        name = input('请输入要删除的人名（\'q\' 退出）： ')
                        if name == 'q':
                            break
                        elif name not in faceNames:
                            print('该名字不存在，', end='')
                            continue
                        else:
                            faceNames.remove(name)
                            faceNamePaths.remove(filePath + '/faces/' + name + '.jpg')
                            faceNamesWrite(faceNames, faceNamePaths)

                elif choice == '0':
                    faceNamesWrite(faceNames, faceNamePaths)
                    quitHandler()
                else:
                    print('无效操作！！！')
            exit()

        #########
        # 正常模式
        #########

        # 加载储存的人脸
        knownFaceNames = list()
        try:
            with open(filePath + '/faceNames.ini', 'r') as f:
                for line in f:
                    knownFaceNames.append(line.strip('\n'))
        except FileNotFoundError:
            print('[Error] 请先以配置模式运行录入人脸')
            exit()
        if not knownFaceNames:
            print('[Error] 请先以配置模式运行录入人脸')
            exit()
        knownFaceEncodings = [face_encodings(load_image_file(filePath + '/faces/' + knownFaceName + '.jpg'))[0] for knownFaceName in knownFaceNames]
        print(knownFaceEncodings)

        counter  = 0
        while True:
            ret, frame = cam.read()
            small = cv.resize(frame, (0, 0), fx=factor, fy=factor)
            rgbImg = small[:, :, ::-1]
            # rgbImg = frame[:, :, ::-1]

            faceLocation = face_locations(rgbImg)
            faceEncodings = face_encodings(rgbImg, faceLocation)

            names = []
            for faceEncoding in faceEncodings:
                print(len(faceEncoding))
                matches = compare_faces(knownFaceEncodings, faceEncoding)
                name  = 'unknow'

                faceDistance = face_distance(knownFaceEncodings, faceEncoding)
                bestMatchIndex = np.argmin(faceDistance)
                if matches[bestMatchIndex]:
                    name = knownFaceNames[bestMatchIndex]
    
                if not(name == 'unknow'):
                    if name not in names:
                        counter += 1

                names.append(name)

            for (top, right, bottom, left), name in zip(faceLocation, names):
                cv.rectangle(small, (left, top), (right, bottom), (0, 0, 255), 1)
                cv.putText(small, name, (left + 6, bottom - 6), cv.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

            if debug:
                cv.imshow('Recognition', small)

            if counter == 5:
                # 输出成功识别人脸信号
                # 通过 GPIO 输出信号
                pass
                print('识别人脸')
                
                counter = 0

                print('暂停3秒')
                time.sleep(3)

            if cv.waitKey(40) == 27:
                break