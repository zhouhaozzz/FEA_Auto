from pint import Quantity
from ansys.geometry.core import launch_modeler
from ansys.geometry.core import Modeler
from ansys.geometry.core.misc import UNITS, Distance
from ansys.geometry.core.sketch import Sketch
from ansys.geometry.core.designer.design import Design
import math
from pathlib import Path
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.math import (
    UNITVECTOR3D_Z,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    Vector3D,
    Plane,
    Point2D,
    Point3D
)
import time
import sys
import os
import read_write as rw #一些辅助函数
start_time = time.time()

cwd = os.path.dirname(os.getcwd())

l = 0.6
b = 0.05
t = 0.05
l_optics = 0.6
b_optics = 0.042
cu_kuan = 0.008
cu_height = 0.008
cu_optics = 0.002
cu_D = 0.006
cao_optics = 0.031 
cao_kuan = 0.007
cao_height = 0.007
OFHC_L_mid = 0.5 #铜管长度

l = float(sys.argv[1])
b = float(sys.argv[2])
t = float(sys.argv[3])
OFHC_L_mid = float(sys.argv[4])
OFHC_L_side = float(sys.argv[5])
GAP_CU = float(sys.argv[6])
dw_length = float(sys.argv[7])
kong_height = float(sys.argv[8])
kong_length = float(sys.argv[9])
notch_depth = float(sys.argv[10])
l_optics = float(sys.argv[11])
b_optics = float(sys.argv[12])
kaicao = sys.argv[13]
cao_optics = float(sys.argv[14])
cao_kuan = float(sys.argv[15])
cao_height = float(sys.argv[16])
print(l, b, t, OFHC_L_mid, OFHC_L_side, GAP_CU, dw_length, kong_height, kong_length, notch_depth, kaicao, cao_optics, cao_kuan, cao_height)

origin = Point3D([0, 0, 0])

plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
sketch = Sketch()
sketch_mirror=(
    sketch.segment(Point2D([l/2,b/2]), Point2D([l/2,-b/2]))
        .segment_to_point(Point2D([-l/2,-b/2]))
        .segment_to_point(Point2D([-l/2,b/2]))
        .segment_to_point(Point2D([l/2,b/2]))
            )
modeler = launch_modeler()

#design = modeler.create_design(rw.read_geometry() + "_" + sys.argv[4])  # 文件名后缀使用 OFHC_L_mid*1000
geometry_name = rw.read_geometry()
design_name = (geometry_name + "_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[3] +
               "_" + sys.argv[4] + "_" + sys.argv[5] + "_" + sys.argv[6] + "_" +
               sys.argv[7] + "_" + sys.argv[8] + "_" + sys.argv[9] + "_" +
               sys.argv[10] + "_" +
               sys.argv[13] + "_" + sys.argv[14] + "_" + sys.argv[15] + "_" + sys.argv[16])
design = modeler.create_design(design_name)

mirror_part = design.add_component("Mirror")
# Extrude the sketch to create the body
body_mirror = mirror_part.extrude_sketch("Mirror",sketch_mirror, -t * UNITS.m)

yy, zz = b/2, -cu_optics
origin1 = Point3D([OFHC_L_mid/2, yy, zz])
plane1 = Plane(origin1, direction_x=[0, 0, 1], direction_y=[0, 1, 0])
sketch = Sketch(plane1)
OFHC_n_sketch = (
        sketch.segment(Point2D([0,0]), Point2D([0,cu_kuan]))
        .segment_to_point(Point2D([-cu_kuan,cu_kuan]))
        .segment_to_point(Point2D([-cu_kuan,0]))
        .segment_to_point(Point2D([0,0]))
        .circle(center=Point2D([-cu_kuan/2, cu_kuan/2 ]), radius=cu_D/2)
    )
OFHCn_part = design.add_component("OFHC_NEG")
body_cu_neg = OFHCn_part.extrude_sketch("OFHC_NEG", OFHC_n_sketch, OFHC_L_mid * UNITS.m)

yy1 = -b/2-cu_kuan
origin1 = Point3D([OFHC_L_mid/2, yy1, zz])
plane1 = Plane(origin1, direction_x=[0, 0, 1], direction_y=[0, 1, 0])
sketch = Sketch(plane1)
OFHC_m_sketch = (
        sketch.segment(Point2D([0,0]), Point2D([0,cu_kuan]))
        .segment_to_point(Point2D([-cu_kuan,cu_kuan]))
        .segment_to_point(Point2D([-cu_kuan,0]))
        .segment_to_point(Point2D([0,0]))
        .circle(center=Point2D([-cu_kuan/2, cu_kuan/2 ]), radius=cu_D/2)
    )
OFHCm_part = design.add_component("OFHC_MID")
body_cu_middle = OFHCm_part.extrude_sketch("OFHC_MID", OFHC_m_sketch, OFHC_L_mid * UNITS.m)

sketch = Sketch(plane)
sketch_opt=(
    sketch.segment(Point2D([l_optics/2,b_optics/2]), Point2D([l_optics/2,-b_optics/2]))
        .segment_to_point(Point2D([-l_optics/2,-b_optics/2]))
        .segment_to_point(Point2D([-l_optics/2,b_optics/2]))
        .segment_to_point(Point2D([l_optics/2,b_optics/2]))
            )

imprint_face = body_mirror.imprint_projected_curves(direction=UNITVECTOR3D_Z,sketch=sketch_opt, closest_face=True)

faces_mirror = body_mirror.faces
faces_cu_neg = body_cu_neg.faces
faces_cu_mid = body_cu_middle.faces

def create_conn_named_selection(faces_mine, indices, selection_name):
        # 定义一个空列表，用来收集 faces_mine 中指定的面
        faces_to_include = []

        # 如果 indices 是单个数字
        if isinstance(indices, int):
            indices = [indices]  # 将单个数字转为列表

        # 如果 indices 是一个范围（例如 '3-5' 格式）
        elif isinstance(indices, str) and '-' in indices:
            start, end = map(int, indices.split('-'))
            indices = list(range(start, end + 1))  # 转换为连续的数字范围

        # 如果 indices 是一个列表或集合，直接处理
        if isinstance(indices, (list, set)):
            for idx in indices:
                if 0 <= idx < len(faces_mine):  # 检查索引是否在有效范围内
                    faces_to_include.append(faces_mine[idx])
        else:
            raise ValueError("Invalid indices format. Must be an integer, a list, or a range string.")

        # 创建命名选择
        design.create_named_selection(selection_name, faces=faces_to_include)


##不开夹持槽的时候命名如下！！！
create_conn_named_selection(faces_mirror,6, "optics_face")
create_conn_named_selection(faces_cu_neg, 6, "sanre_mid")
create_conn_named_selection(faces_cu_mid, 6, "sanre_mid")
create_conn_named_selection(faces_cu_neg, 0, "cu_conn_mirror_neg")
create_conn_named_selection(faces_cu_mid, 2, "cu_conn_mirror_mid")
create_conn_named_selection(faces_mirror, 3, "mirror_conn_cu_neg")
create_conn_named_selection(faces_mirror, 1, "mirror_conn_cu_mid")

# 加入体的NamedSelection
design.create_named_selection("ns_mirror", bodies=[body_mirror])
design.create_named_selection("ns_cu", bodies=[body_cu_middle,body_cu_neg])

if (kaicao == "yes"):
    origin = Point3D([l/2, 0, 0])
    plane = Plane(origin, direction_x=Vector3D([0,0,1]), direction_y=Vector3D([0,1,0]))
    sketch = Sketch(plane)
    sketch_cao = (
        sketch.segment(Point2D([-cao_optics,-b/2]), Point2D([-cao_optics,-b/2+cao_kuan]))
        .segment_to_point(Point2D([-cao_optics-cao_height,-b/2+cao_kuan]))
        .segment_to_point(Point2D([-cao_optics-cao_height,-b/2]))
        .segment_to_point(Point2D([-cao_optics,-b/2]))
    )
    body_cao = design.extrude_sketch("cao", sketch_cao, l * UNITS.m)
    mirrored_body_cao = body_cao.copy(body_cao.parent_component,"cao2")
    mirrored_body_cao.mirror(Plane(direction_x=[1,0,0],direction_y=[0,0,1]))
    body_mirror.subtract(body_cao)
    body_mirror.subtract(mirrored_body_cao)

# 构建目标保存路径
cwd = os.path.dirname(os.getcwd())
save_path = os.path.join(cwd, "Files", "Model")
file_location = design.export_to_pmdb(save_path)

#time.sleep(1000)

modeler.close()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"建模完成，总用时: {elapsed_time:.4f} 秒")