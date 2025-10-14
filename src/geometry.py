class GeometryParameters:
    def __init__(self):
        # 反射镜相关参数
        self.l = 0.85  # 反射镜长度
        self.b = 0.05  # 反射镜宽度
        self.t = 0.025  # 反射镜厚度

        # 光学区域相关参数
        self.l_optics = 0.5  # 光学长度
        self.b_optics = 0.03 # 光学宽度

        # 铟镓开槽相关参数
        self.inga_opt = 0.003  # 铟镓槽到光学面距离
        self.l_ingac = 0.55  # 铟镓开槽上边长度
        self.kuan_ingac = 0.008  # 铟镓开槽宽度
        self.shen_ingac = 0.01  # 铟镓开槽深度
        self.xiakuan_ingac = 0.5  # 铟镓开槽下层长度
        self.r = 0.03  # 铟镓开槽半径
        self.height_inga = 0.008  # 铟镓的液面高度

        # 铜管截面相关参数(正常不变)
        self.cu_kuan_b = 0.003  # 铜底部宽度
        self.cu_height_long = 0.04  # 铜高度
        self.cu_kuan_top = 0.012  # 铜顶部宽度
        self.cu_height_short = 0.012  # 铜短边高度
        self.cu_kuan_middle = 0.009  # 铜中间宽度
        self.cu_D = 0.006  # 水管直径

        # OFHC铜参数
        self.OFHC_L_mid = 0.12  # OFHC铜中部长度 (变)
        self.OFHC_L_side = 0.17  # OFHC铜两侧长度 (变)
        self.GAP_CU = 0.005  # 铜与铜之间的间隙 (变)
        self.bottom_inga = 0.002  # 铟镓液底部预留的厚度
        self.OFHC_L_side_1 = 0.005 #铜中间长度
        self.OFHC_L_Length = 0.25 #两侧铜中心距离

        # 铜管开孔相关参数
        self.dw_height = 0.007  # 定位高度
        self.dw_length = 0.03  # 定位长度 (变)
        self.kong_height = 0.013  # 孔的高度 (变)
        self.kong_length = 0.025  # 孔的长度 (变)
        
        self.notch_depth = 0.008 #notch 深度

    def as_dict(self):
        """将类的属性转换为字典"""
        return {
            "l": self.l,
            "b": self.b,
            "t": self.t,
            "l_optics": self.l_optics,
            "b_optics": self.b_optics,
            "inga_opt": self.inga_opt,
            "l_ingac": self.l_ingac,
            "kuan_ingac": self.kuan_ingac,
            "shen_ingac": self.shen_ingac,
            "xiakuan_ingac": self.xiakuan_ingac,
            "r": self.r,
            "height_inga": self.height_inga,
            "cu_kuan_b": self.cu_kuan_b,
            "cu_height_long": self.cu_height_long,
            "cu_kuan_top": self.cu_kuan_top,
            "cu_height_short": self.cu_height_short,
            "cu_kuan_middle": self.cu_kuan_middle,
            "cu_D": self.cu_D,
            "OFHC_L_mid": self.OFHC_L_mid,
            "OFHC_L_side": self.OFHC_L_side,
            "GAP_CU": self.GAP_CU,
            "bottom_inga": self.bottom_inga,
            "dw_height": self.dw_height,
            "dw_length": self.dw_length,
            "kong_height": self.kong_height,
            "kong_length": self.kong_length
        }
    
    def extract_values(self):
        # 使用 __dict__ 提取所有实例属性
        return list(self.__dict__.values())
    

class Convention:
    def __init__(self):
        # 铜管散热参数
        self.conv_value = 5000
        self.temp_value = 22
        self.temp_valuem_start = 22
        self.temp_valuem_end = 22
        self.temp_valuem_step = 0.1

    def as_dict(self):
        """将类的属性转换为字典"""
        return {
            "conv_value": self.conv_value,
#             "conv_center": self.conv_center,
#             "conv_side": self.conv_side,
            "temp_value": self.temp_value,
            "temp_valuem_start": self.temp_valuem_start,
            "temp_valuem_end": self.temp_valuem_end,
            "temp_valuem_step": self.temp_valuem_step,
        }
    
    def extract_values(self):
        # 使用 __dict__ 提取所有实例属性
        return list(self.__dict__.values())
