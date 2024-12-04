# 这个文件用来做一些简单工具

# 翻滚角roll、俯仰角pitch、偏航角yaw计算
# 使用前提，拥有四元组坐标，以数组的形式传入，或者以单独的元素传入
import math

def get_all_angles(arr):
    # q是一个四个元素的数组, x y z w arr[0] arr[1] arr[2] arr[3]
    # 翻滚角                
    roll = math.atan2(2 * (arr[3] * arr[2] + arr[0] * arr[1]), 1 - 2 * (arr[0] * arr[0] + arr[2] * arr[2]))
    # 俯仰角
    pitch = math.asin(2 * (arr[3] * arr[0] - arr[2] * arr[1]))
    # 偏航角
    yaw = math.atan2(2 * (arr[3] * arr[1] + arr[2] * arr[0]) , 1 - 2 * (arr[0] * arr[0] + arr[1] * arr[1]))
    return roll, pitch, yaw

