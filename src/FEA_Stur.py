import os
import re
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from PIL import Image
import sys
from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import read_write as rw #一些辅助函数
import time

cwd = os.path.dirname(os.getcwd())
cwd_ansys_out = os.path.join(cwd, "out", "Ansys_out", "Deformation")
def get_object_by_name(name):
    result = [x for x in Tree.AllObjects if x.Name == name]
    return result[0] if result else None
#####################################################
def read_Deformation(rank):
    file_path = os.path.join(cwd_ansys_out, f"def_out_zw_{rank}.txt")
    data = []

    with open(file_path, 'r') as file:
        for line in file:
            if line[0] == 'S': continue
            values = line.strip().split('\t')
            data.append([float(values[0]), float(values[-1])])
    return data

def read_Deformation_sY(rank):
    file_path = os.path.join(cwd_ansys_out, f"def_out_hs_{rank}.txt")
    data = []

    with open(file_path, 'r') as file:
        for line in file:
            if line[0] == 'S': continue
            values = line.strip().split('\t')
            data.append([float(values[0]), float(values[-1])])
    return data

def Deformation_to_dat(filename, data):
    with open(filename, 'w') as file:
        for value in data:
            file.write(f"{value[0]}\t {value[1]}\n")
#####################################################

#cwd_out = os.path.join(cwd, "out", "Deformation")
geometry_path, heat_flux_path, material_path, thermal_script_path, geometry_script_path, stur_script_path = rw.get_all_path(cwd)
geometry_num = len(geometry_path)
rank = int(sys.argv[1])
size = int(sys.argv[2])
colling_type = sys.argv[3]
def_check = int(sys.argv[4])


app=App()
app.update_globals(globals())

# Import Material
Model.Materials.Import(material_path)

# Import geometry
geometry_import_group = Model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()
geometry_import_format = (Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True

GEOM = Model.Geometry
MESH = Model.Mesh
NS = Model.NamedSelections
CONN = Model.Connections
MAT = Model.Materials
CS = Model.CoordinateSystems

analysis1 = Model.AddStaticStructuralAnalysis()
# 定义单位为标准的kg,m,s.
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

size1=MESH.AddSizing()
size2 =MESH.AddSizing()


gp_values = rw.get_geomtry_values(geometry_path)
l2 = float(gp_values[0][1])/2
b2 = float(gp_values[0][2])/2

construction_geometry = Model.AddConstructionGeometry()
path1 = construction_geometry.AddPath()
path1.StartXCoordinate = Quantity(-l2, "m")
path1.EndXCoordinate = Quantity(l2, "m")
path1.NumberOfSamplingPoints = 200

path2 = construction_geometry.AddPath()
path2.StartYCoordinate = Quantity(-b2, "m")
path2.EndYCoordinate = Quantity(b2, "m")
path2.NumberOfSamplingPoints = 30

construction_geometry.UpdateAllSolids()

ST_STU = Model.Analyses[0]
solution_path = Model.Analyses[0].Solution
deformation1 = solution_path.AddDirectionalDeformation()
deformation2 = solution_path.AddDirectionalDeformation()
deformation3 = solution_path.AddDirectionalDeformation()

output_dir = os.path.join(cwd, "out", "Ansys_out", "Thermal")  # 输出目录 (out 文件夹)
temperature_path= rw.get_files_from_folder(output_dir, "txt")
temperature_name = [os.path.basename(path) for path in temperature_path]
temperature_para = [re.findall(r'\d+\.\d+|\d+', name) for name in temperature_name]
gemo_single_num = sum(1 for para in temperature_para if int(para[0]) == 1)
temperature_path_reshape = np.reshape(temperature_path, (-1, gemo_single_num))
temperature_name_reshape = np.reshape(temperature_name, (-1, gemo_single_num))
temperature_para_reshape = np.reshape(temperature_para, (-1, gemo_single_num, 6))

# 生成完整的文件路径
time.sleep(rank/5)  # 等待1秒

init_temp = rw.creat_temp_file(temperature_path[0], cwd, rank)
imported_load = ST_STU.AddImportedLoadExternalData()
external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
external_data_files.SaveFilesWithProject = False
external_data_file = Ansys.Mechanical.ExternalData.ExternalDataFile()
external_data_files.Add(external_data_file)
external_data_file.Identifier = "File1"
external_data_file.Description = ""
external_data_file.IsMainFile = True
external_data_file.FilePath= init_temp
external_data_file.ImportSettings = Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(MechanicalEnums.ExternalData.ImportFormat.Delimited)
import_settings = external_data_file.ImportSettings
import_settings.SkipRows = 1
import_settings.SkipFooter = 0
import_settings.Delimiter = "\t"
import_settings.AverageCornerNodesToMidsideNodes = False
import_settings.UseColumn(0, MechanicalEnums.ExternalData.VariableType.NodeId, "", "Node ID@A")
import_settings.UseColumn(1, MechanicalEnums.ExternalData.VariableType.XCoordinate, "m", "X Coordinate@B")
import_settings.UseColumn(2, MechanicalEnums.ExternalData.VariableType.YCoordinate, "m", "Y Coordinate@C")
import_settings.UseColumn(3, MechanicalEnums.ExternalData.VariableType.ZCoordinate, "m", "Z Coordinate@D")
import_settings.UseColumn(4, MechanicalEnums.ExternalData.VariableType.Temperature, "C", "Temperature@E")
imported_load.ImportExternalDataFiles(external_data_files)
imported_temp = imported_load.AddImportedBodyTemperature()

# 配置导出图片格式
Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1920
settings_720p.Height = 1080
settings_720p.CurrentGraphicsDisplay = False

#模型
mpi_index = -1
index = -1
geom_num = len(str(len(geometry_path))) #model 位数
temp_num = len(str(len(temperature_path))) #总 位数
temp_count = len(temperature_path)

ElementSize_optics_face, ElementSize_ns_inga, ElementSize_ns_mirror, ElementSize_ns_cu = rw.read_mesh_size() #提取网格精度

if (def_check):
    filename = os.path.join(cwd, "out", "GeometryParameters_" + str(rank) + ".txt")
    with open(filename, 'a') as file:
        pass
    for num1, g in enumerate(geometry_path, start=1):  # num1 对应 geometry_path 中的文件
        if (geometry_num >= size):  #模型数大于进程数则平均分配模型给各个进程
            mpi_index += 1
            if mpi_index % size != rank:  #给进程分配任务
                index += gemo_single_num
                continue   
        geometry_import.Import(g, geometry_import_format, geometry_import_preferences)
        mirror = get_object_by_name("Mirror (Mirror)")
        cu1 = get_object_by_name("OFHC_MID (OFHC_MID)")
        cu2 = get_object_by_name("OFHC_POS (OFHC_POS)")
        cu3 = get_object_by_name("OFHC_NEG (OFHC_NEG)")
        inga = get_object_by_name("Inga (Inga)")
        optics_face = get_object_by_name("optics_face")
        ns_mirror = get_object_by_name("ns_mirror")
        # 定义材料参数
        mirror.Material="SI"
        cu1.Material="OFHC"
        cu2.Material="OFHC"
        cu3.Material="OFHC"
        inga.Material="INGA"

        inga.Suppressed = True
        cu1.Suppressed = True
        cu2.Suppressed = True
        cu3.Suppressed = True

        CONN = Model.Connections
        for connection in CONN.Children:
            if connection.DataModelObjectCategory == DataModelObjectCategory.ConnectionGroup:
                connection.Delete()

        # 定义材料参数
        mirror.Material="SI"

        size1.Location = optics_face
        size1.ElementSize=Quantity(ElementSize_optics_face) #2
        size1.Behavior = SizingBehavior.Hard
        size2.Location = ns_mirror
        size2.ElementSize=Quantity(ElementSize_ns_mirror) #6
        #size2.Behavior = SizingBehavior.Hard
        MESH.GenerateMesh()

        deformation1.ScopingMethod = GeometryDefineByType.Path
        deformation1.Path = path1
        deformation1.NormalOrientation = NormalOrientationType.ZAxis
        deformation2.ScopingMethod = GeometryDefineByType.Path
        deformation2.Path = path2
        deformation2.NormalOrientation = NormalOrientationType.ZAxis
        deformation3.ScopingMethod = GeometryDefineByType.Component
        deformation3.Location = optics_face
        deformation3.NormalOrientation = NormalOrientationType.ZAxis

        fileExtension=r".txt"
        for num2, temp_path in enumerate(temperature_path_reshape[num1-1], start=1):
            if (geometry_num >= size):  #模型数大于进程数则平均分配模型给各个进程
                index += 1

            if (geometry_num < size):  #模型数进程数则每个进程计算所有模型
                mpi_index += 1
                index += 1
                if mpi_index % size != rank:  #给进程分配任务
                    continue 
                
            external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
            external_data_files.SaveFilesWithProject = False
            external_data_file = Ansys.Mechanical.ExternalData.ExternalDataFile()
            external_data_files.Add(external_data_file)
            external_data_file.Identifier = "File1"
            external_data_file.Description = ""
            external_data_file.IsMainFile = True
            external_data_file.FilePath= str(temp_path)
            external_data_file.ImportSettings = Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(MechanicalEnums.ExternalData.ImportFormat.Delimited)
            import_settings = external_data_file.ImportSettings
            import_settings.SkipRows = 1
            import_settings.SkipFooter = 0
            import_settings.Delimiter = "\t"
            import_settings.AverageCornerNodesToMidsideNodes = False
            import_settings.UseColumn(0, MechanicalEnums.ExternalData.VariableType.NodeId, "", "Node ID@A")
            import_settings.UseColumn(1, MechanicalEnums.ExternalData.VariableType.XCoordinate, "m", "X Coordinate@B")
            import_settings.UseColumn(2, MechanicalEnums.ExternalData.VariableType.YCoordinate, "m", "Y Coordinate@C")
            import_settings.UseColumn(3, MechanicalEnums.ExternalData.VariableType.ZCoordinate, "m", "Z Coordinate@D")
            import_settings.UseColumn(4, MechanicalEnums.ExternalData.VariableType.Temperature, "C", "Temperature@E")
            imported_load.ImportExternalDataFiles(external_data_files)

            imported_temp.Location=ns_mirror
            imported_temp.ImportLoad()

            print(num1,num2)
            print("几何结构："+os.path.basename(g)+", 参数："+os.path.basename(temp_path))
            temp_name = temperature_name_reshape[num1-1][num2-1]
            temp_para = temperature_para_reshape[num1-1][num2-1]

            ST_STU.AnalysisSettings.WeakSprings = WeakSpringsType.On
            solution_path.Solve()

            newFileName = f"S_deformation_mirror"+temp_name.split("Temperature")[1].split(".txt")[0]
            path = os.path.join(cwd_ansys_out,newFileName+".png")
            Tree.Activate(deformation1)
            Graphics.Camera.SetFit()
            Graphics.ExportImage(path, image_export_format, settings_720p)

            results = solution_path.GetChildren(Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Result,True)
            result0 = results[0]
            fileName = str(result0.Name)
            path = os.path.join(cwd_ansys_out, f"def_out_zw_{rank}.txt")
            result0.ExportToTextFile(path)
            def_data = read_Deformation(rank)
            Deformation_to_dat(os.path.join(cwd,"out", "Deformation", f"{(index+1):0{temp_num}d}" + "_zw.txt"), def_data)
            rw.GeometryParameters_index(f"{(index+1):0{temp_num}d}", gp_values[num1-1], temp_para, rank)

            result1 = results[1]
            path = os.path.join(cwd_ansys_out, f"def_out_hs_{rank}.txt")
            result1.ExportToTextFile(path)
            def_data = read_Deformation_sY(rank)
            Deformation_to_dat(os.path.join(cwd,"out", "Deformation", f"{(index+1):0{temp_num}d}" + "_hs.txt"), def_data)

            result2 = results[2]
            result2.ExportToTextFile(os.path.join(cwd,"out", "Deformation", f"{(index+1):0{temp_num}d}" + "_face.txt"))

            imported_load.ClearGeneratedData()
    #         break
    #     break
            #os.remove(file_path)

else:
    filename = os.path.join(cwd, "out/GeometryParameters_" + str(rank) + ".txt")
    with open(filename, 'a') as file:
        pass
    temp_number = len(temperature_path)
    para_list = rw.check_def_cal(cwd, temp_number, geometry_path, temperature_path_reshape)

    mpi_index = -1
    for para in para_list:
        mpi_index += 1
        if mpi_index % size != rank:  #给进程分配任务
            continue    
        num1 = para[0]
        g = para[1]
        num2 = para[2]
        temp_path = para[3]
        print(num1,num2)

        geometry_import.Import(g, geometry_import_format, geometry_import_preferences)
        mirror = get_object_by_name("Mirror (Mirror)")
        cu1 = get_object_by_name("OFHC_MID (OFHC_MID)")
        cu2 = get_object_by_name("OFHC_POS (OFHC_POS)")
        cu3 = get_object_by_name("OFHC_NEG (OFHC_NEG)")
        inga = get_object_by_name("Inga (Inga)")
        optics_face = get_object_by_name("optics_face")
        ns_mirror = get_object_by_name("ns_mirror")
        mirror.Material="SI"
        cu1.Material="OFHC"
        cu2.Material="OFHC"
        cu3.Material="OFHC"
        inga.Material="INGA"
        inga.Suppressed = True
        cu1.Suppressed = True
        cu2.Suppressed = True
        cu3.Suppressed = True
        CONN = Model.Connections
        for connection in CONN.Children:
            if connection.DataModelObjectCategory == DataModelObjectCategory.ConnectionGroup:
                connection.Delete()
        mirror.Material="SI"
        size1.Location = optics_face
        size1.ElementSize=Quantity(ElementSize_optics_face) #2
        size1.Behavior = SizingBehavior.Hard
        size2.Location = ns_mirror
        size2.ElementSize=Quantity(ElementSize_ns_mirror) #6
        MESH.GenerateMesh()
        deformation1.ScopingMethod = GeometryDefineByType.Path
        deformation1.Path = path1
        deformation1.NormalOrientation = NormalOrientationType.ZAxis
        deformation2.ScopingMethod = GeometryDefineByType.Path
        deformation2.Path = path2
        deformation2.NormalOrientation = NormalOrientationType.ZAxis
        deformation3.ScopingMethod = GeometryDefineByType.Component
        deformation3.Location = optics_face
        deformation3.NormalOrientation = NormalOrientationType.ZAxis
        fileExtension=r".txt"
        external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
        external_data_files.SaveFilesWithProject = False
        external_data_file = Ansys.Mechanical.ExternalData.ExternalDataFile()
        external_data_files.Add(external_data_file)
        external_data_file.Identifier = "File1"
        external_data_file.Description = ""
        external_data_file.IsMainFile = True
        external_data_file.FilePath= str(temp_path)
        external_data_file.ImportSettings = Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(MechanicalEnums.ExternalData.ImportFormat.Delimited)
        import_settings = external_data_file.ImportSettings
        import_settings.SkipRows = 1
        import_settings.SkipFooter = 0
        import_settings.Delimiter = "\t"
        import_settings.AverageCornerNodesToMidsideNodes = False
        import_settings.UseColumn(0, MechanicalEnums.ExternalData.VariableType.NodeId, "", "Node ID@A")
        import_settings.UseColumn(1, MechanicalEnums.ExternalData.VariableType.XCoordinate, "m", "X Coordinate@B")
        import_settings.UseColumn(2, MechanicalEnums.ExternalData.VariableType.YCoordinate, "m", "Y Coordinate@C")
        import_settings.UseColumn(3, MechanicalEnums.ExternalData.VariableType.ZCoordinate, "m", "Z Coordinate@D")
        import_settings.UseColumn(4, MechanicalEnums.ExternalData.VariableType.Temperature, "C", "Temperature@E")
        imported_load.ImportExternalDataFiles(external_data_files)
        imported_temp.Location=ns_mirror
        imported_temp.ImportLoad()
        print(num1,num2)
        print("几何结构："+os.path.basename(g)+", 参数："+os.path.basename(temp_path))
        temp_name = temperature_name_reshape[num1-1][num2-1]
        temp_para = temperature_para_reshape[num1-1][num2-1]
        ST_STU.AnalysisSettings.WeakSprings = WeakSpringsType.On
        solution_path.Solve()
        newFileName = f"S_deformation_mirror"+temp_name.split("Temperature")[1].split(".txt")[0]
        path = os.path.join(cwd_ansys_out,newFileName+".png")
        Tree.Activate(deformation1)
        Graphics.Camera.SetFit()
        Graphics.ExportImage(path, image_export_format, settings_720p)
        results = solution_path.GetChildren(Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Result,True)
        result0 = results[0]
        fileName = str(result0.Name)
        path = os.path.join(cwd_ansys_out, f"def_out_zw_{rank}.txt")
        result0.ExportToTextFile(path)
        def_data = read_Deformation(rank)
        Deformation_to_dat(os.path.join(cwd,"out", "Deformation", f"{(index+1):0{temp_num}d}" + "_zw.txt"), def_data)
        rw.GeometryParameters_index(f"{(index+1):0{temp_num}d}", gp_values[num1-1], temp_para, rank)

        result1 = results[1]
        path = os.path.join(cwd_ansys_out, f"def_out_hs_{rank}.txt")
        result1.ExportToTextFile(path)
        def_data = read_Deformation_sY(rank)
        Deformation_to_dat(os.path.join(cwd,"out", "Deformation", f"{(index+1):0{temp_num}d}" + "_hs.txt"), def_data)

        result2 = results[2]
        result2.ExportToTextFile(os.path.join(cwd,"out", "Deformation", f"{(index+1):0{temp_num}d}" + "_face.txt"))

        imported_load.ClearGeneratedData()
# Close the app
app.close()
os.remove(init_temp) #删除临时文件