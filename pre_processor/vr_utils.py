# 这个文件用来做一些简单工具

# 翻滚角roll、俯仰角pitch、偏航角yaw计算
# 使用前提，拥有四元组坐标，以数组的形式传入，或者以单独的元素传入
import math
import os
import cv2
import json

# def get_all_angles(arr):
#     # q是一个四个元素的数组, x y z w arr[0] arr[1] arr[2] arr[3]
#     # 翻滚角                
#     roll = math.atan2(2 * (arr[3] * arr[2] + arr[0] * arr[1]), 1 - 2 * (arr[0] * arr[0] + arr[2] * arr[2]))
#     # 俯仰角
#     pitch = math.asin(2 * (arr[3] * arr[0] - arr[2] * arr[1]))
#     # 偏航角
#     yaw = math.atan2(2 * (arr[3] * arr[1] + arr[2] * arr[0]) , 1 - 2 * (arr[0] * arr[0] + arr[1] * arr[1]))
#     return roll, pitch, yaw

# 该函数用于获取mp4文件信息, 默认路径为/e3po/source/video/sample.mp4
def open_video_for_info(path):
    # 如果文件不在默认路径下，则将文件复制到默认路径下
    print(path)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        default_video_path = './E3PO/e3po/source/video/' + os.path.basename(path)
        os.system(f"cp {path} {default_video_path}")
    # 如果文件路径为空，且不存在sample，返回错误
    if path == '' and not os.path.exists(path):
        print('[Error] No video file found.')
        return None
    return cv2.VideoCapture(path)

# 获取视频分辨率
def get_video_data(video_capture):
    # 获取视频信息
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    return width, height,fps
# 这个函数用来解析json
def parse_json_key(json_path):
    # 打开文件
    with open(json_path, 'r') as f:
        # 读取文件
        json_content = f.read()
        # 解析文件
        json_content = json.loads(json_content)
    
    return json_content

# 解析script_config.json 文件
def parse_script_config(json_path='./script_config.json'):
    # 打开文件
    with open(json_path, 'r') as f:
        # 读取文件
        json_content = f.read()
        # 解析文件
        json_content = json.loads(json_content)
    
    # 返回文件
    return json_content