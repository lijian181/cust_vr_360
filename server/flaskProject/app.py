from flask import Flask, request, send_file, jsonify, Response
from multiprocessing import Process, Pipe
import json
import requests

#   全局变量data，用于在进程中存储数据
global_data = None

from flask import Flask
import cv2

# 初始化 Flask 和 Flask-SocketIO
app = Flask(__name__)

# 视频流（替换为摄像头索引或文件路径）
video_path = "E:\\code\\opengl_learn\\glex\\Project1\\simple3.mp4"  # 替换为 0 使用摄像头
cap = cv2.VideoCapture(video_path)

def gen_frames():
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video source.")
        return
    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 循环播放
            continue
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            if buffer is None:
                print(f"Error encoding frame at frame {frame_count}")
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'end')
        except cv2.error as e:
            print(f"Error encoding frame at frame {frame_count}: {e}")
            continue

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/get_stream")
def send_video_frames():
    """
    持续读取视频帧并通过 WebSocket 发送。
    """
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 视频结束后重头播放
            continue

        # 压缩并发送帧数据
        frame_data = encode_frame(frame)
        return frame_data


def encode_frame(frame):
    """
    将 OpenCV 的帧编码为 JPEG，并转换为字节流。
    """
    _, buffer = cv2.imencode(".jpg", frame)
    return buffer.tobytes()


# 用于处理进程通信的模块
# 该函数用于接收视口预测模块发出的信息
def get_data_from_viewport_prediction(conn):
    # 接收视口预测模块发出的信息
    try:
        data = conn.recv()
    except EOFError as eofe:
        print("get data from viewport prediction failed")
    finally:
        conn.close()
    # print(data)
    # 这部分返回打的数据中，是对应的块的信息
    return data


# 该函数用来发送从接口中获取的数据到视口预测模块
def send_data_to_viewport_prediction(conn):
    # 发送数据到视口预测模块
    try:
        conn.send(global_data)
    except BrokenPipeError as bpe:
        print("send data to viewport prediction failed")
    conn.close()
    return


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def get_chunk_from_local(json_data):
    chunk_name = []
    # 打通视频快计算的接口
    return chunk_name


@app.route('/net_speed', methods=['GET', 'POST'])
def get_net_speed():
    # 本地存储一个文件，用于客户端获取
    file_path = './net_speed.png'
    return send_file(file_path)


# 获取请求，计算完的结果是返回块的信息
@app.route('/get_chunk', methods=['GET', 'POST'])
def get_chunk():
    # 获取body中的参数
    body_data = request.data
    # print(body_data)
    try:
        json_data = json.loads(body_data)
        if json_data:
            # 创建和视口预测模块的连接
            # viewport_prediction_url = '"http://localhost:5000/hello"'
            # 计算应该返回哪些块
            chunks = get_chunk_from_local(json_data)
            # chunks是一个数组，数组元素是块名
            response_data = {'chunks': chunks,
                             'video_name': json_data['video_name']
                             }
            return jsonify(response_data)
        else:
            return 'error, please check your data (body is empty)'
    except ValueError as ve:
        return 'error'


# 此处逻辑，主要用于发送视频文件，视频名即subpath路径
@app.route('/get_video/<path:subpath>', methods=['GET', 'POST'])
def get_video(subpath):
    # subpath是文件名_分块
    # 获取文件名
    file_name = subpath.split('_')[0]
    # 获取分块
    chunk_num = subpath.split('_')[1]

    # 定义本地的路径
    local_path = f"E:\\code\\cust-project\\vr-video\\e3po\\pythonProject\\E3PO\\e3po\\source\\video\\{file_name}\\{file_name}\\erp\\dst_video_folder"
    file_name = 'chunk_0000_tile_' + chunk_num + '.mp4'
    whole_path = local_path + '\\' + file_name
    return send_file(whole_path, mimetype='video/mp4')


if __name__ == "__main__":
    print("Starting video stream...")
    app.run()
