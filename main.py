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

import RPi.GPIO as gpio
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)


stop = False  # 暂停工作
factor = 0.5  # 人脸识别图像缩放（减小数据处理量）
filePath = os.path.dirname(os.path.abspath(__file__)) # 程序自身路径获取


def quitHandler(signum=None, frame=None):
    """程序退出处理
    """
    print('\n已释放资源，执行退出！')

    # 停止工作循环
    global stop
    stop = True

    # 释放 GPIO
    gpio.cleanup()
    
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


def faceNamesWrite(faceNames):
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

    signal.signal(signal.SIGINT, quitHandler) # Ctrl + C
    signal.signal(signal.SIGQUIT, quitHandler) # Ctrl + \
    signal.signal(signal.SIGTERM, quitHandler) # kill

    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        print('[Error] 摄像头打开失败！')
        quitHandler()

    # 配置
    if 'config' in sys.argv:
        if os.path.exists(filePath + '/faces') and pathlib.Path(filePath + '/faces').is_dir():  # 检测人脸库路径是否存在
            pass
        else:
            os.mkdir(filePath + '/faces')

        # 从配置文件获取人脸名
        faceNames = list()
        try:
            with open(filePath + '/faceNames.ini', 'r') as f:
                for line in f:
                    if line.count('\n') == len(line) or line.count(' ') == len(line) - line.count('\n'):  # 清除空行
                        continue
                    faceNames.append(line.strip('\n'))
        except FileNotFoundError:
            with open(filePath + '/faceNames.ini', 'w') as f:  # 首次运行创建配置文件
                pass

        faceNamePaths = [filePath + '/faces/' + faceName + '.jpg' for faceName in faceNames]  # 生成人脸路径

        # 清除无效数据 - 配置文件有名字，但是不存在对应的人脸图片了
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
                        cv.rectangle(small, (left, top), (right, bottom), (0, 0, 255), 1)  # 框画人脸
                    cv.imshow('face', small)

                    key = cv.waitKey(40)
                    if key == 27:  # Esc
                        print('退出人脸录入！')
                        cv.destroyAllWindows()
                        break
                    elif key == 32:  # Space
                        if not location:
                            print('未检测到人脸，请重新录入!')
                            continue
                        name = input('请输入名字(不支持中文): ')  # 尚未测试此处输入中文会发生什么
                        savePath = filePath + '/faces/' + name + '.jpg'
                        if cv.imwrite(savePath, face):
                            print('录入人脸成功')
                            faceNames.append(name)
                            faceNamePaths.append(savePath)
                            cv.destroyAllWindows()
                            break
                faceNamesWrite(faceNames)

            elif choice == '2':
                confirm = input('确定清空数据？（\'y\' or \'n\'）(\'n\')')
                if confirm == 'y':
                    faceNames = []
                    faceNamePaths = []
                    faceNamesWrite(faceNames)
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
                        faceNamesWrite(faceNames)

            elif choice == '0':
                faceNamesWrite(faceNames)
                break
            else:
                print('无效操作！！！')
        quitHandler()
        exit()

    #############
    # 人脸识别工作
    #############

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

    gpio.setup(17, gpio.OUT)
    gpio.setup(18, gpio.OUT)
    gpio.setup(19, gpio.OUT)
    gpio.setup(20, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(21, gpio.OUT, initial=gpio.LOW)

    counter  = 0
    lastState = False
    readCounter = 0
    while True:
        gpio.output(17, gpio.HIGH)
        gpio.output(18, gpio.LOW)
        gpio.output(19, gpio.LOW)
        gpio.output(21, gpio.LOW)  # 开门信号控制，置为低电平

        ret, frame = cam.read()

        # 跳帧处理，缓解图像延时问题
        readCounter += 1
        if readCounter != 4:
            continue
        else:
            readCounter = 0
        #######################
            
        small = cv.resize(frame, (0, 0), fx=factor, fy=factor)
        rgbImg = small[:, :, ::-1]

        faceLocation = face_locations(rgbImg)
        faceEncodings = face_encodings(rgbImg, faceLocation)

        names = []
        for faceEncoding in faceEncodings:  # 检测到人脸
            gpio.output(17, gpio.LOW)
            gpio.output(18, gpio.HIGH)
            gpio.output(19, gpio.LOW)

            matches = compare_faces(knownFaceEncodings, faceEncoding)
            name  = 'unknow'

            faceDistance = face_distance(knownFaceEncodings, faceEncoding)
            bestMatchIndex = np.argmin(faceDistance)
            if matches[bestMatchIndex]:
                name = knownFaceNames[bestMatchIndex]

            nowState = (name != 'unknow')
            if nowState and lastState:
                counter += 1
            else:
                counter = 0
            lastState = nowState
            names.append(name)

        for (top, right, bottom, left), name in zip(faceLocation, names):
            cv.rectangle(small, (left, top), (right, bottom), (0, 0, 255), 1)
            cv.putText(small, name, (left + 6, bottom - 6), cv.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

        if 'show' in sys.argv:
            cv.imshow('Recognition', small)

        if counter == 5:  # 识别到5次人脸
            counter = 0

            gpio.output(17, gpio.LOW)
            gpio.output(18, gpio.LOW)
            gpio.output(19, gpio.HIGH)

            quitCounter = 0
            lastTouch = gpio.input(20)
            while True:
                nowTouch = gpio.input(20)
                if nowTouch != lastTouch:
                    gpio.output(21, gpio.HIGH)
                    time.sleep(1)
                    lastTouch = nowTouch
                    break
                else:
                    time.sleep(1)
                    quitCounter += 1
                    if quitCounter == 20:
                        quitCounter = 0
                        break

        if cv.waitKey(40) == 27:
            break