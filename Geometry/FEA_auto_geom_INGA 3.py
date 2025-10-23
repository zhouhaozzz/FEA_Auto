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

l_optics = 0.96
b_optics = 0.012
inga_opt = 0.005
l_ingac = 0.76
kuan_ingac = 0.008
shen_ingac = 0.01
xiakuan_ingac = 0.716
r = 0.03
height_inga = 0.008
cu_kuan_b = 0.003
cu_height_long = 0.04
cu_kuan_top = 0.012
cu_height_short = 0.012
cu_kuan_middle = 0.009
cu_D = 0.006
bottom_inga = 0.002
dw_height = 0.007

l = 1
b = 0.07
t = 0.05
OFHC_L_mid = 0.12
OFHC_L_side = 0.07
GAP_CU = 0.05
dw_length = 0.03
kong_height = 0.013
kong_length = 0.025

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

print(l, b, t, OFHC_L_mid, OFHC_L_side, GAP_CU, dw_length, kong_height, kong_length, notch_depth)

## 默认单位m,Radian
# Define the origin point of the plane
origin = Point3D([0, 0, 0])

# Create a plane located in previous point with desired fundamental directions
plane = Plane(
    origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0]
)

sketch = Sketch()
sketch_mirror=(
    sketch.segment(Point2D([l/2,b/2]), Point2D([l/2,-b/2]))
        .segment_to_point(Point2D([-l/2,-b/2]))
        .segment_to_point(Point2D([-l/2,b/2]))
        .segment_to_point(Point2D([l/2,b/2]))
            )

modeler = launch_modeler()
geometry_name = rw.read_geometry()
design_name = (geometry_name + "_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[3] +
               "_" + sys.argv[4] + "_" + sys.argv[5] + "_" + sys.argv[6] + "_" +
               sys.argv[7] + "_" + sys.argv[8] + "_" + sys.argv[9] + "_" +
               sys.argv[10])
design = modeler.create_design(design_name)

mirror_part = design.add_component("Mirror")
# Extrude the sketch to create the body
body_mirror = mirror_part.extrude_sketch("Mirror",sketch_mirror, -t * UNITS.m)

## 铟镓槽处的基准平面
origin = Point3D([0, 0, -inga_opt])
plane1 = Plane(
    origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0]
)
sketch = Sketch(plane1)

## 计算圆心
def find_circle_center(x1, y1, x2, y2, r):
        # 如果 x1 == x2，直接返回 x2, y2
    if x1 == x2:
        return x2, y2
    # 计算两点之间的距离的平方
    dist_sq = (x2 - x1)**2 + (y2 - y1)**2
    
    # 圆心的坐标 (x_c, y_c) 的计算
    # 计算半径平方和距离的差
    d = r**2 - dist_sq / 4
    
    if d < 0:
        raise ValueError("The radius is too small for the given points.")
    
    # 中点坐标 (xm, ym)
    xm = (x1 + x2) / 2
    ym = (y1 + y2) / 2
    
    # 计算圆心坐标
    dx = (y2 - y1) * math.sqrt(d) / dist_sq**0.5
    dy = (x2 - x1) * math.sqrt(d) / dist_sq**0.5
    
    # 计算圆心1（位于垂直平分线正方向）
    xc, yc = xm + dx, ym - dy
    
    return xc, yc
### 
x1, y1, x2, y2, x3, y3, x4, y4 = (
    l_ingac / 2, b / 2, 
    xiakuan_ingac / 2, b / 2 - shen_ingac, 
    -xiakuan_ingac / 2, b / 2 - shen_ingac, 
    -l_ingac / 2, b / 2
)

center1 = find_circle_center(x1, y1, x2, y2, r)
xc,yc = center1[0] , center1[1]

if x1 == x2:
    # 如果 x1 == x2，执行以下代码
    sketch_ingac = (
        sketch.segment(Point2D([x4, y4]), Point2D([x1, y1]))
        .segment_to_point(Point2D([x2, y2]))
        .segment_to_point(Point2D([x3, y3]))
        .segment_to_point(Point2D([x4, y4]))
    )
else:
    # 否则执行原始代码
    sketch_ingac = (
        sketch.segment(Point2D([x4, y4]), Point2D([x1, y1]))
        .arc_to_point(Point2D([x2, y2]), Point2D([xc, yc]), True)
        .segment_to_point(Point2D([x3, y3]))
        .arc_to_point(Point2D([x4, y4]), Point2D([-xc, yc]), True)
    )

# # Extrude the sketch to create the body
body_ingac = design.extrude_sketch("ingac", sketch_ingac, -kuan_ingac * UNITS.m)
mirrored_body_ingac = body_ingac.copy(body_ingac.parent_component,"mirrored_body")
mirrored_body_ingac.mirror(Plane(direction_x=[1,0,0],direction_y=[0,0,1]))
body_mirror.subtract(body_ingac)
body_mirror.subtract(mirrored_body_ingac)

sketch = Sketch(plane1)
sketch_cut =(
    sketch.segment(Point2D([x4-0.2, y4+0.2]), Point2D([x1+0.2, y1+0.2]))
    .segment_to_point(Point2D([x2+0.2, y2+height_inga]))
    .segment_to_point(Point2D([x3-0.2, y3+height_inga]))
    .segment_to_point(Point2D([x4-0.2, y4+0.2]))
)


inga_part = design.add_component("Inga")
body_inga = inga_part.extrude_sketch("Inga", sketch_ingac, -kuan_ingac * UNITS.m)
body_inga_cut = design.extrude_sketch("ingacut", sketch_cut, -kuan_ingac * UNITS.m)
body_inga.subtract(body_inga_cut)

yy, zz= b/2-shen_ingac+bottom_inga,-(inga_opt+kuan_ingac/2)
origin2 = Point3D([OFHC_L_mid/2, yy,zz ])
plane2 = Plane(
    origin2, direction_x=[0, 0, 1], direction_y=[0, 1, 0]
)
sketch = Sketch(plane2)

OFHC_m_sketch = (
        sketch.segment(Point2D([0,0]), Point2D([cu_kuan_b/2,0]))
        .segment_to_point(Point2D([cu_kuan_b/2,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top, cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,0]))
        .segment_to_point(Point2D([0,0]))
        .circle(center=Point2D([(cu_kuan_b-cu_kuan_top)/2, cu_height_long-cu_height_short/2 ]), radius=cu_D/2)
    )

# # Extrude the sketch to create the body
OFHCM_part = design.add_component("OFHC_MID")
body_cu_middle = OFHCM_part.extrude_sketch("OFHC_MID", OFHC_m_sketch, OFHC_L_mid * UNITS.m)

origin2 = Point3D([GAP_CU+OFHC_L_mid/2, yy,zz ])
plane2 = Plane(
    origin2, direction_x=[0, 0, 1], direction_y=[0, 1, 0]
)
sketch = Sketch(plane2)

OFHC_pos_sketch = (
        sketch.segment(Point2D([0,0]), Point2D([cu_kuan_b/2,0]))
        .segment_to_point(Point2D([cu_kuan_b/2,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top, cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,0]))
        .segment_to_point(Point2D([0,0]))
        .circle(center=Point2D([(cu_kuan_b-cu_kuan_top)/2, cu_height_long-cu_height_short/2 ]), radius=cu_D/2)
    )

# # Extrude the sketch to create the body
OFHCP_part = design.add_component("OFHC_POS")
body_cu_pos = OFHCP_part.extrude_sketch("OFHC_POS", OFHC_pos_sketch, OFHC_L_side * UNITS.m,"-")

origin3 = Point3D([-(GAP_CU+OFHC_L_mid/2), yy,zz ])
plane3 = Plane(
    origin3, direction_x=[0, 0, 1], direction_y=[0, 1, 0]
)
sketch = Sketch(plane3)

OFHC_neg_sketch = (
        sketch.segment(Point2D([0,0]), Point2D([cu_kuan_b/2,0]))
        .segment_to_point(Point2D([cu_kuan_b/2,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top, cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,0]))
        .segment_to_point(Point2D([0,0]))
        .circle(center=Point2D([(cu_kuan_b-cu_kuan_top)/2, cu_height_long-cu_height_short/2 ]), radius=cu_D/2)
    )

# # Extrude the sketch to create the body
OFHCN_part = design.add_component("OFHC_NEG")
body_cu_neg = OFHCN_part.extrude_sketch("OFHC_NEG", OFHC_neg_sketch, OFHC_L_side * UNITS.m)

body_inga.subtract(body_cu_neg)
body_inga.subtract(body_cu_middle)
body_inga.subtract(body_cu_pos)

body_cu_middle = OFHCM_part.extrude_sketch("OFHC_MID", OFHC_m_sketch, OFHC_L_mid * UNITS.m)
body_cu_pos = OFHCP_part.extrude_sketch("OFHC_POS", OFHC_pos_sketch, OFHC_L_side * UNITS.m,"-")
body_cu_neg = OFHCN_part.extrude_sketch("OFHC_NGE", OFHC_neg_sketch, OFHC_L_side * UNITS.m)

sketch = Sketch(plane)
sketch_opt=(
    sketch.segment(Point2D([l_optics/2,b_optics/2]), Point2D([l_optics/2,-b_optics/2]))
        .segment_to_point(Point2D([-l_optics/2,-b_optics/2]))
        .segment_to_point(Point2D([-l_optics/2,b_optics/2]))
        .segment_to_point(Point2D([l_optics/2,b_optics/2]))
            )

imprint_face = body_mirror.imprint_projected_curves(direction=UNITVECTOR3D_Z,sketch=sketch_opt, closest_face=True)

def create_conn_named_selection(faces_mine, indices, selection_name):
    """
    创建一个命名选择，名称为 selection_name, 包含 faces_mine 列表中指定的索引位置的所有面。
    支持单个数字、多个不连续的数字、以及连续的数字范围。

    参数:
    - faces_mine: 包含所有面的列表。
    - indices: 单个数字、一个列表、一个连续的数字范围，或者一个包含多个数字的列表。
    - selection_name: 创建的命名选择的名称，默认为 "inga_conn_mirror"。
    """
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

faces_mirror =body_mirror.faces
faces_cu_mid =body_cu_middle.faces
faces_cu_pos =body_cu_pos.faces
faces_cu_neg =body_cu_neg.faces
faces_inga =body_inga.faces

create_conn_named_selection(faces_cu_neg,8, "sanre_neg")
create_conn_named_selection(faces_cu_mid,8, "sanre_mid")
create_conn_named_selection(faces_cu_pos,8, "sanre_pos")

create_conn_named_selection(faces_mirror,"5-9", "mirror_conn_inga")
create_conn_named_selection(faces_mirror,15, "optics_face")

create_conn_named_selection(faces_inga,"0-4", "inga_conn_mirror")
create_conn_named_selection(faces_inga,"6-10", "inga_conn_ofhcn")
create_conn_named_selection(faces_inga,"11-15", "inga_conn_ofhcm")
create_conn_named_selection(faces_inga,"16-20", "inga_conn_ofhcp")

create_conn_named_selection(faces_cu_neg,[0,1,5,6,7], "ofhcn_conn_inga")
create_conn_named_selection(faces_cu_mid,[0,1,5,6,7], "ofhcm_conn_inga")
create_conn_named_selection(faces_cu_pos,[0,1,5,6,7], "ofhcp_conn_inga")

# 加入体的NamedSelection
design.create_named_selection("ns_mirror", bodies=[body_mirror])
design.create_named_selection("ns_inga", bodies=[body_inga])
design.create_named_selection("ns_cu", bodies=[body_cu_middle,body_cu_pos,body_cu_neg])


## 铜管打孔
origin4 = Point3D([-(GAP_CU+OFHC_L_mid/2), yy,0 ])
plane4 = Plane(
    origin4, direction_x=[1, 0, 0], direction_y=[0, 1, 0]
)

sketch = Sketch(plane4)
OFHC_neg_kong_sketch = (
        sketch.segment(Point2D([-dw_length,dw_height]), Point2D([-dw_length, dw_height+kong_height]))
        .segment_to_point(Point2D([-dw_length-kong_length,dw_height+kong_height]))
        .segment_to_point(Point2D([-dw_length-kong_length,dw_height]))
        .segment_to_point(Point2D([-dw_length,dw_height]))
    )

## 铜管打孔
origin5 = Point3D([(GAP_CU+OFHC_L_mid/2), yy,0 ])
plane5 = Plane(
    origin5, direction_x=[1, 0, 0], direction_y=[0, 1, 0]
)

sketch = Sketch(plane5)
OFHC_pos_kong_sketch = (
        sketch.segment(Point2D([dw_length,dw_height]), Point2D([dw_length, dw_height+kong_height]))
        .segment_to_point(Point2D([dw_length+kong_length,dw_height+kong_height]))
        .segment_to_point(Point2D([dw_length+kong_length,dw_height]))
        .segment_to_point(Point2D([dw_length,dw_height]))
    )

# # Extrude the sketch to create the body
body_kong_neg = OFHCN_part.extrude_sketch("KONG_NEG", OFHC_neg_kong_sketch, -0.2 * UNITS.m)
body_kong_pos = OFHCP_part.extrude_sketch("KONG_POS", OFHC_pos_kong_sketch, -0.2 * UNITS.m)

body_cu_neg.subtract(body_kong_neg)
body_cu_pos.subtract(body_kong_pos)

# 构建目标保存路径
cwd = os.path.dirname(os.getcwd())
save_path = os.path.join(cwd, "Files", "Model")
file_location = design.export_to_pmdb(save_path)

#time.sleep(1000)

modeler.close()


end_time = time.time()
elapsed_time = end_time - start_time
print(f"建模完成，总用时: {elapsed_time:.4f} 秒")