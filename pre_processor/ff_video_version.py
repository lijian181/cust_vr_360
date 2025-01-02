# 创建更多视频版本，向下兼容，最低为1k
import subprocess
import vr_utils
def create_more_version_videos(opt):
    conmands = []
    # 先打开文件查看分辨率信息
    video_capture = vr_utils.open_video_for_info(opt['video_path'])
    if video_capture is None:
        print("无法打开视频文件")
        conmands.append(opt['video_path'])
        return
    # 获取视频信息
    width, height, fps = vr_utils.get_video_data(video_capture)
    # 根据分辨率信息判断创建视频版本，如果小于1k则报错
    if width <= 1280 or height <= 720:
        # 不需要创建任何版本

        return
    # 使用ffmpeg创建多个视频版本, 4k 2k 1080p ######720p 480p 360p，这部分需要重新处理，e3po不支持 
    # 平台判定中 Invalid too big or non positive size for width '1280' or height '640

    # 4k判断
    if (width >= 3840 and width <= 4096) and (height >= 1920 and height <= 2160):
        # 增加2k版本
        conmands.append(f"ffmpeg -i {opt['video_path']} -vf scale=2560:1440 -c:v libx264 -crf 23 -preset medium {opt["video_path"].rsplit(".", 1)[0]}_2k.mp4")
    # 增加1k版本
    conmands.append(f"ffmpeg -i {opt['video_path']} -vf scale=1920:1080 -c:v libx264 -crf 23 -preset medium {opt["video_path"].rsplit(".", 1)[0]}_1k.mp4")
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
    