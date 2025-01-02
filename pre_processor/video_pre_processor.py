# 该文件集成E3PO代码库，环境需要opencv、pytorch、ffmpeg等
"""
    首先，拥有一个360°的视频文件，之后根据视频的分辨率等信息，生成多个版本
    每个版本命名规则，例：[simple]_1080.mp4
    然后，使用e3po处理视频，这个部分因为要使用dash协议，所以对整个视频切块，每块的时间依旧是整个视频的时间
    最后使用MP4box生成mpd文件

    该文件涉及到e3po的主要工作内容为：
        1：获取360°视频文件，若不存在使用默认路径
        2：将文件挪至E3PO对应的文件夹下，例如/e3po/source/video/[sample].mp4.
        3：通过opencv获取视频的信息，更改yml
        4：执行脚本

        ...可定义工作模式，默认使用approach_name->type, approach_type->on_demand
"""

import os
import cv2
import argparse
import yaml
import subprocess
# 该函数用于获取mp4文件信息, 默认路径为/e3po/source/video/sample.mp4
def open_video_for_info(video_path='./E3PO/e3po/source/video/simple.mp4'):
    # 如果文件不在默认路径下，则将文件复制到默认路径下
    if not os.path.exists(video_path):
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        default_video_path = './E3PO/e3po/source/video/' + os.path.basename(video_path)
        os.system(f"cp {video_path} {default_video_path}")
    # 如果文件路径为空，且不存在sample，返回错误
    if video_path == '' and not os.path.exists('./e3po/source/video/sample.mp4'):
        print('[Error] No video file found.')
        return None
    return cv2.VideoCapture(video_path)

# 该函数用于将获取到的mp4文件信息写入到yml文件中
def start_video_line(opt, yml_path='./E3PO/e3po/e3po.yml'):
    for video_path_version in opt['video_path_arr']:
        video_capture = open_video_for_info(video_path_version)
        yml_content_from_video = {}
        # 帧率
        yml_content_from_video['video_fps'] = (int(video_capture.get(cv2.CAP_PROP_FPS)))
        # 时长
        yml_content_from_video['video_duration'] = (int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT) / yml_content_from_video['video_fps']))
        # chunk_duration， 分块大小
        # yml_content_from_video['chunk_duration'] = opt['chunk_duration']
        # video_name
        yml_content_from_video['video_name'] = os.path.basename(video_path_version)
        # 分块方式
        yml_content_from_video['projection_mode'] = opt['chunk_type']
        # video_height
        yml_content_from_video['height'] = video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # video_width
        yml_content_from_video['width'] = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    
        #做个判断，如果不需要encode模式，此时的数据已经足够
        if opt['model_select'] != 'on_demand':
            opt = add_encoding_to_yml(yml_content_from_video, video_capture)
        # 写道yml文件
        write_yml(yml_content_from_video, yml_path, opt['model_select'])
        # 执行e3po将视频切块
        execute_e3po_tiling()
        # 执行mp4box
        # execute_mp4box(video_path_version)

    # 循环结束

def execute_mp4box(video_path):
    # 这个函数目前不需要要其他额外参数，后续可根据需求添加
    # 此处逻辑需要找到处理完分块之后的视频地址，然后使用mp4box生成mpd文件
    mpd_path = video_path.rsplit('.', 1)[0] + '.mpd'
    # 获取video_path的路径
    mpd_path = video_path.rsplit('/', 1)[0] + '/' + os.path.basename(video_path).rsplit('.', 1)[0] + '/' + 'erp'
    mp4box_command = "mp4box -dash 5000 -rap -profile dashavc264:onDemand -out {mpd_path} {video_path}"
    try :
        result = subprocess.check_output(mp4box_command, shell=True)
        # print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode())

def execute_e3po_tiling():
    # 这个函数目前不需要其他参数，后续可根据需要添加参数
    # 目前的使用场景中只需要用到此命令
    e3po_command = "python ./E3PO/e3po/make_preprocessing.py -approach_name erp -approach_type on_demand"
    try:
        result_e3po = subprocess.check_output(e3po_command, shell=True)
        print(result_e3po.stdout.decode())
    except subprocess.CalledProcessError as e3po_err:
        #print(result.stdout.decode())
        print("error")

# 这个函数用来将yml_content_from_video写入到yml文件中
def write_yml(yml_content_from_video, yml_path, model):
    with open(yml_path, 'r') as file:
        data = yaml.safe_load(file)
    # 先处理一下video_name作为group的名称，删除掉文件名中的后缀
    # print(data)
    group = yml_content_from_video['video_name'].rsplit('.', 1)[0]
    # 修改yml
    # group默认使用文件名
    data['test_group'] = group
    data['e3po_settings']['video'] = {
            'video_duration' : yml_content_from_video['video_duration'],
            # 切整块
            'chunk_duration': yml_content_from_video['video_duration'],
            'video_fps' : yml_content_from_video['video_fps'],
            'origin': {
                'video_name': yml_content_from_video['video_name'],
                # 平台bug，video_dir默认使用当前路径
                'video_dir' : None,
                'projection_mode': yml_content_from_video['projection_mode'],
                'height' : (int(yml_content_from_video['height'])),
                'width' : (int(yml_content_from_video['width'])),
            }
        }
    if (model != 'on_demand'):
        data['e3po_settings'] = {
            'encoding_params': {
                'encoder': yml_content_from_video['encoder'],
                'gop': yml_content_from_video['gop'],
                'bp': yml_content_from_video['bp']
            }
        }
    
    # 写回到yml中
    with open(yml_path, 'w') as file:
        yaml.dump(data, file)
    # 执行e3po
    

# 这个函数是用来使用第二种模式，即编码模式，可以选择指定的编码方式
def add_encoding_to_yml(yml_content_from_video, video_capture ):
    # 指定编码方式
    yml_content_from_video['encoder'] = opt['encoder']
    # 用ffmpeg获取gop 大小
    yml_content_from_video['gop'] = os.popen(f"ffmpeg -i {opt['video_path']} -map 0:v -c copy -f null -").read().split('\n')[-2].split(' ')[-1]
    # 用ffmpeg获取b帧
    yml_content_from_video['bp'] = os.popen(f"ffmpeg -i {opt['video_path']} -map 0:v -c copy -f null -").read().split('\n')[-3].split(' ')[-1]
    return yml_content_from_video

def create_more_version_videos(opt):
    # 使用ffmpeg创建多个视频版本, 4k 2k 1080p ######720p 480p 360p，这部分需要重新处理，e3po不支持 
    # 平台判定中 Invalid too big or non positive size for width '1280' or height '640
    conmands = [f"ffmpeg -i {opt['video_path']} -vf scale=1920:1080 -c:v libx264 -crf 23 -preset medium {opt["video_path"].rsplit(".", 1)[0]}_1080.mp4",
               #f"ffmpeg -i {opt['video_path']} -vf scale=1280:720 -c:v libx264 -crf 23 -preset medium {opt["video_path"].rsplit(".", 1)[0]}_720.mp4",
               #f"ffmpeg -i {opt['video_path']} -vf scale=854:480 -c:v libx264 -crf 23 -preset medium {opt["video_path"].rsplit(".", 1)[0]}_480.mp4",
               #f"ffmpeg -i {opt['video_path']} -vf scale=640:360 -c:v libx264 -crf 23 -preset medium {opt["video_path"].rsplit(".", 1)[0]}_360.mp4"
               ]
    opt["video_path_arr"] = []
    # 执行命令，创建视频版本
    for command in conmands:
        try :
            result = subprocess.check_output(command, shell=True)
            # print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(e.stderr.decode())
            continue
        opt["video_path_arr"].append(command.split(' ')[-1])
    print(opt["video_path_arr"])
    return opt
    


# 主函数，获取参数，主要包括视频地址，appreoach_name，approach_type
if __name__ == '__main__':
    # 获取参数
    parser = argparse.ArgumentParser()
    # 添加参数
    parser.add_argument('--model_select', type=str, default='on_demand', help='default using model on_demand model')
    parser.add_argument('--encoder', type=str, default='libx264', help='encoder')
    parser.add_argument('--video_path', type=str, default='./E3PO/e3po/source/video/simple.mp4', help='path to the video file')
    parser.add_argument('--approach_name', type=str, default='erp', help='approach name')
    parser.add_argument('--approach_type', type=str, default='on_demand', help='approach type')
    # 分块每块的秒数， 默认5s， 这个用于MP4box分段用
    parser.add_argument('--chunk_duration', type=int, default=5, help='chunk duration')
    #分块方式，默认使用erp，6X6矩阵
    parser.add_argument('--chunk_type', type=str, default='erp', help='chunk type')
    args = parser.parse_args()
    # 放入hash
    opt = {}
    opt['encoder'] = args.encoder
    opt['model_select'] = args.model_select
    opt['approach_type'] = args.approach_type
    opt['approach_name'] = args.approach_name
    opt['video_path'] = args.video_path
    opt['chunk_duration'] = args.chunk_duration
    opt['chunk_type'] = args.chunk_type
    
    # 由于需要使用dash协议，所以需要先使用ffmpeg将文件做出多个分辨率版本
    opt = create_more_version_videos(opt)
    # 执行结束后，现在已经有了多个版本,地址存放在opt["video_path_arr"]中
    start_video_line(opt)
    #print(opt)
    

