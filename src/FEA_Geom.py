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
    Plane,
    Point2D,
    Point3D
)
import time
from geometry import GeometryParameters
import sys
import os
import read_write as rw #一些辅助函数

start_time = time.time()
geom_params = GeometryParameters()
# 初始定义量，单位（米）
l = geom_params.l
b = geom_params.b
t = geom_params.t
l_optics = geom_params.l_optics
b_optics = geom_params.b_optics
inga_opt = geom_params.inga_opt
l_ingac = geom_params.l_ingac
kuan_ingac = geom_params.kuan_ingac
shen_ingac = geom_params.shen_ingac
xiakuan_ingac = geom_params.xiakuan_ingac
r = geom_params.r
height_inga = geom_params.height_inga
cu_kuan_b = geom_params.cu_kuan_b
cu_height_long = geom_params.cu_height_long
cu_kuan_top = geom_params.cu_kuan_top
cu_height_short = geom_params.cu_height_short
cu_kuan_middle = geom_params.cu_kuan_middle
cu_D = geom_params.cu_D
OFHC_L_mid = geom_params.OFHC_L_mid
OFHC_L_side = geom_params.OFHC_L_side
GAP_CU = geom_params.GAP_CU
bottom_inga = geom_params.bottom_inga
dw_height = geom_params.dw_height
dw_length = geom_params.dw_length
kong_height = geom_params.kong_height
kong_length = geom_params.kong_length
notch_depth = geom_params.notch_depth

gemo_check, thermal_check = rw.cal_geometry()
if gemo_check == 1:
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
    print(l, b, t, OFHC_L_mid, OFHC_L_side, GAP_CU, dw_length, kong_height, kong_length, notch_depth)

#sys.exit()
## 默认单位m,Radian
# Define the origin point of the plane
origin = Point3D([0, 0, 0])

# Create a plane located in previous point with desired fundamental directions
plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
sketch = Sketch()
sketch_mirror=(
    sketch.segment(Point2D([l/2,b/2]), Point2D([l/2,-b/2]))
        .segment_to_point(Point2D([-l/2,-b/2]))
        .segment_to_point(Point2D([-l/2,b/2]))
        .segment_to_point(Point2D([l/2,b/2]))
            )
modeler = launch_modeler()

geometry_name = rw.read_geometry()
design = modeler.create_design(geometry_name + "_" + sys.argv[1] + "_" + sys.argv[2] + "_" + sys.argv[3] + "_" + sys.argv[4] + "_" + sys.argv[5] + "_" + sys.argv[6] + "_" + sys.argv[7] + "_" + sys.argv[8] + "_" + sys.argv[9] + "_" + sys.argv[10])
mirror_part = design.add_component("Mirror")
# Extrude the sketch to create the body
body_mirror = mirror_part.extrude_sketch("Mirror",sketch_mirror, -t * UNITS.m)


##########################################################InGa
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
##########################################################  InGa


##########################################################  铜管
In_length = l
In_width = 0.008
#In_height = 0.001

yy, zz= b/2-shen_ingac+bottom_inga,-(inga_opt+kuan_ingac/2)
#######OFHC_MID#######
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

OFHCM_part = design.add_component("OFHC_MID")
body_cu_middle = OFHCM_part.extrude_sketch("OFHC_MID", OFHC_m_sketch, OFHC_L_mid * UNITS.m)

#######OFHC_POS#######
origin3 = Point3D([GAP_CU+OFHC_L_mid/2, yy,zz ])
plane2 = Plane(
    origin3, direction_x=[0, 0, 1], direction_y=[0, 1, 0]
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

OFHCP_part = design.add_component("OFHC_POS")
body_cu_pos = OFHCP_part.extrude_sketch("OFHC_POS", OFHC_pos_sketch, OFHC_L_side * UNITS.m,"-")

#######OFHC_NEG#######
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

OFHCN_part = design.add_component("OFHC_NEG")
body_cu_neg = OFHCN_part.extrude_sketch("OFHC_NEG", OFHC_neg_sketch, OFHC_L_side * UNITS.m)

body_inga.subtract(body_cu_neg)
body_inga.subtract(body_cu_middle)
body_inga.subtract(body_cu_pos)
body_cu_middle = OFHCM_part.extrude_sketch("OFHC_MID", OFHC_m_sketch, OFHC_L_mid * UNITS.m)
body_cu_pos = OFHCP_part.extrude_sketch("OFHC_POS", OFHC_pos_sketch, OFHC_L_side * UNITS.m,"-")
body_cu_neg = OFHCN_part.extrude_sketch("OFHC_NGE", OFHC_neg_sketch, OFHC_L_side * UNITS.m)

##########################################################  铜管

########################################################## 负载区域
l_optics = 0.7
b_optics = 0.03

sketch = Sketch(plane)
sketch_opt=(
    sketch.segment(Point2D([l_optics/2,b_optics/2]), Point2D([l_optics/2,-b_optics/2]))
        .segment_to_point(Point2D([-l_optics/2,-b_optics/2]))
        .segment_to_point(Point2D([-l_optics/2,b_optics/2]))
        .segment_to_point(Point2D([l_optics/2,b_optics/2]))
            )
imprint_face = body_mirror.imprint_projected_curves(direction=UNITVECTOR3D_Z,sketch=sketch_opt, closest_face=True)

###############################################################


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
faces_inga =body_inga.faces
faces_cu_mid =body_cu_middle.faces
faces_cu_pos =body_cu_pos.faces
faces_cu_neg =body_cu_neg.faces

create_conn_named_selection(faces_mirror, 15, "optics_face")
create_conn_named_selection(faces_mirror,"5-9", "mirror_conn_inga")
create_conn_named_selection(faces_inga,"0-4", "inga_conn_mirror")    
create_conn_named_selection(faces_inga,"6-10", "inga_conn_ofhcn")
create_conn_named_selection(faces_inga,"11-15", "inga_conn_ofhcm")
create_conn_named_selection(faces_inga,"16-20", "inga_conn_ofhcp")

create_conn_named_selection(faces_cu_neg,[0,1,5,6,7], "ofhcn_conn_inga")
create_conn_named_selection(faces_cu_mid,[0,1,5,6,7], "ofhcm_conn_inga")
create_conn_named_selection(faces_cu_pos,[0,1,5,6,7], "ofhcp_conn_inga")

create_conn_named_selection(faces_cu_neg,8, "sanre_neg")
create_conn_named_selection(faces_cu_mid,8, "sanre_mid")
create_conn_named_selection(faces_cu_pos,8, "sanre_pos")

# 加入体的NamedSelection
design.create_named_selection("ns_mirror", bodies=[body_mirror])
design.create_named_selection("ns_inga", bodies=[body_inga])
design.create_named_selection("ns_cu", bodies=[body_cu_middle,body_cu_pos,body_cu_neg])

########################################################## 镜子开槽
l1 = 0.01 #长界面深度
t1 = 0.014 #顶端距离开槽
t2 = 0.006 #开槽高度
b1 = notch_depth # 长轴方向开槽深度
#b1 = 0.008 #短截面深度

origin6 = Point3D([-l/2,0,0])
plane6 = Plane(
    origin6, direction_x=[0, 1, 0], direction_y=[0, 0, 1]
)

sketch = Sketch(plane6)
mirror_cut1 = (
        sketch.segment(Point2D([b/2-b1,-t1]), Point2D([b/2,-t1]))
        .segment_to_point(Point2D([b/2,-(t1+t2)]))
        .segment_to_point(Point2D([b/2-b1,-(t1+t2)]))
        .segment_to_point(Point2D([b/2-b1,-t1]))
    )

## 镜子开槽
origin7 = Point3D([-l/2,0,0])
plane7 = Plane(
    origin7, direction_x=[0, 1, 0], direction_y=[0, 0, 1]
)

sketch = Sketch(plane7)
mirror_cut2 = (
        sketch.segment(Point2D([-b/2,-t1]), Point2D([-b/2+b1,-t1]))
        .segment_to_point(Point2D([-b/2+b1,-(t1+t2)]))
        .segment_to_point(Point2D([-b/2,-(t1+t2)]))
        .segment_to_point(Point2D([-b/2,-t1]))
    )


## 镜子开槽
origin8 = Point3D([0,b/2,0])
plane8 = Plane(
    origin8, direction_x=[1, 0, 0], direction_y=[0, 0, 1]
)

sketch = Sketch(plane8)
mirror_cut3 = (
        sketch.segment(Point2D([l/2,-t1]), Point2D([l/2,-(t1+t2)]))
        .segment_to_point(Point2D([l/2-l1,-(t1+t2)]))
        .segment_to_point(Point2D([l/2-l1,-t1]))
        .segment_to_point(Point2D([l/2,-t1]))
    )

## 镜子开槽
origin9 = Point3D([0,b/2,0])
plane9 = Plane(
    origin9, direction_x=[1, 0, 0], direction_y=[0, 0, 1]
)

sketch = Sketch(plane9)
mirror_cut4 = (
        sketch.segment(Point2D([-l/2,-t1]), Point2D([-l/2+l1,-t1]))
        .segment_to_point(Point2D([-l/2+l1,-(t1+t2)]))
        .segment_to_point(Point2D([-l/2,-(t1+t2)]))
        .segment_to_point(Point2D([-l/2,-t1]))
    )


# # Extrude the sketch to create the body
body_kong_mirror1 = mirror_part.extrude_sketch("KONG_mirror1", mirror_cut1, l * UNITS.m)
body_kong_mirror2 = mirror_part.extrude_sketch("KONG_mirror2", mirror_cut2, l * UNITS.m)
body_kong_mirror3 = mirror_part.extrude_sketch("KONG_mirror3", mirror_cut3, (b) * UNITS.m)
body_kong_mirror4 = mirror_part.extrude_sketch("KONG_mirror4", mirror_cut4, (b) * UNITS.m)

body_mirror.subtract(body_kong_mirror1)
body_mirror.subtract(body_kong_mirror2)
body_mirror.subtract(body_kong_mirror3)
body_mirror.subtract(body_kong_mirror4)
########################################################## 镜子开槽


########################################################## 铜管截断
yy, zz= b/2-shen_ingac+bottom_inga,-(inga_opt+kuan_ingac/2)

origin10 = Point3D([GAP_CU+OFHC_L_mid/2, yy,zz ])
plane10 = Plane(
    origin10, direction_x=[0, 0, 1], direction_y=[0, 1, 0]
)
sketch = Sketch(plane10)
OFHC_pos_sketch_cut = (
        sketch.segment(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]), Point2D([-cu_kuan_b/2,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]))
    )

origin11 = Point3D([-(GAP_CU+OFHC_L_mid/2), yy,zz ])
plane11 = Plane(
    origin11, direction_x=[0, 0, 1], direction_y=[0, 1, 0]
)
sketch = Sketch(plane11)
OFHC_neg_sketch_cut = (
        sketch.segment(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]), Point2D([-cu_kuan_b/2,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long]))
        .segment_to_point(Point2D([cu_kuan_b/2-cu_kuan_top,cu_height_long-cu_height_short]))
        .segment_to_point(Point2D([-cu_kuan_b/2,cu_height_long-cu_height_short]))
    )


# # Extrude the sketch to create the body
body_cu_cut1 = mirror_part.extrude_sketch("KONG_cu1", OFHC_pos_sketch_cut, 0.025 * UNITS.m,"-")
body_cu_cut2 = mirror_part.extrude_sketch("KONG_cu2", OFHC_neg_sketch_cut, 0.025 * UNITS.m)

body_cu_pos.subtract(body_cu_cut1)
body_cu_neg.subtract(body_cu_cut2)
########################################################## 铜管截断



# 构建目标保存路径
cwd = os.path.dirname(os.getcwd())
save_path = os.path.join(cwd, "Files", "Model")
file_location = design.export_to_pmdb(save_path)

#time.sleep(1000)

modeler.close()


end_time = time.time()
elapsed_time = end_time - start_time
print(f"建模完成，总用时: {elapsed_time:.4f} 秒")