import os
import sys
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
from PIL import Image
from ansys.mechanical.core import App
from geometry import GeometryParameters, Convention
import numpy as np
import read_write as rw #一些辅助函数
import itertools
import time

# # 将标准输出重定向到 os.devnull
# sys.stdout = open(os.devnull, 'w')

def get_object_by_name(name):
    result = [x for x in Tree.AllObjects if x.Name == name]
    return result[0] if result else None
geom_params = GeometryParameters()
conv_params = Convention()
cwd = os.path.dirname(os.getcwd())
cwd_out = os.path.join(cwd, "out", "Ansys_out", "Thermal")
geometry_path, heat_flux_path, material_path, thermal_script_path, geometry_script_path, stur_script_path = rw.get_all_path(cwd)
geometry_num = len(geometry_path)
heat_flux_path = rw.read_ini_heat_flux_path()
heat_flux_index = int(sys.argv[1])
heat_flux_path = heat_flux_path[heat_flux_index]
rank = int(sys.argv[2])
size = int(sys.argv[3])
colling_type = sys.argv[4]
temp_check = int(sys.argv[5])

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

# 导入热力学分析
# Add static analysis to the Model.
analysis1 = Model.AddSteadyStateThermalAnalysis()
# 定义单位为标准的kg,m,s.
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

if (colling_type == "INGA 3" or colling_type == "INGA 1" ):
    size1 = MESH.AddSizing()
    size2 = MESH.AddSizing()
    size3 = MESH.AddSizing()
    size4 = MESH.AddSizing()
elif (colling_type == "IN 3" or colling_type == "IN 1" ):
    size1 = MESH.AddSizing()
    size2 = MESH.AddSizing()
    size3 = MESH.AddSizing()


ST_STA = Model.Analyses[0]
STAT_THERM_SOLN = Model.Analyses[0].Solution
# Add heat transfer
if (colling_type == "INGA 3" or colling_type == "IN 3"):
    conv1 = analysis1.AddConvection()
    conv2 = analysis1.AddConvection()
    conv3 = analysis1.AddConvection()
elif (colling_type == "INGA 1"or colling_type == "INGA 1"):
    conv1 = analysis1.AddConvection()
TEMP_Mirror = STAT_THERM_SOLN.AddTemperature()
CONT_REG1 = []
CONT_REG2 = []
CONT_REG3 = []
CONT_REG4 = []

# Add Heatflux
time.sleep(rank/5+0.5) 
imported_load = ST_STA.AddImportedLoadExternalData()
external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
external_data_files.SaveFilesWithProject = False
external_data_file = Ansys.Mechanical.ExternalData.ExternalDataFile()
external_data_files.Add(external_data_file)
external_data_file.Identifier = "File1"
external_data_file.Description = ""
external_data_file.IsMainFile = True
external_data_file.FilePath = heat_flux_path[0]
external_data_file.ImportSettings = Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(MechanicalEnums.ExternalData.ImportFormat.Delimited)
import_settings = external_data_file.ImportSettings
import_settings.SkipRows = 1
import_settings.SkipFooter = 0
import_settings.Delimiter = ","
import_settings.AverageCornerNodesToMidsideNodes = False
import_settings.UseColumn(0, MechanicalEnums.ExternalData.VariableType.XCoordinate, "mm", "X Coordinate@A")
import_settings.UseColumn(1, MechanicalEnums.ExternalData.VariableType.YCoordinate, "mm", "Y Coordinate@B")
import_settings.UseColumn(2, MechanicalEnums.ExternalData.VariableType.HeatFlux, "W mm^-2", "Heat Flux@C")
imported_load.ImportExternalDataFiles(external_data_files)
imported_heatflux = imported_load.AddImportedHeatFlux()

temp_center3 = rw.read_ini_temp()
temp_vals = np.arange(temp_center3[0], temp_center3[1], temp_center3[2])
temp_value = conv_params.temp_value
conv_center3, conv_side3 = rw.read_ini_conv()
conv_center_vals = np.arange(conv_center3[0], conv_center3[1], conv_center3[2])
conv_side_vals = np.arange(conv_side3[0], conv_side3[1], conv_side3[2])

# 配置导出图片格式
Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1920
settings_720p.Height = 1080
settings_720p.CurrentGraphicsDisplay = False

appointed_task_id = []
temp_index = []
#模型
temp_num = geometry_num * len(temp_vals) * len(conv_center_vals) * len(conv_side_vals)
temp_num_mini = len(temp_vals) * len(conv_center_vals) * len(conv_side_vals)
total_digit = len(str(temp_num+1))
mpi_index = -1
cal_index = -1
geom_num = len(str(geometry_num)) #model 位数
ElementSize_optics_face, ElementSize_ns_inga, ElementSize_ns_mirror, ElementSize_ns_cu = rw.read_mesh_size() #提取网格精度

if (temp_check==0):
    for num1, g in enumerate(geometry_path, start=1):  # num1 对应 geometry_path 中的文件
        if (geometry_num >= size):  #模型数大于进程数则平均分配模型给各个进程
            mpi_index += 1
            if mpi_index % size != rank:  #给进程分配任务
                cal_index += temp_num_mini
                continue     
        geometry_import.Import(g, geometry_import_format, geometry_import_preferences)
        if (colling_type == "INGA 3"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            cu_pos = get_object_by_name("OFHC_POS (OFHC_POS)")
            cu_neg = get_object_by_name("OFHC_NEG (OFHC_NEG)")
            inga = get_object_by_name("Inga (Inga)")
            optics_face = get_object_by_name("optics_face")
            inga_conn_mirror = get_object_by_name("inga_conn_mirror")
            mirror_conn_inga = get_object_by_name("mirror_conn_inga")
            inga_conn_ofhcn = get_object_by_name("inga_conn_ofhcn")
            inga_conn_ofhcm = get_object_by_name("inga_conn_ofhcm")
            inga_conn_ofhcp = get_object_by_name("inga_conn_ofhcp")
            ofhcn_conn_inga = get_object_by_name("ofhcn_conn_inga")
            ofhcm_conn_inga = get_object_by_name("ofhcm_conn_inga")
            ofhcp_conn_inga = get_object_by_name("ofhcp_conn_inga")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_inga = get_object_by_name("ns_inga")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            sanre_neg = get_object_by_name("sanre_neg")
            sanre_pos = get_object_by_name("sanre_pos")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            cu_pos.Material="OFHC"
            cu_neg.Material="OFHC"
            inga.Material="INGA"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_inga
            size2.ElementSize=Quantity(ElementSize_ns_inga)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_mirror
            size3.ElementSize=Quantity(ElementSize_ns_mirror)
            size3.Behavior = SizingBehavior.Hard
            size4.Location = ns_cu
            size4.ElementSize=Quantity(ElementSize_ns_cu)
            size4.Behavior = SizingBehavior.Hard
        elif (colling_type == "INGA 1"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            inga = get_object_by_name("Inga (Inga)")
            optics_face = get_object_by_name("optics_face")
            inga_conn_mirror = get_object_by_name("inga_conn_mirror")
            mirror_conn_inga = get_object_by_name("mirror_conn_inga")
            inga_conn_ofhcm = get_object_by_name("inga_conn_ofhcm")
            ofhcm_conn_inga = get_object_by_name("ofhcm_conn_inga")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_inga = get_object_by_name("ns_inga")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            inga.Material="INGA"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_inga
            size2.ElementSize=Quantity(ElementSize_ns_inga)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_mirror
            size3.ElementSize=Quantity(ElementSize_ns_mirror)
            size3.Behavior = SizingBehavior.Hard
            size4.Location = ns_cu
            size4.ElementSize=Quantity(ElementSize_ns_cu)
            size4.Behavior = SizingBehavior.Hard
        elif (colling_type == "IN 1"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            cu_neg = get_object_by_name("OFHC_NEG (OFHC_NEG)")
            optics_face = get_object_by_name("optics_face")
            cu_conn_mirror_neg = get_object_by_name("cu_conn_mirror_neg")
            cu_conn_mirror_mid = get_object_by_name("cu_conn_mirror_mid")
            mirror_conn_cu_neg = get_object_by_name("mirror_conn_cu_neg")
            mirror_conn_cu_mid = get_object_by_name("mirror_conn_cu_mid")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            cu_neg.Material="OFHC"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_mirror
            size2.ElementSize=Quantity(ElementSize_ns_mirror)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_cu
            size3.ElementSize=Quantity(ElementSize_ns_cu)
            size3.Behavior = SizingBehavior.Hard


        MESH.GenerateMesh()

        Tree.Activate(MESH)
        Graphics.Camera.SetFit()
        Graphics.ExportImage("mesh.png", image_export_format, settings_720p)

        CONN = Model.Connections
        for connection in CONN.Children:
            if connection.DataModelObjectCategory == DataModelObjectCategory.ConnectionGroup:
                connection.Delete()

        if (colling_type == "INGA 3"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG3 = CONN.AddContactRegion()
            CONT_REG4 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = inga_conn_mirror
            CONT_REG1.TargetLocation = mirror_conn_inga
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = inga_conn_ofhcn
            CONT_REG2.TargetLocation = ofhcn_conn_inga
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
            CONT_REG3.SourceLocation = inga_conn_ofhcm
            CONT_REG3.TargetLocation = ofhcm_conn_inga
            CONT_REG3.ContactType = ContactType.NoSeparation
            CONT_REG3.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG3.AutomaticThermalConductance = False
            CONT_REG4.SourceLocation = inga_conn_ofhcp
            CONT_REG4.TargetLocation = ofhcp_conn_inga
            CONT_REG4.ContactType = ContactType.NoSeparation
            CONT_REG4.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG4.AutomaticThermalConductance = False
        elif (colling_type == "INGA 1"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = inga_conn_mirror
            CONT_REG1.TargetLocation = mirror_conn_inga
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = inga_conn_ofhcm
            CONT_REG2.TargetLocation = ofhcm_conn_inga
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
        elif (colling_type == "IN 1"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = cu_conn_mirror_neg
            CONT_REG1.TargetLocation = mirror_conn_cu_neg
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = cu_conn_mirror_mid
            CONT_REG2.TargetLocation = mirror_conn_cu_mid
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
            


        TEMP_Mirror.Location = ns_mirror
        TEMP_Mirror.ScopingMethod = GeometryDefineByType.Component

        external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
        external_data_files.SaveFilesWithProject = False
        external_data_file = Ansys.Mechanical.ExternalData.ExternalDataFile()
        external_data_files.Add(external_data_file)
        external_data_file.Identifier = "File1"
        external_data_file.Description = ""
        external_data_file.IsMainFile = True
        external_data_file.FilePath = heat_flux_path
        external_data_file.ImportSettings = Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(MechanicalEnums.ExternalData.ImportFormat.Delimited)
        import_settings = external_data_file.ImportSettings
        import_settings.SkipRows = 1
        import_settings.SkipFooter = 0
        import_settings.Delimiter = ","
        import_settings.AverageCornerNodesToMidsideNodes = False
        import_settings.UseColumn(0, MechanicalEnums.ExternalData.VariableType.XCoordinate, "mm", "X Coordinate@A")
        import_settings.UseColumn(1, MechanicalEnums.ExternalData.VariableType.YCoordinate, "mm", "Y Coordinate@B")
        import_settings.UseColumn(2, MechanicalEnums.ExternalData.VariableType.HeatFlux, "W mm^-2", "Heat Flux@C")
        imported_load.ImportExternalDataFiles(external_data_files)
        imported_heatflux.Location=optics_face
        imported_heatflux.ImportLoad()

        #print(num1,num2)
        print("几何结构："+os.path.basename(g)+", 负载："+os.path.basename(heat_flux_path))
        # 水温、对流换热
        for conv_center, conv_side, temp_center in itertools.product(conv_center_vals, conv_side_vals, temp_vals):
            cal_index += 1
            if (geometry_num < size):  #模型数大于进程数则每个进程计算所有模型
                mpi_index += 1
                if mpi_index % size != rank:  #给进程分配任务
                    continue 
            conv_center, conv_side = int(conv_center), int(conv_side)
            temp_center = float("{:.1f}".format(temp_center))
            if (colling_type == "INGA 3"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))

                conv2.Location = sanre_neg
                conv2.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_side, "W m^-1 m^-1 C^-1"))
                conv2.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_value, "C"))

                conv3.Location = sanre_pos
                conv3.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_side, "W m^-1 m^-1 C^-1"))
                conv3.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_value, "C"))
            elif (colling_type == "INGA 1"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))
            elif (colling_type == "IN 3"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))

            STAT_THERM_SOLN.Solve()

            fileExtension=r".txt"
            results = STAT_THERM_SOLN.GetChildren(Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Result,True)

            result = results[0]
            fileName = str(result.Name)
            newFileName = f"{fileName}_Geom{num1:0{geom_num}d}_Heat{heat_flux_index}_ConvCenter{conv_center}_ConvSide{conv_side}_temp" + "{:.1f}".format(temp_center) + f" {(cal_index+1):0{total_digit}d}" # 格式化文件名
            path = os.path.join(cwd_out,newFileName+fileExtension)
            result.ExportToTextFile(path)

            Tree.Activate(TEMP_Mirror)
            Graphics.Camera.SetFit()
            newFileName = newFileName
            Graphics.ExportImage(os.path.join(cwd_out,newFileName+".png"), image_export_format, settings_720p)
            
            Messages = ExtAPI.Application.Messages
            if Messages:
                for message in Messages:
                    print(f"[{message.Severity}] {message.DisplayString}")
            else:
                print("No [Info]/[Warning]/[Error] Messages")

            print("Thermal done, Model: " +str(num1)+"#, Heat: "+str(heat_flux_index)+"#, 水温: " + str(temp_center) +"#, 对流换热系数: " + str(conv_center) +" "+str(conv_side))
            STAT_THERM_SOLN.ClearGeneratedData()
#             break
        imported_load.ClearGeneratedData()
#         break
#     break
elif (temp_check==1):
    para_list = rw.check_temp_cal(cwd, temp_num, geometry_path, heat_flux_path, conv_center_vals, conv_side_vals, temp_vals)
    print(para_list)
    mpi_index = -1
    for para in para_list:
        mpi_index += 1
        if mpi_index % size != rank:  #给进程分配任务
            continue    
        print(para[-1])
        num1 = para[0]
        g = para[1]
        h = para[2]
        conv_center = para[3]
        conv_side = para[4]
        temp_center = para[5]
        geometry_import_format = (Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic)
        geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
        geometry_import_preferences.ProcessNamedSelections = True
        geometry_import.Import(g, geometry_import_format, geometry_import_preferences)
        if (colling_type == "INGA 3"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            cu_pos = get_object_by_name("OFHC_POS (OFHC_POS)")
            cu_neg = get_object_by_name("OFHC_NEG (OFHC_NEG)")
            inga = get_object_by_name("Inga (Inga)")
            optics_face = get_object_by_name("optics_face")
            inga_conn_mirror = get_object_by_name("inga_conn_mirror")
            mirror_conn_inga = get_object_by_name("mirror_conn_inga")
            inga_conn_ofhcn = get_object_by_name("inga_conn_ofhcn")
            inga_conn_ofhcm = get_object_by_name("inga_conn_ofhcm")
            inga_conn_ofhcp = get_object_by_name("inga_conn_ofhcp")
            ofhcn_conn_inga = get_object_by_name("ofhcn_conn_inga")
            ofhcm_conn_inga = get_object_by_name("ofhcm_conn_inga")
            ofhcp_conn_inga = get_object_by_name("ofhcp_conn_inga")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_inga = get_object_by_name("ns_inga")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            sanre_neg = get_object_by_name("sanre_neg")
            sanre_pos = get_object_by_name("sanre_pos")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            cu_pos.Material="OFHC"
            cu_neg.Material="OFHC"
            inga.Material="INGA"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_inga
            size2.ElementSize=Quantity(ElementSize_ns_inga)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_mirror
            size3.ElementSize=Quantity(ElementSize_ns_mirror)
            size3.Behavior = SizingBehavior.Hard
            size4.Location = ns_cu
            size4.ElementSize=Quantity(ElementSize_ns_cu)
            size4.Behavior = SizingBehavior.Hard
        elif (colling_type == "INGA 1"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            inga = get_object_by_name("Inga (Inga)")
            optics_face = get_object_by_name("optics_face")
            inga_conn_mirror = get_object_by_name("inga_conn_mirror")
            mirror_conn_inga = get_object_by_name("mirror_conn_inga")
            inga_conn_ofhcm = get_object_by_name("inga_conn_ofhcm")
            ofhcm_conn_inga = get_object_by_name("ofhcm_conn_inga")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_inga = get_object_by_name("ns_inga")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            inga.Material="INGA"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_inga
            size2.ElementSize=Quantity(ElementSize_ns_inga)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_mirror
            size3.ElementSize=Quantity(ElementSize_ns_mirror)
            size3.Behavior = SizingBehavior.Hard
            size4.Location = ns_cu
            size4.ElementSize=Quantity(ElementSize_ns_cu)
            size4.Behavior = SizingBehavior.Hard
        elif (colling_type == "IN 1"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            cu_neg = get_object_by_name("OFHC_NEG (OFHC_NEG)")
            optics_face = get_object_by_name("optics_face")
            cu_conn_mirror_neg = get_object_by_name("cu_conn_mirror_neg")
            cu_conn_mirror_mid = get_object_by_name("cu_conn_mirror_mid")
            mirror_conn_cu_neg = get_object_by_name("mirror_conn_cu_neg")
            mirror_conn_cu_mid = get_object_by_name("mirror_conn_cu_mid")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            cu_neg.Material="OFHC"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_mirror
            size2.ElementSize=Quantity(ElementSize_ns_mirror)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_cu
            size3.ElementSize=Quantity(ElementSize_ns_cu)
            size3.Behavior = SizingBehavior.Hard
        
        MESH.GenerateMesh()
        CONN = Model.Connections
        for connection in CONN.Children:
            if connection.DataModelObjectCategory == DataModelObjectCategory.ConnectionGroup:
                connection.Delete()
        if (colling_type == "INGA 3"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG3 = CONN.AddContactRegion()
            CONT_REG4 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = inga_conn_mirror
            CONT_REG1.TargetLocation = mirror_conn_inga
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = inga_conn_ofhcn
            CONT_REG2.TargetLocation = ofhcn_conn_inga
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
            CONT_REG3.SourceLocation = inga_conn_ofhcm
            CONT_REG3.TargetLocation = ofhcm_conn_inga
            CONT_REG3.ContactType = ContactType.NoSeparation
            CONT_REG3.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG3.AutomaticThermalConductance = False
            CONT_REG4.SourceLocation = inga_conn_ofhcp
            CONT_REG4.TargetLocation = ofhcp_conn_inga
            CONT_REG4.ContactType = ContactType.NoSeparation
            CONT_REG4.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG4.AutomaticThermalConductance = False
        elif (colling_type == "INGA 1"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = inga_conn_mirror
            CONT_REG1.TargetLocation = mirror_conn_inga
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = inga_conn_ofhcm
            CONT_REG2.TargetLocation = ofhcm_conn_inga
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
        elif (colling_type == "IN 1"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = cu_conn_mirror_neg
            CONT_REG1.TargetLocation = mirror_conn_cu_neg
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = cu_conn_mirror_mid
            CONT_REG2.TargetLocation = mirror_conn_cu_mid
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False

        TEMP_Mirror.Location = ns_mirror
        TEMP_Mirror.ScopingMethod = GeometryDefineByType.Component
        external_data_file.FilePath = h
        imported_heatflux.Location=optics_face
        imported_heatflux.ImportLoad()
        conv_center, conv_side = int(conv_center), int(conv_side)
        temp_center = float("{:.1f}".format(temp_center))
        if (colling_type == "INGA 3"):
            conv1.Location = sanre_mid
            conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
            conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))

            conv2.Location = sanre_neg
            conv2.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_side, "W m^-1 m^-1 C^-1"))
            conv2.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_value, "C"))

            conv3.Location = sanre_pos
            conv3.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_side, "W m^-1 m^-1 C^-1"))
            conv3.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_value, "C"))
        elif (colling_type == "INGA 1"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))
        elif (colling_type == "IN 3"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))

        STAT_THERM_SOLN.Solve()
        fileExtension=r".txt"
        results = STAT_THERM_SOLN.GetChildren(Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Result,True)
        result = results[0]
        fileName = str(result.Name)
        newFileName = f"{fileName}_Geom{num1:0{geom_num}d}_Heat{heat_flux_index}_ConvCenter{conv_center}_ConvSide{conv_side}_temp" + "{:.1f}".format(temp_center) + f" {(para[-1]):0{total_digit}d}" # 格式化文件名
        path = os.path.join(cwd_out,newFileName+fileExtension)
        result.ExportToTextFile(path)

        Tree.Activate(TEMP_Mirror)
        Graphics.Camera.SetFit()
        newFileName = newFileName
        Graphics.ExportImage(os.path.join(cwd_out,newFileName+".png"), image_export_format, settings_720p)
        
        Messages = ExtAPI.Application.Messages
        if Messages:
            for message in Messages:
                print(f"[{message.Severity}] {message.DisplayString}")
        else:
            print("No [Info]/[Warning]/[Error] Messages")

        print("Thermal done, Model: " +str(num1)+"#, Heat: "+str(heat_flux_index)+"#, 水温: " + str(temp_center) +"#, 对流换热系数: " + str(conv_center) +" "+str(conv_side))
        STAT_THERM_SOLN.ClearGeneratedData()
        imported_heatflux.ClearGeneratedData()
        
else:
    para_list = rw.check_temp_cal(cwd, temp_num, geometry_path, heat_flux_path, conv_center_vals, conv_side_vals, temp_vals)
    print(para_list)
    for para in para_list:
        print(para[-1])
        num1 = para[0]
        g = para[1]
        h = para[2]
        conv_center = para[3]
        conv_side = para[4]
        temp_center = para[5]
        geometry_import_format = (Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic)
        geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
        geometry_import_preferences.ProcessNamedSelections = True
        geometry_import.Import(g, geometry_import_format, geometry_import_preferences)
        if (colling_type == "INGA 3"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            cu_pos = get_object_by_name("OFHC_POS (OFHC_POS)")
            cu_neg = get_object_by_name("OFHC_NEG (OFHC_NEG)")
            inga = get_object_by_name("Inga (Inga)")
            optics_face = get_object_by_name("optics_face")
            inga_conn_mirror = get_object_by_name("inga_conn_mirror")
            mirror_conn_inga = get_object_by_name("mirror_conn_inga")
            inga_conn_ofhcn = get_object_by_name("inga_conn_ofhcn")
            inga_conn_ofhcm = get_object_by_name("inga_conn_ofhcm")
            inga_conn_ofhcp = get_object_by_name("inga_conn_ofhcp")
            ofhcn_conn_inga = get_object_by_name("ofhcn_conn_inga")
            ofhcm_conn_inga = get_object_by_name("ofhcm_conn_inga")
            ofhcp_conn_inga = get_object_by_name("ofhcp_conn_inga")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_inga = get_object_by_name("ns_inga")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            sanre_neg = get_object_by_name("sanre_neg")
            sanre_pos = get_object_by_name("sanre_pos")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            cu_pos.Material="OFHC"
            cu_neg.Material="OFHC"
            inga.Material="INGA"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_inga
            size2.ElementSize=Quantity(ElementSize_ns_inga)
            #size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_mirror
            size3.ElementSize=Quantity(ElementSize_ns_mirror)
            #size3.Behavior = SizingBehavior.Hard
            size4.Location = ns_cu
            size4.ElementSize=Quantity(ElementSize_ns_cu)
            #size4.Behavior = SizingBehavior.Hard
        elif (colling_type == "INGA 1"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            inga = get_object_by_name("Inga (Inga)")
            optics_face = get_object_by_name("optics_face")
            inga_conn_mirror = get_object_by_name("inga_conn_mirror")
            mirror_conn_inga = get_object_by_name("mirror_conn_inga")
            inga_conn_ofhcm = get_object_by_name("inga_conn_ofhcm")
            ofhcm_conn_inga = get_object_by_name("ofhcm_conn_inga")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_inga = get_object_by_name("ns_inga")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            inga.Material="INGA"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_inga
            size2.ElementSize=Quantity(ElementSize_ns_inga)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_mirror
            size3.ElementSize=Quantity(ElementSize_ns_mirror)
            size3.Behavior = SizingBehavior.Hard
            size4.Location = ns_cu
            size4.ElementSize=Quantity(ElementSize_ns_cu)
            size4.Behavior = SizingBehavior.Hard
        elif (colling_type == "IN 1"):
            mirror = get_object_by_name("Mirror (Mirror)")
            cu_mid = get_object_by_name("OFHC_MID (OFHC_MID)")
            cu_neg = get_object_by_name("OFHC_NEG (OFHC_NEG)")
            optics_face = get_object_by_name("optics_face")
            cu_conn_mirror_neg = get_object_by_name("cu_conn_mirror_neg")
            cu_conn_mirror_mid = get_object_by_name("cu_conn_mirror_mid")
            mirror_conn_cu_neg = get_object_by_name("mirror_conn_cu_neg")
            mirror_conn_cu_mid = get_object_by_name("mirror_conn_cu_mid")
            ns_mirror = get_object_by_name("ns_mirror")
            ns_cu = get_object_by_name("ns_cu")
            sanre_mid = get_object_by_name("sanre_mid")
            # 定义材料参数
            mirror.Material="SI"
            cu_mid.Material="OFHC"
            cu_neg.Material="OFHC"
            #定义网格精度
            size1.Location = optics_face
            size1.ElementSize=Quantity(ElementSize_optics_face)
            size1.Behavior = SizingBehavior.Hard
            size2.Location = ns_mirror
            size2.ElementSize=Quantity(ElementSize_ns_mirror)
            size2.Behavior = SizingBehavior.Hard
            size3.Location = ns_cu
            size3.ElementSize=Quantity(ElementSize_ns_cu)
            size3.Behavior = SizingBehavior.Hard

        MESH.GenerateMesh()
        CONN = Model.Connections
        for connection in CONN.Children:
            if connection.DataModelObjectCategory == DataModelObjectCategory.ConnectionGroup:
                connection.Delete()
        if (colling_type == "INGA 3"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG3 = CONN.AddContactRegion()
            CONT_REG4 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = inga_conn_mirror
            CONT_REG1.TargetLocation = mirror_conn_inga
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = inga_conn_ofhcn
            CONT_REG2.TargetLocation = ofhcn_conn_inga
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
            CONT_REG3.SourceLocation = inga_conn_ofhcm
            CONT_REG3.TargetLocation = ofhcm_conn_inga
            CONT_REG3.ContactType = ContactType.NoSeparation
            CONT_REG3.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG3.AutomaticThermalConductance = False
            CONT_REG4.SourceLocation = inga_conn_ofhcp
            CONT_REG4.TargetLocation = ofhcp_conn_inga
            CONT_REG4.ContactType = ContactType.NoSeparation
            CONT_REG4.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG4.AutomaticThermalConductance = False
        elif (colling_type == "INGA 1"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = inga_conn_mirror
            CONT_REG1.TargetLocation = mirror_conn_inga
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = inga_conn_ofhcm
            CONT_REG2.TargetLocation = ofhcm_conn_inga
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False
        elif (colling_type == "IN 1"):
            CONT_REG1 = CONN.AddContactRegion()
            CONT_REG2 = CONN.AddContactRegion()
            CONT_REG1.SourceLocation = cu_conn_mirror_neg
            CONT_REG1.TargetLocation = mirror_conn_cu_neg
            CONT_REG1.ContactType = ContactType.NoSeparation
            CONT_REG1.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG1.AutomaticThermalConductance = False
            CONT_REG2.SourceLocation = cu_conn_mirror_mid
            CONT_REG2.TargetLocation = mirror_conn_cu_mid
            CONT_REG2.ContactType = ContactType.NoSeparation
            CONT_REG2.ThermalConductanceValue = Quantity(150000, "W m^-1 m^-1 C^-1")
            CONT_REG2.AutomaticThermalConductance = False

        TEMP_Mirror.Location = ns_mirror
        TEMP_Mirror.ScopingMethod = GeometryDefineByType.Component
        external_data_file.FilePath = h
        imported_heatflux.Location=optics_face
        imported_heatflux.ImportLoad()
        conv_center, conv_side = int(conv_center), int(conv_side)
        temp_center = float("{:.1f}".format(temp_center))
        if (colling_type == "INGA 3"):
            conv1.Location = sanre_mid
            conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
            conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))

            conv2.Location = sanre_neg
            conv2.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_side, "W m^-1 m^-1 C^-1"))
            conv2.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_value, "C"))

            conv3.Location = sanre_pos
            conv3.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_side, "W m^-1 m^-1 C^-1"))
            conv3.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_value, "C"))
        elif (colling_type == "INGA 1"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))
        elif (colling_type == "IN 3"):
                conv1.Location = sanre_mid
                conv1.FilmCoefficient.Output.SetDiscreteValue(0, Quantity(conv_center, "W m^-1 m^-1 C^-1"))
                conv1.AmbientTemperature.Output.SetDiscreteValue(0, Quantity(temp_center, "C"))
                
        STAT_THERM_SOLN.Solve()
        fileExtension=r".txt"
        results = STAT_THERM_SOLN.GetChildren(Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Result,True)
        result = results[0]
        fileName = str(result.Name)
        newFileName = f"{fileName}_Geom{num1:0{geom_num}d}_Heat{num2}_ConvCenter{conv_center}_ConvSide{conv_side}_temp" + "{:.1f}".format(temp_center) + f" {(para[-1]):0{total_digit}d}" # 格式化文件名
        path = os.path.join(cwd_out,newFileName+fileExtension)
        result.ExportToTextFile(path)

        Tree.Activate(TEMP_Mirror)
        Graphics.Camera.SetFit()
        newFileName = newFileName
        Graphics.ExportImage(os.path.join(cwd_out,newFileName+".png"), image_export_format, settings_720p)
        
        Messages = ExtAPI.Application.Messages
        if Messages:
            for message in Messages:
                print(f"[{message.Severity}] {message.DisplayString}")
        else:
            print("No [Info]/[Warning]/[Error] Messages")

        print("Thermal done, Model: " +str(num1)+"#, Heat: "+str(heat_flux_index)+"#, 水温: " + str(temp_center) +"#, 对流换热系数: " + str(conv_center) +" "+str(conv_side))
        STAT_THERM_SOLN.ClearGeneratedData()
        imported_heatflux.ClearGeneratedData()
        
# Close the app
app.close()