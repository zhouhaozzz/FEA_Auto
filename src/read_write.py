import os
import numpy as np
import re
from geometry import GeometryParameters
import glob
import pandas as pd
import os
import itertools
import shutil

cwd = os.path.dirname(os.getcwd())

#######zhou duqu txt############
def read_ini_temp():
    file_path = "parameters.txt"
    a = [0,0,0]
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'temperature:':
                a[0] = float(values[1])
                a[1] = float(values[2])
                a[2] = float(values[3])
    return a[0], a[1], a[2]

def read_geometry():
    file_path = "parameters.txt"
    a = 'none'
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'geometry:':
                a = values[1]
    return a

def read_Temp(gp, h, conv):
    file_path = os.path.join(cwd, "out", "Ansys_out", "Thermal", "Temperature_Geom" + str(gp) + "_Heat" + str(h) + "_Conv" + str(conv) + ".txt")
    data = []

    with open(file_path, 'r') as file:
        for line in file:
            if line[0] == 'N': continue
            values = [v for v in line.strip().split('\t') if v]
            data.append([float(value) for value in values])
    return data

def temp_to_dat(filename, data):
    with open(filename, 'w') as file:
        for value in data:
            file.write(f"{value} \n")

def read_ini_geom_value(gp, value):
    gp[0] = float(value[1])
    gp[1] = float(value[2])
    gp[2] = float(value[3])
    if value[1] == 'y':
       gp[2] = gp[1]
    #print(gp)

    
def read_ini_geom():
    file_path = "parameters.txt"
    geometry = []
    colling_type = []
    heat = []
    frequency = []
    l3 = [0,0,0]
    b3 = [0,0,0]
    t3 = [0,0,0]
    OFHC_L_mid3 = [0,0,0]
    OFHC_L_side3 = [0,0,0]
    GAP_CU3 = [0,0,0]
    dw_length3 = [0,0,0]
    kong_height3 = [0,0,0]
    kong_length3 = [0,0,0]
    notch_depth3 = [0,0,0]
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'geometry:':
                geometry = " ".join(values[1:])
            if values[0] == 'colling_type:':
                colling_type = " ".join(values[1:])
            if values[0] == 'heat_flux:':
                heat = geometry + " " + " ".join(values[1:])
            if values[0] == 'frequency:':
                frequency = [values[1]]
            if values[0] == 'l:':
                read_ini_geom_value(l3, values)
            if values[0] == 'b:':
                read_ini_geom_value(b3, values)
            if values[0] == 't:':
                read_ini_geom_value(t3, values)
            if values[0] == 'OFHC_L_mid:':
                read_ini_geom_value(OFHC_L_mid3, values)
            if values[0] == 'OFHC_L_side:':
                read_ini_geom_value(OFHC_L_side3, values)
            if values[0] == 'GAP_CU:':
                read_ini_geom_value(GAP_CU3, values)
            if values[0] == 'dw_length:':
                read_ini_geom_value(dw_length3, values)
            if values[0] == 'kong_height:':
                read_ini_geom_value(kong_height3, values)
            if values[0] == 'kong_length:':
                read_ini_geom_value(kong_length3, values)
            if values[0] == 'notch_depth:':
                read_ini_geom_value(notch_depth3, values)
    return colling_type, heat, frequency, l3, b3, t3, OFHC_L_mid3, OFHC_L_side3, GAP_CU3, dw_length3, kong_height3, kong_length3, notch_depth3

def read_ini_conv():
    file_path = "parameters.txt"
    conv_center3 = [0,0,0]
    conv_side3 = [0,0,0]
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'conv_center:':
                read_ini_geom_value(conv_center3, values)
            if values[0] == 'conv_side:':
                read_ini_geom_value(conv_side3, values)
    return conv_center3, conv_side3     

def read_flux():
    file_path = "parameters.txt"
    flux = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'heat_flux:':
                read_ini_geom_value(conv_center3, values)
            if values[0] == 'conv_side:':
                read_ini_geom_value(conv_side3, values)
    return conv_center3, conv_side3     

def read_mesh_size():
    file_path = "parameters.txt"
    ElementSize_optics_face = 1.0
    ElementSize_ns_inga = 1.0
    ElementSize_ns_mirror = 1.0
    ElementSize_ns_cu = 1.0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'optics_face(mm):':
                ElementSize_optics_face = values[1] + " [mm]"
            if values[0] == 'ns_inga(mm):':
                ElementSize_ns_inga = values[1] + " [mm]"
            if values[0] == 'ns_mirror(mm):':
                ElementSize_ns_mirror = values[1] + " [mm]"
            if values[0] == 'ns_cu(mm):':
                ElementSize_ns_cu = values[1] + " [mm]"
    return ElementSize_optics_face, ElementSize_ns_inga, ElementSize_ns_mirror, ElementSize_ns_cu

def cal_geometry(): #判断是否创建模型
    check = [0, 0]
    file_path = "parameters.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split(' ') if v]
            if len(values) == 0: continue
            if values[0] == 'cal_geometry:':
                if values[1] == 'yes' : check[0] = 1
            if values[0] == 'cal_thermal:':
                if values[1] == 'yes' : check[1] = 1
    return check[0], check[1]


def get_ini_index():
    file_path = os.path.join(cwd, "out", "index.txt")
    index = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            values = [v for v in line.strip().split('\t') if v]
            index = int(values[0])
    return index

def update_index(index):
    file_path = os.path.join(cwd, "out", "index.txt")
    with open(file_path, 'w') as file:
        file.write(str(index))

def GeometryParameters_index(index, gp, temp_para, rank):
    file_path = os.path.join(cwd, "out", "GeometryParameters_" + str(rank) + ".txt")
    gp_data = GeometryParameters()
    variables = vars(gp_data)
    with open(file_path, 'a') as file:
        file.write(index + ' ')
        file.write(gp[0] + ' ')
        for name, value in variables.items():
            if name == 'l':  file.write(gp[1] + ' ')
            elif name == 'b':  file.write(gp[2] + ' ')
            elif name == 't':  file.write(gp[3] + ' ')
            elif name == 'OFHC_L_mid':  file.write(gp[4] + ' ')
            elif name == 'OFHC_L_side':  file.write(gp[5] + ' ')
            elif name == 'GAP_CU':  file.write(gp[6] + ' ')
            elif name == 'dw_length':  file.write(gp[7] + ' ')
            elif name == 'kong_height':  file.write(gp[8] + ' ')
            elif name == 'kong_length':  file.write(gp[9] + ' ')
            elif name == 'notch_depth':  file.write(gp[10] + ' ')
            else : file.write(f"{value} ")
        file.write(temp_para[1] + ' ')
        file.write(temp_para[2] + ' ')
        file.write(temp_para[3] + ' ')
        file.write(temp_para[4] + ' ')
        file.write(f"\n")    

def get_files_from_folder(folder_path, file_extension):
    """ 获取指定文件夹中的指定扩展名的文件 """
    return glob.glob(os.path.join(folder_path, f"*.{file_extension}"))

def get_all_path(cwd):
    geometry_folder = os.path.join(cwd, "Files", "Model")  # 存放 .agdb 文件 
    heat_flux_folder = os.path.join(cwd, "Files", "Heatload")  # 存放 .txt 文件 
    geometry_path = get_files_from_folder(geometry_folder, 'pmdb')
    heat_flux_path = get_files_from_folder(heat_flux_folder, 'txt')
    material_path= os.path.join(cwd, "Files", "Material", "SYS.engd")
    thermal_script_path = os.path.join(cwd, "src",  "FEA_Thermal.py")
    geometry_script_path = os.path.join(cwd, "src",  "FEA_Geom.py")
    stur_script_path = os.path.join(cwd, "src",  "FEA_Stur.py")
    return geometry_path, heat_flux_path, material_path, thermal_script_path, geometry_script_path, stur_script_path

def creat_heatload_file(cwd, mirror_name, frequency):
    source_folder = os.path.join(cwd,"Files", "HeatFlux collect", mirror_name, frequency)
    destination_folder = os.path.join(cwd,"Files", "Heatload")
    # 遍历源文件夹中的所有文件
    for file_name in os.listdir(source_folder):
        if file_name[-4:] == ".txt":
            # 拼接文件的完整路径
            source_file = os.path.join(source_folder, file_name)
            destination_file = os.path.join(destination_folder, file_name)

            # 如果是文件，执行复制操作
            if os.path.isfile(source_file):
                shutil.copy(source_file, destination_file)  # 使用 shutil.copy2() 也可以保留文件元数据

#判断是否重复计算几何结构
def Split_geometry(file_name): #拆分几何结构命名
    values = file_name.split("Model\\")[1].split(".pmdb")[0]
    values = [part for part in values.split('_') if part]
    return values
def get_geomtry_values(geometry_path):
    gp_values = []
    for filename in geometry_path:
        gp_value = Split_geometry(filename)
        gp_values.append(gp_value)
    return gp_values

def frange(start, stop, step):
    while start <=stop:
        yield round(start, 2)  # 保证输出的小数只有两位
        start += step

def get_temp_num():
    temp_count = 0
    temp_valuem_start, temp_valuem_end, temp_valuem_step = read_ini_temp()
    temp_valuem = temp_valuem_start
    while temp_valuem <= temp_valuem_end:
        temp_count += 1
        temp_valuem += temp_valuem_step
    return temp_count

def combined_GeometryParameters(size):
    print("所有进程计算完成！")
    data = []
    data_num = []
    for r in range(size):
        file_path = os.path.join(cwd,"out", f"GeometryParameters_{r}.txt")
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                data.append(line)
                values = [v for v in line.strip().split(' ') if v]
                data_num.append(int(values[0]))
    data_cache = data.copy()         
    data = [data_cache[i] for i in np.argsort(data_num)]     
    if len(data) > 0:
        file_path = os.path.join(cwd,"out", "GeometryParameters.txt")
        with open(file_path, 'w') as file:
            for value in data:
                file.write(value)
    else:
        print("没有有效数据可供合并。")


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    plt.imshow(mpimg.imread(os.path.join(cwd_out, image_name)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()

def get_digit_count(number):
    if number > 0:
        return len(str(number))
    else:
        raise ValueError("Input must be a positive integer")
def delete_gp_txt(folder_path):
    files_to_delete = glob.glob(os.path.join(folder_path, 'GeometryParameters*.txt'))
    for file_path in files_to_delete: os.remove(file_path)
    files_to_delete = glob.glob(os.path.join(folder_path, "Ansys_out", "Deformation", "*"))
    for file_path in files_to_delete: os.remove(file_path)
    files_to_delete = glob.glob(os.path.join(folder_path, "Ansys_out", "Thermal", "*"))
    for file_path in files_to_delete: os.remove(file_path)
    files_to_delete = glob.glob(os.path.join(folder_path, "Deformation", "*"))
    for file_path in files_to_delete: os.remove(file_path)

def def_to_csv():
    folder_path = os.path.join(cwd,"out", "Deformation")
    file_list = [f for f in os.listdir(folder_path) if f.endswith('_zw.txt')]

    matrix_list = []
    for file in file_list:
        file_path = os.path.join(folder_path, file)
        data = np.loadtxt(file_path)
        matrix_list.append(data)
    result_matrix = np.hstack(matrix_list).T
    save_path = os.path.join(cwd, "out", "deformation_trans.csv")
    np.savetxt(save_path, result_matrix, delimiter=',')
    print(result_matrix.shape)
    print("文件已保存到：", save_path)

    file_list = [f for f in os.listdir(folder_path) if f.endswith('_hs.txt')]
    matrix_list = []
    for file in file_list:
            file_path = os.path.join(folder_path, file)
            data = np.loadtxt(file_path)
            matrix_list.append(data)

    result_matrix = np.hstack(matrix_list).T
    print(result_matrix.shape)
    save_path = os.path.join(cwd, "out", "deformation_trans_Y.csv")
    np.savetxt(save_path, result_matrix, delimiter=',')
    print("文件已保存到：", save_path)
    
def cheak_thermal_result():
    geometry_folder = os.path.join(cwd, "Files", "Model")  # 存放 .agdb 文件 
    geometry_path = get_files_from_folder(geometry_folder, 'pmdb')
    temp_center3 = read_ini_temp()
    temp_vals = np.arange(temp_center3[0], temp_center3[1], temp_center3[2])
    conv_center3, conv_side3 = read_ini_conv()
    conv_center_vals = np.arange(conv_center3[0], conv_center3[1], conv_center3[2])
    conv_side_vals = np.arange(conv_side3[0], conv_side3[1], conv_side3[2])
    temp_num = (len(geometry_path)) * len(temp_vals) * len(conv_center_vals) * len(conv_side_vals)
    
    full_temp = set(range(1, temp_num+1))
    output_dir = os.path.join(cwd, "out", "Ansys_out", "Thermal")  # 输出目录 (out 文件夹)
    temperature_path= get_files_from_folder(output_dir, "png")
    temperature_name = [os.path.basename(path) for path in temperature_path]
    temp_number = []
    for i in temperature_name:
        temp_number.append(int(re.search(r'(\d+).png',i).group(1)))
    temp_number = set(temp_number) 
    cal_num = list(full_temp - temp_number)
    if len(cal_num) > 0: check = 1
    else: check = 0

    return check
    
def read_temp_conv():
    temp_center3 = read_ini_temp()
    temp_vals = np.arange(temp_center3[0], temp_center3[1], temp_center3[2])
    conv_center3, conv_side3 = read_ini_conv()
    conv_center_vals = np.arange(conv_center3[0], conv_center3[1], conv_center3[2])
    conv_side_vals = np.arange(conv_side3[0], conv_side3[1], conv_side3[2])
    return temp_vals, conv_center_vals, conv_side_vals
    
def check_temp_cal(cwd, temp_num, geometry_path, heat_flux_path, conv_center_vals, conv_side_vals, temp_vals):
    full_temp = set(range(1, temp_num+1))
    output_dir = os.path.join(cwd, "out", "Ansys_out", "Thermal")  # 输出目录 (out 文件夹)
    temperature_path= get_files_from_folder(output_dir, "txt")
    temperature_name = [os.path.basename(path) for path in temperature_path]
    temp_number = []
    for i in temperature_name:
        temp_number.append(int(re.search(r'(\d+).txt',i).group(1)))
    temp_number = set(temp_number) 
    cal_num = list(full_temp - temp_number)

    count = 1
    para_list = []
    for num1, g in enumerate(geometry_path, start=1):  # num1 对应 geometry_path 中的文件
        for conv_center, conv_side, temp_center in itertools.product(conv_center_vals, conv_side_vals, temp_vals):
            if count in cal_num:
                para_list.append([num1, g, heat_flux_path, conv_center, conv_side, temp_center, count])
            count += 1
    return para_list

def check_def_cal(cwd, temp_num, geometry_path, temperature_path_reshape):
    full_def = set(range(1, temp_num+1))
    output_dir = os.path.join(cwd, "out", "Deformation")  # 输出目录 (out 文件夹)
    def_path= get_files_from_folder(output_dir, "txt")
    def_name = [os.path.basename(path) for path in def_path]
    def_number = []
    for i in def_name:
        if i[-5]== 'e':
            def_number.append(int(re.search(r'(\d+)_face',i).group(1)))
    def_number = set(def_number) 
    cal_num = list(full_def - def_number)

    count = 1
    para_list = []
    for num1, g in enumerate(geometry_path, start=1):  # num1 对应 geometry_path 中的文件
        for num2, temp_path in enumerate(temperature_path_reshape[num1-1], start=1):
            if count in cal_num:
                para_list.append([num1, g, num2, temp_path, count])
            count += 1
    return para_list

def creat_temp_file(temp_name, cwd, rank):
    filename = os.path.join(cwd, "out", "Ansys_out", "Deformation", str(rank)+".txt")
    shutil.copy(temp_name, filename)
    return filename

def copy_result_to_target(mirror_name, frequency, flux):
    # 指定路径
    folder_path = os.path.join(cwd, "out", "def_cache", mirror_name, frequency, flux)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"文件夹 {folder_path} 已创建")
        
    shutil.copytree(os.path.join(cwd, "out", "Ansys_out"), os.path.join(folder_path, os.path.basename('out/Ansys_out')), dirs_exist_ok=True)
    shutil.copytree(os.path.join(cwd, "out", "Deformation"), os.path.join(folder_path, os.path.basename('out/Deformation')), dirs_exist_ok=True)
    shutil.copy(os.path.join(cwd, "out", "deformation_trans.csv"), os.path.join(folder_path, os.path.basename('out/deformation_trans.csv')))
    shutil.copy(os.path.join(cwd, "out", "deformation_trans_Y.csv"), os.path.join(folder_path, os.path.basename('out/deformation_trans_Y.csv')))
    shutil.copy(os.path.join(cwd, "out", "GeometryParameters.txt"), os.path.join(folder_path, os.path.basename('out/GeometryParameters.txt')))
    
def delete_files_in_folder(folder_path):
    """ 删除文件夹中的所有文件，但不删除子文件夹 """
    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # 如果是文件，删除它
        if os.path.isfile(file_path):
            os.remove(file_path)

def save_heat_flux_path(heat_flux_path):
    filename = os.path.join(cwd, "out", "Init HeatFlux List.txt")
    with open(filename, 'w') as file:
        for flux in heat_flux_path:
            file.write(flux + "\n")
            
def read_ini_heat_flux_path():
    heat_flux_path = []
    filename  = os.path.join(cwd, "out", "Init HeatFlux List.txt")
    with open(filename, 'r') as file:
        for line in file:
            heat_flux_path.append(line[:-1])
    return heat_flux_path