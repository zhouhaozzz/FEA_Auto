import os
import re
import subprocess
import sys
import time
from geometry import GeometryParameters
import numpy as np
import itertools
import read_write as rw #一些辅助函数
from mpi4py import MPI
import itertools
start_time = time.time()
geom_params = GeometryParameters()
# 获取MPI相关的基本信息
comm = MPI.COMM_WORLD  # 获取默认的通信器
rank = comm.Get_rank()  # 获取当前进程的ID
size = comm.Get_size()  # 获取进程总数

# 计算脚本文件的完整路径
cwd = os.path.dirname(os.getcwd())
geometry_path, heat_flux_path, material_path, thermal_script_path, geometry_script_path, stur_script_path = rw.get_all_path(cwd)
gp_values = rw.get_geomtry_values(geometry_path)
gemo_check, thermal_check = rw.cal_geometry()
colling_type, heat, frequency, l3, b3, t3, OFHC_L_mid3, OFHC_L_side3, GAP_CU3, dw_length3, kong_height3, kong_length3, notch_depth3 = rw.read_ini_geom()
mpi_index = 0    


comm.Barrier() # 等待所有进程完成几何结构计算
#sys.exit()
####### end ############

#Thermal
from geometry import GeometryParameters, Convention
conv_params = Convention()
geom_params = GeometryParameters()
temp_vals, conv_center_vals, conv_side_vals = rw.read_temp_conv()
#temp_num = (len(geometry_path)) * len(heat_flux_path) * len(temp_vals) * len(conv_center_vals) * len(conv_side_vals)
temp_num = (len(geometry_path)) * 1 * len(temp_vals) * len(conv_center_vals) * len(conv_side_vals)

if rank == 0: #拷贝已有负载
    mirror_name = [heat]
    print(heat)

    #mirror_name = ["M1 EEHG"]
    #frequency = ["100k"]
    
    rw.delete_files_in_folder(os.path.join(cwd,"Files", "Heatload"))
    for i in mirror_name:
        for j in frequency:
            rw.creat_heatload_file(cwd, i, j)
    
# exit(0)
comm.Barrier()
geometry_path, heat_flux_path, material_path, thermal_script_path, geometry_script_path, stur_script_path = rw.get_all_path(cwd)
if rank == 0:
    rw.save_heat_flux_path(heat_flux_path)
    print(heat_flux_path)
    # exit(0)

for i, h in enumerate(heat_flux_path, start=0):
    print(h)
    heat_name,extension = os.path.splitext(os.path.basename(h))
    result = heat_name.split('_')
    wavelength = result[1]
    mirror_name = result[2]
    frequency = result[3]
    
    if rank == 0:
        rw.delete_gp_txt(os.path.join(cwd, "out"))
    comm.Barrier() # 等待所有进程完成计算

    para_list = rw.check_temp_cal(cwd, temp_num, geometry_path, h, conv_center_vals, conv_side_vals, temp_vals)
    print(para_list)
    
    if len(para_list) == temp_num:
        subprocess.run(["python", thermal_script_path, str(i), str(rank), str(size), colling_type, "0"])
    comm.Barrier() # 等待所有进程完成计算
    para_list = rw.check_temp_cal(cwd, temp_num, geometry_path, h, conv_center_vals, conv_side_vals, temp_vals)
    kkk=0
    jump=0
    for i in range(2): #多核
        if len(para_list) > 0:
            subprocess.run(["python", thermal_script_path, str(i), str(rank), str(size), colling_type, "1"])
            comm.Barrier() # 等待所有进程完成计算
            para_list = rw.check_temp_cal(cwd, temp_num, geometry_path, h, conv_center_vals, conv_side_vals, temp_vals)
    comm.Barrier() # 等待所有进程完成计算
    if rank == 0:
        for i in range(1): #单核
            if len(para_list) > 0 | len(para_list) < 5:
                subprocess.run(["python", thermal_script_path, str(i), str(rank), str(size), colling_type, "2"])
                para_list = rw.check_temp_cal(cwd, temp_num, geometry_path, h, conv_center_vals, conv_side_vals, temp_vals)
    comm.Barrier() # 等待所有进程完成计算
    
    
    
    if len(para_list) > 0: continue


    #Struct
    output_dir = os.path.join(cwd, "out", "Ansys_out", "Thermal")  # 输出目录 (out 文件夹)
    temperature_path= rw.get_files_from_folder(output_dir, "txt")
    temperature_name = [os.path.basename(path) for path in temperature_path]
    temperature_para = [re.findall(r'\d+\.\d+|\d+', name) for name in temperature_name]
    gemo_single_num = sum(1 for para in temperature_para if int(para[0]) == 1)
    temperature_path_reshape = np.reshape(temperature_path, (-1, gemo_single_num))
    para_list = rw.check_def_cal(cwd, temp_num, geometry_path, temperature_path_reshape)
    if len(para_list) == temp_num:
        subprocess.run(["python", stur_script_path, str(rank), str(size), colling_type, "1"])    
    comm.Barrier() # 等待所有进程完成计算
    para_list = rw.check_def_cal(cwd, temp_num, geometry_path, temperature_path_reshape)
    while len(para_list) > 0:
        subprocess.run(["python", stur_script_path, str(rank), str(size), colling_type, "0"])
        comm.Barrier() # 等待所有进程完成计算
        para_list = rw.check_def_cal(cwd, temp_num, geometry_path, temperature_path_reshape)

    if rank == 0:
        rw.combined_GeometryParameters(size)
        rw.def_to_csv()
        #os.remove(h)
        rw.copy_result_to_target(mirror_name, frequency, wavelength)
    
    comm.Barrier() # 等待所有进程完成计算
    if rank == 0:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{mirror_name} {frequency} {wavelength} 计算完成，总用时: {elapsed_time:.4f} 秒")
