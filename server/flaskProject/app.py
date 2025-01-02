from flask import Flask, request, send_file, jsonify
from multiprocessing import Process, Pipe
import json
import requests

app = Flask(__name__)

#   全局变量data，用于在进程中存储数据
global_data = None


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


if __name__ == '__main__':
    # server_conn, predict_conn = Pipe()
    # predict_p = Process(target=get_data_from_viewport_prediction, args=(predict_conn,))
    # server_p = Process(target=send_data_to_viewport_prediction, args=(server_conn))
    # predict_p.start()
    # server_p.start()

    app.run()
