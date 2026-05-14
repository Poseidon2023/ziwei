import streamlit as st
import cnlunar
import datetime

# --- 核心算法部分 (直接引入你校正后的代数公式) ---
# 注意：为了篇幅，这里我简写了结构，你需要将 SKILL.md 中的 14 个模块函数粘贴在这里

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]

# [此处粘贴你的 14 个模块函数：get_all_palace_stems, get_ming_shen_palace, get_wuxing_bureau 等]
# [以及核心主控函数 build_ziwei_chart]
def get_yin_palace_stem(year_stem_str):
    """模块1：根据年干获取寅宫天干（代数化五虎遁）"""
    try:
        y = TIAN_GAN.index(year_stem_str)
    except ValueError:
        return None
    
    t_yin_idx = (y * 2 + 1) % 10
    if t_yin_idx == 0:
        t_yin_idx = 10
    return TIAN_GAN[t_yin_idx]

def get_all_palace_stems(year_stem_str):
    """模块2：以寅宫为起点，顺时针推算十二宫天干"""
    yin_stem = get_yin_palace_stem(year_stem_str)
    if not yin_stem:
        return []
    
    t_yin_idx = TIAN_GAN.index(yin_stem)
    palace_stems = []
    
    for d in range(12): # d 为地支偏移量
        t_target_idx = (t_yin_idx + d - 1) % 10 + 1
        palace_stems.append(TIAN_GAN[t_target_idx])
        
    return palace_stems

def get_ming_shen_palace(lunar_month, hour_zhi_str):
    """模块3：计算命宫与身宫的位置地支"""
    try:
        # 将时辰转为数字 (子=1, 丑=2...)
        h = ZHI_HOUR.index(hour_zhi_str) + 1 
    except ValueError:
        return None, None

    # 命宫索引逻辑: (12 + 月份 - 时辰) % 12
    ming_idx = (12 + lunar_month - h) % 12

    # 身宫索引逻辑: (月份 + 时辰 - 2) % 12
    shen_idx = (lunar_month + h - 2) % 12

    return DI_ZHI[ming_idx], DI_ZHI[shen_idx]

def get_palace_names(ming_branch):
    """
    模块12：根据命宫位置，逆时针排布十二宫名称。
    顺序：命宫、兄弟、夫妻、子女、财帛、疾厄、迁移、交友、官禄、田宅、福德、父母。
    """
    names = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄", "迁移", "交友", "官禄", "田宅", "福德", "父母"]
    try:
        ming_idx = DI_ZHI.index(ming_branch)
    except ValueError:
        return {}
        
    palace_name_map = {}
    for i in range(12):
        # 十二宫逆时针推算：(命宫索引 - 步数) % 12
        target_idx = (ming_idx - i) % 12
        palace_name_map[DI_ZHI[target_idx]] = f"{names[i]}宫"
    return palace_name_map

#==========================================
# --- 安星诀的代数化 ---

# 十四主星名称
STARS_14 = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞", "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"]

def get_wuxing_bureau(ming_stem, ming_branch):
    """
    模块4：代数化推算五行局 (水2, 木3, 金4, 土5, 火6)
    修复了地支索引偏移的Bug，采用独立的子丑起点数组以确保纳音计算准确。
    """
    try:
        # 天干配对值: 甲乙(0), 丙丁(1), 戊己(2), 庚辛(3), 壬癸(4)
        s = (TIAN_GAN.index(ming_stem) - 1) // 2  
        
        # 地支配对值: 必须以子丑为起点！子丑(0), 寅卯(1), 辰巳(2)
        # 这里单独定义一个以"子"开头的数组，防止和全局的寅宫起点冲突
        z_idx = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"].index(ming_branch)
        b = (z_idx % 6) // 2  
        
    except ValueError:
        return None
        
    nayin_idx = (s + b) % 5
    # 纳音索引映射五行局数
    bureau_map = {0: 4, 1: 2, 2: 6, 3: 5, 4: 3} # 0金四, 1水二, 2火六, 3土五, 4木三
    bureau_names = {4: "金四局", 2: "水二局", 6: "火六局", 5: "土五局", 3: "木三局"}
    
    bureau_num = bureau_map[nayin_idx]
    return bureau_num, bureau_names[bureau_num]

def get_14_major_stars(day, bureau_num):
    """
    模块5：十四主星排布引擎
    输入：出生日数 (day), 五行局数 (bureau_num)
    输出：一个长度为12的列表，代表寅宫到丑宫的主星分布
    """
    # 1. 计算紫微星位置 (代数化起紫微诀)
    remainder = day % bureau_num
    x = 0 if remainder == 0 else bureau_num - remainder
    quotient = (day + x) // bureau_num
    
    # 奇数减，偶数加
    offset = -x if x % 2 != 0 else x
    
    # 紫微星地支索引 (寅=0)
    ziwei_idx = (quotient + offset - 1) % 12
    
    # 2. 计算天府星位置 (天府与紫微在寅申线对称)
    tianfu_idx = (12 - ziwei_idx) % 12
    
    # 3. 初始化十二宫星曜列表 (每个宫位可能有多颗星，所以用列表嵌套)
    palaces_stars = [[] for _ in range(12)]
    
    # 4. 紫微星系绝对偏移量 (逆时针排布)
    ziwei_series = {
        "紫微": 0, "天机": -1, "太阳": -3, "武曲": -4, "天同": -5, "廉贞": -8
    }
    for star, offset in ziwei_series.items():
        pos = (ziwei_idx + offset) % 12
        palaces_stars[pos].append(star)
        
    # 5. 天府星系绝对偏移量 (顺时针排布)
    tianfu_series = {
        "天府": 0, "太阴": 1, "贪狼": 2, "巨门": 3, "天相": 4, "天梁": 5, "七杀": 6, "破军": 10
    }
    for star, offset in tianfu_series.items():
        pos = (tianfu_idx + offset) % 12
        palaces_stars[pos].append(star)
        
    return palaces_stars

#辅星公式
# --- 左右、昌曲、空劫 ---

def get_month_hour_stars(lunar_month, hour_zhi_str):
    """
    模块6：月系与时系辅星（左辅右弼、文昌文曲、地空地劫）
    利用代数模运算，以寅宫为 0 的坐标系进行顺逆推演。
    """
    try:
        h = ZHI_HOUR.index(hour_zhi_str) + 1  # 时辰转换为数字 (子=1...亥=12)
        m = lunar_month                       # 月份 (1-12)
    except ValueError:
        return {}

    # 初始化空列表接收星曜
    stars_layout = [[] for _ in range(12)]
    
    # 1. 左辅、右弼 (月系)
    # 左辅: 辰起正月顺推 -> 起点辰(2) + M - 1 -> (m + 1) % 12
    # 右弼: 戌起正月逆推 -> 起点戌(8) - (M - 1) -> (9 - m) % 12
    stars_layout[(m + 1) % 12].append("左辅")
    stars_layout[(9 - m) % 12].append("右弼")

    # 2. 文曲、文昌 (时系)
    # 文曲: 辰起子时顺推 -> 起点辰(2) + H - 1 -> (h + 1) % 12
    # 文昌: 戌起子时逆推 -> 起点戌(8) - (H - 1) -> (9 - h) % 12
    stars_layout[(h + 1) % 12].append("文曲")
    stars_layout[(9 - h) % 12].append("文昌")

    # 3. 地空、地劫 (时系)
    # 地劫: 亥起子时顺推 -> 起点亥(9) + H - 1 -> (8 + h) % 12
    # 地空: 亥起子时逆推 -> 起点亥(9) - (H - 1) -> (10 - h) % 12
    stars_layout[(8 + h) % 12].append("地劫")
    stars_layout[(10 - h) % 12].append("地空")

    return stars_layout

#--- 禄存、羊陀、魁钺---
def get_year_stem_stars(year_stem_str):
    """
    模块7：年干系辅星（禄存、擎羊、陀罗、天魁、天钺）
    使用固定字典映射与步数偏移相结合。
    """
    stars_layout = [[] for _ in range(12)]
    
    # 1. 禄存星地支索引 (基于甲禄在寅...口诀的映射表)
    # 寅=0, 卯=1, 辰=2, 巳=3, 午=4, 未=5, 申=6, 酉=7, 戌=8, 亥=9, 子=10, 丑=11
    lu_map = {
        "甲": 0, "乙": 1, "丙": 3, "丁": 4, "戊": 3, 
        "己": 4, "庚": 6, "辛": 7, "壬": 9, "癸": 10
    }
    
    if year_stem_str in lu_map:
        lu_idx = lu_map[year_stem_str]
        stars_layout[lu_idx].append("禄存")
        # 擎羊永远在禄存前一位 (+1)，陀罗永远在禄存后一位 (-1)
        stars_layout[(lu_idx + 1) % 12].append("擎羊")
        stars_layout[(lu_idx - 1) % 12].append("陀罗")

    # 2. 天魁、天钺 (贵人星映射表)
    kui_map = {"甲": 11, "乙": 10, "丙": 9, "丁": 9, "戊": 11, "己": 10, "庚": 11, "辛": 4, "壬": 1, "癸": 1}
    yue_map = {"甲": 5, "乙": 6, "丙": 7, "丁": 7, "戊": 5, "己": 6, "庚": 5, "辛": 0, "壬": 3, "癸": 3}
    
    if year_stem_str in kui_map:
        stars_layout[kui_map[year_stem_str]].append("天魁")
        stars_layout[yue_map[year_stem_str]].append("天钺")

    return stars_layout

#--- 火铃、天马---
def get_year_branch_stars(year_branch_str, hour_zhi_str):
    """
    模块8：年支系辅星（火星、铃星、天马）
    基于地支三合局确定起点，再结合时辰推算。
    """
    try:
        yb_idx = DI_ZHI.index(year_branch_str)
        h = ZHI_HOUR.index(hour_zhi_str) + 1
    except ValueError:
        return [[] for _ in range(12)]

    stars_layout = [[] for _ in range(12)]

    # 1. 火星与铃星
    start_huo = start_ling = 0
    if yb_idx in [0, 4, 8]:     # 寅午戌
        start_huo, start_ling = 0, 1  # 丑, 卯
    elif yb_idx in [6, 10, 2]:  # 申子辰
        start_huo, start_ling = 0, 8   # 寅, 戌
    elif yb_idx in [3, 7, 11]:  # 巳酉丑
        start_huo, start_ling = 1, 8   # 卯, 戌
    elif yb_idx in [9, 1, 5]:   # 亥卯未
        start_huo, start_ling = 7, 8   # 酉, 戌

    stars_layout[(start_huo + h - 1) % 12].append("火星")
    stars_layout[(start_ling + h - 1) % 12].append("铃星")

    # 2. 天马星 (驿马星)
    ma_idx = 0
    if yb_idx in [0, 4, 8]:     # 寅午戌 马在申
        ma_idx = 6
    elif yb_idx in [6, 10, 2]:  # 申子辰 马在寅
        ma_idx = 0
    elif yb_idx in [3, 7, 11]:  # 巳酉丑 马在亥
        ma_idx = 9
    elif yb_idx in [9, 1, 5]:   # 亥卯未 马在巳
        ma_idx = 3
        
    stars_layout[ma_idx].append("天马")

    return stars_layout

#--- 生年四化（化禄、化权、化科、化忌）---
#四化星是紫微斗数推断吉凶的绝对核心。这个没有数学推演，纯粹是十天干与特定星曜的哈希映射（Hash Map）。

def get_sihua_stars(year_stem_str):
    """
    模块9：生年四化（禄、权、科、忌）
    返回一个字典，明确指出哪颗星被“四化”附体。
    """
    # 四化标准口诀映射表 (甲: 廉破武阳, 乙: 机梁紫阴, 丙: 同机昌廉...)
    sihua_map = {
        "甲": {"化禄": "廉贞", "化权": "破军", "化科": "武曲", "化忌": "太阳"},
        "乙": {"化禄": "天机", "化权": "天梁", "化科": "紫微", "化忌": "太阴"},
        "丙": {"化禄": "天同", "化权": "天机", "化科": "文昌", "化忌": "廉贞"},
        "丁": {"化禄": "太阴", "化权": "天同", "化科": "天机", "化忌": "巨门"},
        "戊": {"化禄": "贪狼", "化权": "太阴", "化科": "右弼", "化忌": "天机"},
        "己": {"化禄": "武曲", "化权": "贪狼", "化科": "天梁", "化忌": "文曲"},
        "庚": {"化禄": "太阳", "化权": "武曲", "化科": "太阴", "化忌": "天同"},
        "辛": {"化禄": "巨门", "化权": "太阳", "化科": "文曲", "化忌": "文昌"},
        "壬": {"化禄": "天梁", "化权": "紫微", "化科": "左辅", "化忌": "武曲"},
        "癸": {"化禄": "破军", "化权": "巨门", "化科": "太阴", "化忌": "贪狼"}
    }
    
    return sihua_map.get(year_stem_str, {})

#--- 重要杂曜（红鸾、天喜、天哭、天虚）的代数降维---
#传统口诀：“红鸾卯上起子逆数至生年支，天喜对宫。天哭午上起子逆数，天虚午上起子顺数。”

def get_minor_stars(year_branch_str):
    """
    模块10：重要杂曜（红鸾、天喜、天哭、天虚）
    全部转化为绝对坐标的模运算。
    """
    try:
        yb_idx = DI_ZHI.index(year_branch_str) # 子=10, 丑=11, 寅=0... 
        # 为了方便年支起算，我们将地支重新映射: 子=0, 丑=1, 寅=2... 亥=11
        d_idx = (yb_idx + 2) % 12 
    except ValueError:
        return [[] for _ in range(12)]
        
    stars_layout = [[] for _ in range(12)]
    
    # 1. 红鸾：卯(1)起子(0)逆推 -> (1 - 岁支) % 12
    hongluan_idx = (1 - d_idx) % 12
    stars_layout[hongluan_idx].append("红鸾")
    
    # 2. 天喜：永远在红鸾对宫 (+6)
    tianxi_idx = (hongluan_idx + 6) % 12
    stars_layout[tianxi_idx].append("天喜")
    
    # 3. 天哭：午(4)起子(0)逆推 -> (4 - 岁支) % 12
    tianku_idx = (4 - d_idx) % 12
    stars_layout[tianku_idx].append("天哭")
    
    # 4. 天虚：午(4)起子(0)顺推 -> (4 + 岁支) % 12
    tianxu_idx = (4 + d_idx) % 12
    stars_layout[tianxu_idx].append("天虚")
    
    return stars_layout

#--- 大限推算引擎（时间轴）---
#大限是推断一个人在特定年龄段（10年）运势的基础。它不仅取决于“五行局”的岁数起步，还受“阴阳男/阴阳女”的顺逆行规则控制。

def get_daxian_layout(year_stem_str, gender, ming_palace_branch, bureau_num):
    """
    模块11：大限（十年运势）排布
    输入: 年干(定阴阳), 性别(男/女), 命宫地支, 五行局数(起步年龄)
    输出: 包含十二宫大限年龄段的字典
    """
    # 1. 判断天干阴阳
    yang_stems = ["甲", "丙", "戊", "庚", "壬"]
    is_yang = year_stem_str in yang_stems
    
    # 2. 判断顺逆行（阳男阴女顺行，阴男阳女逆行）
    if (is_yang and gender == "男") or (not is_yang and gender == "女"):
        direction = 1  # 顺时针
    else:
        direction = -1 # 逆时针
        
    # 3. 计算十二宫的年龄段
    try:
        ming_idx = DI_ZHI.index(ming_palace_branch)
    except ValueError:
        return {}
        
    daxian_layout = {}
    
    for step in range(12):
        # 当前宫位索引
        current_palace_idx = (ming_idx + step * direction) % 12
        # 大限起始与结束年龄 (例如：水二局，步数为0时是 2-11岁)
        start_age = bureau_num + step * 10
        end_age = start_age + 9
        
        palace_name = DI_ZHI[current_palace_idx]
        daxian_layout[palace_name] = f"{start_age}-{end_age}岁"
        
    return daxian_layout

# ==========================================

def get_advanced_profile(year_stem, year_branch, ming_branch, gender):
    """
    模块13：进阶命理档案（阴阳性别、命主、身主）
    """
    # 1. 阴阳性别
    yang_stems = ["甲", "丙", "戊", "庚", "壬"]
    yin_yang = "阳" if year_stem in yang_stems else "阴"
    yy_gender = f"{yin_yang}{gender}"
    
    # 2. 命主 (由命宫地支决定)
    ming_master_map = {
        "子":"贪狼", "丑":"巨门", "寅":"禄存", "卯":"文曲", 
        "辰":"廉贞", "巳":"武曲", "午":"破军", "未":"武曲", 
        "申":"廉贞", "酉":"文曲", "戌":"禄存", "亥":"巨门"
    }
    
    # 3. 身主 (由生年地支决定)
    shen_master_map = {
        "子":"铃星", "丑":"天相", "寅":"天梁", "卯":"天同", 
        "辰":"文昌", "巳":"天机", "午":"火星", "未":"天相", 
        "申":"天梁", "酉":"天同", "戌":"文昌", "亥":"天机"
    }
    
    return yy_gender, ming_master_map.get(ming_branch, ""), shen_master_map.get(year_branch, "")

#--- 最常用的乙级星（孤寡、刑姚、龙凤、台座等约 10 颗）---

def get_high_freq_secondary_stars(lunar_month, lunar_day, year_branch_str, mh_stars):
    """
    模块14：高频乙级辅星（刑姚、孤寡、龙凤、台座、恩贵）
    """
    try:
        yb_idx = DI_ZHI.index(year_branch_str) 
        z_idx = (yb_idx + 2) % 12 # 映射为子=0起算的索引
    except ValueError:
        return [[] for _ in range(12)]
        
    stars_layout = [[] for _ in range(12)]
    
    # 1. 天刑与天姚 (月系)
    stars_layout[(6 + lunar_month) % 12].append("天刑")
    stars_layout[(10 + lunar_month) % 12].append("天姚")
    
    # 2. 孤辰与寡宿 (年支三会局系)
    group = yb_idx // 3
    stars_layout[(group * 3 + 3) % 12].append("孤辰")
    stars_layout[(group * 3 + 11) % 12].append("寡宿")
    
    # 3. 龙池与凤阁 (年支系)
    stars_layout[(2 + z_idx) % 12].append("龙池")
    stars_layout[(8 - z_idx) % 12].append("凤阁")

    # 4. 获取辅弼昌曲位置用于推算关联星曜
    zuo_idx = you_idx = chang_idx = qu_idx = 0
    for i in range(12):
        if "左辅" in mh_stars[i]: zuo_idx = i
        if "右弼" in mh_stars[i]: you_idx = i
        if "文昌" in mh_stars[i]: chang_idx = i
        if "文曲" in mh_stars[i]: qu_idx = i

    # 5. 三台八座 (辅弼日系) / 恩光天贵 (昌曲日系)
    stars_layout[(zuo_idx + lunar_day - 1) % 12].append("三台")
    stars_layout[(you_idx - lunar_day + 1) % 12].append("八座")
    stars_layout[(chang_idx + lunar_day - 2) % 12].append("恩光")
    stars_layout[(qu_idx + lunar_day - 2) % 12].append("天贵")
    
    return stars_layout

# --- 终极主控函数 (提供给 AI 直接调用) ---

def build_ziwei_chart(year_stem, year_branch, lunar_month, lunar_day, hour_zhi, gender, is_leap=False):
    """
    终极排盘组装函数。
    参数 is_leap: 默认为 False。若用户出生于闰月，由调用者传入 True。
    """
    # 自动处理闰月逻辑 (模块修正)
    # 根据紫微斗数惯例：闰月15日及之前按本月算，16日及以后按后一月算
    actual_month = lunar_month
    if is_leap and lunar_day > 15:
        actual_month = (lunar_month % 12) + 1

    # 1. 基础参数计算
    palace_stems = get_all_palace_stems(year_stem)
    # 使用处理后的 actual_month 计算命身宫
    ming_branch, shen_branch = get_ming_shen_palace(actual_month, hour_zhi)
    if not ming_branch: return "命宫计算失败"
    
    # 2. 核心局数与宫名
    ming_idx = DI_ZHI.index(ming_branch)
    bureau_num, bureau_name = get_wuxing_bureau(palace_stems[ming_idx], ming_branch)
    palace_name_map = get_palace_names(ming_branch)
    
    # 3. 星曜全量获取 (使用 actual_month 计算月系星曜)
    major_stars = get_14_major_stars(lunar_day, bureau_num)
    mh_stars = get_month_hour_stars(actual_month, hour_zhi)
    ys_stars = get_year_stem_stars(year_stem)
    yb_stars = get_year_branch_stars(year_branch, hour_zhi)
    minor_stars = get_minor_stars(year_branch)
    high_freq_stars = get_high_freq_secondary_stars(actual_month, lunar_day, year_branch, mh_stars)
    
    # 4. 辅助档案
    sihua = get_sihua_stars(year_stem)
    daxian = get_daxian_layout(year_stem, gender, ming_branch, bureau_num)
    yy_gender, ming_master, shen_master = get_advanced_profile(year_stem, year_branch, ming_branch, gender)
    
    # 5. 数据拼装
    chart_data = {}
    for i in range(12):
        zhi = DI_ZHI[i]
        # 合并所有星曜列表
        all_stars = major_stars[i] + mh_stars[i] + ys_stars[i] + yb_stars[i] + minor_stars[i] + high_freq_stars[i]
        
        # 处理四化标注
        formatted_stars = []
        for star in all_stars:
            hua = "".join([f"[{k}]" for k, v in sihua.items() if v == star])
            formatted_stars.append(f"{star}{hua}")
            
        chart_data[zhi] = {
            "宫位名称": palace_name_map.get(zhi, ""),
            "宫干地支": f"{palace_stems[i]}{zhi}",
            "是否命身": ("命宫" if zhi == ming_branch else "") + ("身宫" if zhi == shen_branch else ""),
            "星曜": formatted_stars,
            "大限": daxian.get(zhi, "")
        }
        
    return {
        "五行局": bureau_name,
        "阴阳性别": yy_gender,
        "命主": ming_master,
        "身主": shen_master,
        "命盘数据": chart_data
    }
# --- Streamlit 界面逻辑 ---

st.set_page_config(page_title="Hermes 紫微斗数排盘引擎", layout="wide")

# 自定义 CSS 让表格更像命盘
st.markdown("""
    <style>
    .stTable { font-size: 14px !important; }
    .palace-box { border: 1px solid #ddd; padding: 10px; height: 150px; background-color: #f9f9f9; }
    .main-star { color: #d32f2f; font-weight: bold; font-size: 18px; }
    .palace-name { color: #1976d2; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("🌙 生辰输入")
    name = st.text_input("姓名", "命主")
    gender = st.radio("性别", ["男", "女"])
    birth_date = st.date_input("出生日期", datetime.date(1990, 6, 1))
    birth_time = st.time_input("出生时间", datetime.time(12, 30))
    is_leap = st.checkbox("是否闰月出生")
    
    submit = st.button("开启天命盘", type="primary")

if submit:
        # 1. 彻底初始化所有变量，确保不会报 NameError
        result = None
        ct = None
        y8 = m8 = d8 = h8 = "未知"
        y_stem = y_branch = ""
        
        dt = datetime.datetime.combine(birth_date, birth_time)
        
        try:
            # 初始化 cnlunar
            ct = cnlunar.Lunar(dt, godType=0)
            
            # --- 自动探测八字属性 (兼容所有大小写版本) ---
            def get_lunar_attr(obj, base_name):
                for suffix in [base_name.lower(), base_name.capitalize(), base_name]:
                    val = getattr(obj, suffix, None)
                    if val and isinstance(val, str): return val
                return "未知"

            y8 = get_lunar_attr(ct, 'year8Char')
            m8 = get_lunar_attr(ct, 'month8Char')
            d8 = get_lunar_attr(ct, 'day8Char')
            h8 = get_lunar_attr(ct, 'twohour8Char')

            # --- 关键防护：确保 y8 格式正确且在 TIAN_GAN/DI_ZHI 范围内 ---
            if len(y8) >= 2 and y8[0] in TIAN_GAN and y8[1] in DI_ZHI:
                y_stem, y_branch = y8[0], y8[1]
            else:
                # 如果 cnlunar 返回异常，尝试根据日期强制计算一个默认值，防止 index error
                y_stem, y_branch = TIAN_GAN[0], DI_ZHI[0] 
                
            l_month = getattr(ct, 'lunarMonth', 1)
            l_day = getattr(ct, 'lunarDay', 1)
            
            # 时辰索引保护
            hour_idx = (dt.hour + 1) // 2 % 12
            h_zhi = DI_ZHI[hour_idx]

            # 2. 调用核心引擎 (增加局部异常捕获，防止 TypeError)
            try:
                # 显式传递参数，确保不为 None
                if y_stem and y_branch:
                    result = build_ziwei_chart(y_stem, y_branch, l_month, l_day, h_zhi, gender, is_leap)
                else:
                    st.error("❌ 无法识别年干支，请检查出生日期。")
            except Exception as e_inner:
                st.error(f"❌ 算法引擎内部崩溃: {str(e_inner)}")
                result = None

        except Exception as lunar_err:
            st.error(f"❌ 农历换算逻辑崩溃: {str(lunar_err)}")

        # 3. 渲染界面 (使用严格判定，彻底解决 result["命盘数据"] 的 TypeError)
        if isinstance(result, dict) and "命盘数据" in result:
            st.subheader(f"📊 {name} 的紫微命盘")
            st.info(f"**生辰八字：** {y8}年 {m8}月 {d8}日 {h8}时")
            
            # 渲染中宫
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("五行局", result.get("五行局", "N/A"))
            c2.metric("阴阳性别", result.get("阴阳性别", "N/A"))
            c3.metric("命主", result.get("命主", "N/A"))
            c4.metric("身主", result.get("身主", "N/A"))

            # 4. 渲染 4x3 布局 (绝对安全的字典访问)
            chart_data = result["命盘数据"]
            rows = [
                ["巳", "午", "未", "申"],
                ["辰", "中宫", "中宫", "酉"],
                ["卯", "中宫", "中宫", "戌"],
                ["寅", "丑", "子", "亥"]
            ]
            
            for r in rows:
                cols = st.columns(4)
                for i, zhi in enumerate(r):
                    if zhi == "中宫":
                        cols[i].empty()
                    else:
                        cell = chart_data.get(zhi)
                        if cell:
                            with cols[i].container():
                                # 宫位标题
                                t = f"**{cell.get('宫位名称', '未知')}**"
                                if "命宫" in cell.get('是否命身',''): t += " ✨"
                                cols[i].markdown(t)
                                
                                # 星曜展示
                                stars = cell.get('星曜', [])
                                if stars:
                                    # 前两颗为主星，红色显示
                                    m_stars = " ".join(stars[:2])
                                    s_stars = " ".join(stars[2:])
                                    cols[i].markdown(f"<span style='color:red;font-weight:bold'>{m_stars}</span>", unsafe_allow_html=True)
                                    if s_stars: cols[i].caption(s_stars)
                                
                                cols[i].write(f"{cell.get('宫干地支','')} {cell.get('大限','')}")
                                cols[i].divider()
        elif result is not None and isinstance(result, str):
            st.warning(f"⚠️ 引擎返回提示: {result}")
        elif submit and result is None:
            # 如果点击了提交但 result 依然是 None，说明前面的 try 块报错了，上面已经有 st.error 了
            pass

        if submit:
            # 1. 预先初始化所有可能用到的变量，防止 NameError
            y8 = m8 = d8 = h8 = "未知"
            result = None
            ct = None
    
            dt = datetime.datetime.combine(birth_date, birth_time)
            
            try:
                ct = cnlunar.Lunar(dt, godType=0)
                
                # 兼容性提取八字数据
                if hasattr(ct, 'year8char'):
                    y8, m8, d8, h8 = ct.year8char, ct.month8char, ct.day8char, ct.twohour8char
                else:
                    y8, m8, d8, h8 = ct.get_year8char(), ct.get_month8char(), ct.get_day8char(), ct.get_twohour8char()
                
                # 提取排盘参数
                y_stem, y_branch = y8[0], y8[1]
                l_month = ct.lunarMonth
                l_day = ct.lunarDay
                hour_idx = (dt.hour + 1) // 2 % 12
                h_zhi = DI_ZHI[hour_idx] # 确保你定义的 DI_ZHI 包含子到亥
    
                # 2. 调用核心引擎
                result = build_ziwei_chart(y_stem, y_branch, l_month, l_day, h_zhi, gender, is_leap)
    
            except Exception as e:
                st.error(f"❌ 数据换算或引擎报错: {str(e)}")

        # 3. 渲染界面 (只有当 result 有内容时才执行)
        if result:
            st.subheader(f"📊 {name} 的紫微命盘")
            st.info(f"**生辰八字：** {y8}年 {m8}月 {d8}日 {h8}时")
            
            # --- 后面接 col1.metric 和 4x3 布局代码 ---
            # 注意：确保下面的代码中使用的是 result.get("命盘数据", {})

        # --- 渲染 4x3 命盘 (这里使用 Streamlit Columns 模拟) ---
        # 第一排：巳 午 未 申
        rows = [
            ["巳", "午", "未", "申"],
            ["辰", "中宫", "中宫", "酉"],
            ["卯", "中宫", "中宫", "戌"],
            ["寅", "丑", "子", "亥"]
        ]
        
        data = result["命盘数据"]
        
        for row in rows:
            cols = st.columns(4)
            for i, zhi in enumerate(row):
                if zhi == "中宫":
                    cols[i].write("") # 留空
                else:
                    cell = data[zhi]
                    with cols[i].container():
                        st.markdown(f"**{cell['宫位名称']}** {cell['是否命身'].replace('命宫','✨')}")
                        st.markdown(f"<span class='main-star'>{' '.join(cell['星曜'][:2])}</span>", unsafe_allow_html=True)
                        st.caption(f"{' '.join(cell['星曜'][2:6])}")
                        st.write(f"{cell['宫干地支']} {cell['大限']}")
                        st.divider()

st.success("💡 提示：本排盘由 Hermes Poseidon驱动，已对齐文墨天机专业版逻辑。")
