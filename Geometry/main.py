import os
import re
import subprocess
import sys
import time
import numpy as np
import itertools
from mpi4py import MPI
import itertools
start_time = time.time()
# 获取MPI相关的基本信息
comm = MPI.COMM_WORLD  # 获取默认的通信器
rank = comm.Get_rank()  # 获取当前进程的ID
size = comm.Get_size()  # 获取进程总数 

cwd = os.path.dirname(os.getcwd())
import read_write as rw #一些辅助函数


# 计算脚本文件的完整路径
cwd = os.path.dirname(os.getcwd())

colling_type, heat, frequency, l3, b3, t3, OFHC_L_mid3, OFHC_L_side3, GAP_CU3, dw_length3, kong_height3, kong_length3, notch_depth3, l_optics, b_optics, kaicao, cao_optics, cao_kuan, cao_height = rw.read_ini_geom()

geometry_folder = os.path.join(cwd, "Files", "Model")  # 存放 .agdb 文件 
geometry_path = rw.get_files_from_folder(geometry_folder, 'pmdb')
geometry_script_path = os.path.join(cwd, "Geometry",  "FEA_auto_geom_" + colling_type + ".py")
gp_values = rw.get_geomtry_values(geometry_path)

mpi_index = 0    

print("start cal geometry!!!")
l_vals = np.arange(l3[0], l3[1], l3[2])
b_vals = np.arange(b3[0], b3[1], b3[2])
t_vals = np.arange(t3[0], t3[1], t3[2])
OFHC_L_mid_vals = np.arange(OFHC_L_mid3[0], OFHC_L_mid3[1], OFHC_L_mid3[2])
OFHC_L_side_vals = np.arange(OFHC_L_side3[0], OFHC_L_side3[1], OFHC_L_side3[2])
GAP_CU_vals = np.arange(GAP_CU3[0], GAP_CU3[1], GAP_CU3[2])
dw_length_vals = np.arange(dw_length3[0], dw_length3[1], dw_length3[2])
kong_height_vals = np.arange(kong_height3[0], kong_height3[1], kong_height3[2])
kong_length_vals = np.arange(kong_length3[0], kong_length3[1], kong_length3[2])
notch_depth_vals = np.arange(notch_depth3[0], notch_depth3[1], notch_depth3[2])
for l, b, t, OFHC_L_mid, OFHC_L_side, GAP_CU, dw_length, kong_height, kong_length, notch_depth in itertools.product(
        l_vals, b_vals, t_vals, OFHC_L_mid_vals, OFHC_L_side_vals, GAP_CU_vals, dw_length_vals, kong_height_vals, kong_length_vals, notch_depth_vals):
    
    l3f = "{:.3f}".format(l)
    b3f = "{:.3f}".format(b)
    t3f = "{:.3f}".format(t)
    OFHC_L_mid_3f = "{:.3f}".format(OFHC_L_mid)
    OFHC_L_side_3f = "{:.3f}".format(OFHC_L_side)
    GAP_CU_3f = "{:.3f}".format(GAP_CU)
    dw_length_3f = "{:.3f}".format(dw_length)
    kong_length_3f = "{:.3f}".format(kong_length)
    kong_height_3f = "{:.3f}".format(kong_height)
    notch_depth_3f = "{:.3f}".format(notch_depth)
    
    if mpi_index % size != rank:  #给进程分配任务
        mpi_index += 1
        continue
    gp_check = 0
    for gp_value in gp_values:
        if gp_value[1:] == [l3f, b3f, t3f, OFHC_L_mid_3f, OFHC_L_side_3f, GAP_CU_3f, dw_length_3f, kong_height_3f, kong_length_3f, notch_depth_3f, l_optics, b_optics, kaicao, cao_optics, cao_kuan, cao_height]:
            gp_check = 1
            break
    if gp_check == 1: 
        print("model already exists")
        continue #模型已存在
    subprocess.run(["python", geometry_script_path, l3f, b3f, t3f, OFHC_L_mid_3f, OFHC_L_side_3f, GAP_CU_3f, dw_length_3f, kong_height_3f, kong_length_3f, notch_depth_3f, l_optics, b_optics, kaicao, cao_optics, cao_kuan, cao_height])
    mpi_index += 1
    print([str(mpi_index), l3f, b3f, t3f, OFHC_L_mid_3f, OFHC_L_side_3f, GAP_CU_3f, dw_length_3f, kong_height_3f, kong_length_3f, notch_depth_3f, l_optics, b_optics, kaicao, cao_optics, cao_kuan, cao_height])
print("cal geometry complete!!!")
        
comm.Barrier() # 等待所有进程完成几何结构计算

if rank == 0:
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"几何结构计算完成，总用时: {elapsed_time:.4f} 秒")
