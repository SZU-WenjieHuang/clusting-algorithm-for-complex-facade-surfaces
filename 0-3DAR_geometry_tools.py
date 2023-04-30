# coding=utf-8
import rhinoinside
rhinoinside.load()
# import run
import Rhino.Geometry as rg
import math

#from Rhino.Geometry import Curve as rc
#import ghpythonlib.treehelpers as tr

# XKool_DAR_Rhinocommon 工具集
"""
曲线差集
rg.Curve.CreateBooleanDifference(curve,curve)
曲线交集
rg.Curve.CreateBooleanIntersection(curve, curve)
曲线并集
rg.Curve.CreateBooleanUnion(curves)
曲线分段
list(polyline.DuplicateSegments())
曲线节点
[i for i in polyline]
曲线中点
Curve.PointAt(crv.Domain[1]/2)
曲线长度
crv.Domain[1]
"""


def to_NurbsCurve(objects):
    """
    1 将物体转化为NurbsCurve
    :param objects:
    :return:
    """
    if type(objects) is list:
        return [i.ToNurbsCurve() for i in objects]
    if type(objects) is not list:
        return objects.ToNurbsCurve()


def createPlanarBreps(curve):
    """
    2 将曲线转化为brep平面
    :param curve:
    :return: brep
    """
    return rg.Brep.CreatePlanarBreps(curve)


def join_curves(curves):
    """
    3 合并曲线
    当crvs类型为item或者为list且len值等于1时，输出等于输入
    当crvs类型为list时，输出join
    """
    if type(curves) is not list or type(curves) is list and len(curves) == 1:
        return curves
    elif type(curves) is list:
        return list(rg.Curve.JoinCurves(curves))


def _offset(curves, dis):
    """
    4 易用曲线偏移
    (直角，xy平面，正反向偏移)
    当crvs类型为item或者为list且len值等于1时，输出单线offset
    当crvs类型为list时，输出多线offset
    """
    cornerStyle = rg.CurveOffsetCornerStyle(1)

    if type(curves) is not list:
        return curves.Offset(rg.Plane.WorldXY, dis, 0.001, cornerStyle)[0]
    elif type(curves) is list:
        return [i.Offset(rg.Plane.WorldXY, dis, 0.001, cornerStyle)[0] for i in curves]


def offset(curves, dis, both=False):
    """
    5 可双向offset
    curve为闭合图形时，dis正：内偏移；dis负：外偏移
    """
    if both is True:
        return [_offset(curves, dis), _offset(curves, -dis)]
    elif both is not True:
        return _offset(curves, dis)


def polyline_to_bar(polyline, dis, planar=False):
    """
    6 polyline生成条形几何
    :param polyline:
    :param dis:
    :return:
    """
    # 两侧偏移线
    poly1 = offset(polyline, dis, both=True)[0]
    poly2 = offset(polyline, dis, both=True)[1]
    # 当两偏移线均为闭合线时
    if poly1.IsClosed is True and poly2.IsClosed is True:
        if planar is False:
            return [poly1, poly2]
        elif planar is True:
            brep1 = createPlanarBreps(poly1)[0]
            brep2 = createPlanarBreps(poly2)[0]
            return rg.Brep.CreateBooleanDifference(brep1, brep2, 0.001)
    # 当两偏移线不为闭合线时
    else:
        # 短边封口线
        line1 = rg.Polyline([poly1.PointAtStart, poly2.PointAtStart])
        line2 = rg.Polyline([poly1.PointAtEnd, poly2.PointAtEnd])
        # 转化为NurbsCurve
        nurbs_lst = to_NurbsCurve([poly1, poly2, line1, line2])
        if planar is False:
            return join_curves(nurbs_lst)
        elif planar is True:
            join_crv = join_curves(nurbs_lst)
            return rg.Brep.CreatePlanarBreps(join_crv)


def _transformOrientation(curve):
    """
    7 单一曲线的方向翻转
    :param curve: 曲线
    :return: 统一方向的曲线
    """
    if curve.IsClosed is True:
        if str(curve.ClosedCurveOrientation()) == 'CounterClockwise':
            curve.Reverse()
            return curve
        else:
            return curve


def transformOrientation(curves):
    """
    8 曲线的方向统一
    :param curves: 曲线
    :return: 统一方向的曲线
    """
    if type(curves) is not list:
        return _transformOrientation(curves)
    elif type(curves) is list:
        return [_transformOrientation(i) for i in curves]


def _choose_intersectionCrvs(crv_goal, crv_others):
    """
    9 单一曲线选择曲线集合中相交的图形
    :param crv_goal: 单曲线
    :param crv_others: 曲线集合
    :return: 选出的曲线集合,未选到的曲线集合
    """
    itsct_lst = []
    rest_lst = []
    for i in crv_others:
        event = rg.Intersect.Intersection.CurveCurve(crv_goal, i, 0.001, 0.0)
        if event.Count == 0:
            rest_lst.append(i)
            continue
        itsct_lst.append(i)
    return [itsct_lst, rest_lst]


def choose_intersectionCrvs(crv_goals, crv_others):
    """
    10 选择曲线中与目标曲线相交的曲线
    :param crv_goals:
    :param crv_others:
    :return:
    """
    if type(crv_goals) is not list:
        itsct_lst = _choose_intersectionCrvs(crv_goals, crv_others)[0]
        rest_lst = _choose_intersectionCrvs(crv_goals, crv_others)[1]
        return [itsct_lst, rest_lst]
    elif type(crv_goals) is list:
        crvs_bool = rg.Curve.CreateBooleanUnion(crv_goals)
        itsct_lst = Pytools.flat([_choose_intersectionCrvs(i, crv_others)[0] for i in crvs_bool])
        rest_lst = Pytools.flat([_choose_intersectionCrvs(i, crv_others)[1] for i in crvs_bool])
        return [itsct_lst, rest_lst]


def _multiple_trim(crv_goal, crv_others):
    """
    12 单线split多线
    :param crv_goal:
    :param crv_others:
    :return:
    """
    # 有动态输入时
    if crv_goal is not None:
        # 求选择线
        choosed_crvs = choose_intersectionCrvs(crv_goal, crv_others)[0]
        # 求剩余线
        rest_crvs = choose_intersectionCrvs(crv_goal, crv_others)[1]
        # 被分者
        split_blocks = []
        # 切割者
        cutter_blocks = []
        for i in choosed_crvs:
            split_blocks.extend(list(rg.Curve.CreateBooleanDifference(i, crv_goal)))
            cutter_blocks.extend(list(rg.Curve.CreateBooleanIntersection(i, crv_goal)))
        # 合并全部曲线
        blocks = rest_crvs[:]
        blocks.extend(split_blocks)
        return [blocks, cutter_blocks]
    # 无动态输入时
    elif crv_goal is None:
        return [crv_others, None]


def multiple_trim(crv_goals, crv_others):
    """
    13 多线split并拾取包含的线
    :param crv_goals:
    :param crv_others:
    :return: [0]被打断的线[1]cutter生成的打断线
    """
    iter_lst = rg.Curve.CreateBooleanUnion(crv_goals)
    # 储存cutter自身分割出的图形
    cutter_blocks = []
    blocks = crv_others
    for i in iter_lst:
        # 迭代储存被分割图形
        blocks_i = _multiple_trim(i, blocks)[0]
        # 集合储存cutter自身分割出的图形
        cutters_i = _multiple_trim(i, blocks)[1]
        cutter_blocks.extend(cutters_i)
        blocks = blocks_i
    # 在blocks中提取出来crvs
    inCrvs = choose_inCrvs(crv_goals, blocks)[0]
    cutter_blocks = inCrvs + cutter_blocks
    blocks = choose_inCrvs(crv_goals, blocks)[1]
    return [blocks, cutter_blocks]


def find_discontinuities(curve):
    """
    14 寻找曲线不连续节点
    :param curve: 单一曲线
    :return: 节点集合
    """
    cont = rg.Continuity.G2_locus_continuous
    dom = curve.Domain
    t = dom[0]
    params = []
    if curve.IsClosed:
        pass
    elif not curve.IsClosed:
        params.append(curve.PointAtStart)
    while True:
        rst = curve.GetNextDiscontinuity(cont, t, dom[1])
        if not rst[0]:break
        t = rst[1]
        params.append(curve.PointAt(t))
    return params


def pts_in_closedCrv(pts, crv):
    """
    根据多点与单线的关系分类点
    :param pts: 多点
    :param crv: 单曲线
    :return: [0] 在线外的点 [1] 在线内的点 [2] 在线上的点
    """
    pts0 = []
    pts1 = []
    pts2 = []
    for i in pts:
        if str(crv.Contains(i)) == "Outside":
            pts0.append(i)
        elif str(crv.Contains(i)) == "Inside":
            pts1.append(i)
        elif str(crv.Contains(i)) == "Coincident":
            pts2.append(i)
    return pts0, pts1, pts2


def pts_in_closedCrvs(pts, curves):
    """
    根据多点与多线的关系分类点
    :param pts: 多点
    :param curves: 多曲线
    :return: [0] 在线外的点 [1] 在线内的点 [2] 在线上的点
    """
    pts0 = []
    pts1 = []
    pts2 = []
    bool_curves = rg.Curve.CreateBooleanUnion(curves)
    for i in bool_curves:
        pts0.extend(pts_in_closedCrv(pts, i)[0])
        pts1.extend(pts_in_closedCrv(pts, i)[1])
        pts2.extend(pts_in_closedCrv(pts, i)[2])
    return pts0, pts1, pts2


def choose_Crvs(crv_goal, crv_others):
    """
    根据曲线和目标曲线的相交与包含关系分类曲线集
    :param crv_goal: 单曲线
    :param crv_others: 多曲线
    :return: [0]在内部的曲线 [1]在外部的曲线 [2]相交的曲线
    """
    inCrvs = []
    outCrvs = []
    intersectCrvs = []
    for i in crv_others:
        # 找到轮廓的角点
        pts_corner = find_discontinuities(i)
        # 在线外的点的数量
        count_out = len(pts_in_closedCrv(pts_corner, crv_goal)[0])
        # 在线内的点的数量
        count_in = len(pts_in_closedCrv(pts_corner, crv_goal)[1])
        if count_out == 0:
            # 在线内
            inCrvs.append(i)
        elif count_in == 0:
            # 在线外
            outCrvs.append(i)
        else:
            # 相交
            intersectCrvs.append(i)
    return inCrvs, outCrvs, intersectCrvs


def choose_inCrvs(crv_goals, crv_others):
    """
    选择曲线内的点
    :param crv_goals: 多曲线
    :param crv_others: 待筛选的曲线
    :return: 内部的曲线集
    """
    if type(crv_goals) is not list:
        return choose_Crvs(crv_goals, crv_others)[0]
    elif type(crv_goals) is list:
        inCrvs_lst = []
        bool_crvs = rg.Curve.CreateBooleanUnion(crv_goals)
        for i in bool_crvs:
            inCrvs = choose_Crvs(i, crv_others)[0]
            inCrvs_lst.extend(inCrvs)
        outCrvs_lst = crvList_difference(crv_others, inCrvs_lst)[1]
        return inCrvs_lst, outCrvs_lst


def dic_midPt_crv(crvs):
    """
    建立曲线中点作key的字典
    :param crvs:
    :return:
    """
    keys = []
    for i in crvs:
        pt = i.PointAt(i.Domain[1]/2)
        keys.append((round(pt.X, 2), round(pt.Y, 2)))
    dict(zip(keys, crvs))
    return dict(zip(keys, crvs))


def crvList_union(crvlst1, crvlst2):
    """
    曲线list的并集（关联：dic_midPt_crv）
    :param crvlst1:
    :param crvlst2:
    :return:并集
    """
    # 中点key，曲线value字典
    dic1 = dic_midPt_crv(crvlst1)
    dic2 = dic_midPt_crv(crvlst2)
    # 取key交集
    itsct = list(set(dic1.keys()) & set(dic2.keys()))
    # 取key差集
    differ1 = set(dic1.keys())-set(dic2.keys())
    differ2 = set(dic2.keys())-set(dic1.keys())
    # 取value集
    itsct_crvs = [dic1[i] for i in itsct]
    differ_crv1 = [dic1[i] for i in differ1]
    differ_crv2 = [dic2[i] for i in differ2]
    union_crvs = itsct_crvs+differ_crv1+differ_crv2
    return union_crvs


def crvList_difference(crvlst1, crvlst2):
    """
    曲线list的差集（关联：dic_midPt_crv）
    :param crvlst1:
    :param crvlst2:
    :return: [0]差集和[1]crv1被crv2差集[2]crv2被crv1差集
    """
    # 中点key，曲线value字典
    dic1 = dic_midPt_crv(crvlst1)
    dic2 = dic_midPt_crv(crvlst2)
    # 取key差集
    differ1 = set(dic1.keys())-set(dic2.keys())
    differ2 = set(dic2.keys())-set(dic1.keys())
    # 取value集
    differ_crv1 = [dic1[i] for i in differ1]
    differ_crv2 = [dic2[i] for i in differ2]
    differ_crvs = differ_crv1 + differ_crv2
    return differ_crvs, differ_crv1, differ_crv2


def crvList_intersection(crvlst1, crvlst2):
    """
    曲线list的交集（关联：dic_midPt_crv）
    :param crvlst1:
    :param crvlst2:
    :return: 交集list
    """
    # 中点key，曲线value字典
    dic1 = dic_midPt_crv(crvlst1)
    dic2 = dic_midPt_crv(crvlst2)
    # 取key交集
    itsct = list(set(dic1.keys()) & set(dic2.keys()))
    # 取value交集
    itsct_crvs = [dic1[i] for i in itsct]
    return itsct_crvs


def dis_ptToCrv(crv, pt):
    """
    测量点与曲线的距离，并求出最近点
    :param crv:
    :param pt:
    :return:
    """
    t = rg.Curve.ClosestPoint(crv, pt)[1]
    pt_t = rg.Curve.PointAt(crv, t)
    dis = rg.Point3d.DistanceTo(pt, pt_t)
    return dis, pt_t


def choose_lgest_lines(polys, n=1, rev=True):
    """
    寻找最长n边，如果是polyline则优先分解，如果是line则报错
    :param polys: 单polyline或者多条lines
    :param n: 最长的几条边 int
    :param rev: [True]最长边 [False]最短边
    :return: 最值的边
    """
    if type(polys) is list:
        polys_lst = sorted(polys, key=lambda x: x.Domain[1], reverse=rev)
        return polys_lst[0:n]
    elif type(polys) is not list:
        polys = list(polys.DuplicateSegments())
        if not len(polys):
            raise Exception("输入的curve为line，无法分解及排序")
        polys_lst = sorted(polys, key=lambda x: x.Domain[1], reverse=rev)
        return polys_lst[0:n]


def choose_nrest_line(polys, pt=None, rev=False):
    """
    寻找距离点最近的线，当无输入点时，自动选择最长边
    :param polys:
    :param pt:
    :param rev:
    :return:
    """
    # 无输入点
    if pt is None:
        return choose_lgest_lines(polys)
    # 有输入点
    elif pt is not None:
        if type(polys) is list:
            polys_lst = sorted(polys, key=lambda x: dis_ptToCrv(x, pt)[0], reverse=rev)
            return polys_lst[0]
        elif type(polys) is not list:
            polys = list(polys.DuplicateSegments())
            if not len(polys):
                raise Exception("输入的curve为line，无法分解及排序")
            polys_lst = sorted(polys, key=lambda x: dis_ptToCrv(x, pt)[0], reverse=rev)
            return polys_lst[0]


class Pytools:
    @staticmethod
    def flat(lst):
        """
         拍平
        :param lst: 列表
        :return: 内部拍平的列表
        """
        l = []
        for i in lst:
            if type(i) is list:
                for j in i:
                    l.append(j)
            else:
                l.append(i)
        return l

    @staticmethod
    def put_in_dict(dic, key, value):
        """
        以合并key而非删除重复key的方式建立字典
        :param dic:
        :param key:
        :param value:
        :return:
        """
        if key not in dic.keys():
            dic[key] = [value]
        elif key in dic.keys():
            dic.get(key).append(value)


def crv_area(crv):
    """
    求闭合平面曲线面积
    :param crv: 闭合平面曲线 : Curve/Polyline/PolylineCurve/Rectangle
    :return: 面积 : float
    """
    if type(crv).__name__ == "PolylineCurve":
        crv = crv
    else:
        crv = crv.ToNurbsCurve()
    # Exception
    if not crv.IsClosed:
        raise Exception("请输入闭合曲线")
    elif not crv.IsPlanar():
        raise Exception("请输入平面曲线")
    return rg.AreaMassProperties.Compute(crv).Area


class Transformation:
    @staticmethod
    def move(obj, dir, keep=True):
        """
        求闭合平面曲线面积
        :param obj: 需要变换的物体
        :param dir: 变换向量 Vector3d
        :param keep: 是否保留原obj，默认True
        :return: 变换后的物体
        """
        transformation = rg.Transform.Translation(dir)

        if keep is True:
            obj.Transform(transformation)
            return obj

        elif keep is False:
            if hasattr(obj, "Duplicate"):
                obj_copied = obj.Duplicate()
                obj_copied.Transform(transformation)
                return obj_copied
            else:
                raise Exception("该物体无法被复制，需使用原位变换")

    @staticmethod
    def mirror(obj, plane, keep=True):
        """
        求闭合平面曲线面积
        :param obj: 需要变换的物体
        :param plane: 镜像平面 Plane
        :param keep: 是否保留原obj，默认True
        :return: 变换后的物体
        """
        transformation = rg.Transform.Mirror(plane)
        if keep is True:
            obj.Transform(transformation)
            return obj
        elif keep is False:
            if hasattr(obj, "Duplicate"):
                obj_copied = obj.Duplicate()
                obj_copied.Transform(transformation)
                return obj_copied
            else:
                raise Exception("该物体无法被复制，需使用原位变换")

    @staticmethod
    def scale(obj, scaler, centre, keep=True):
        """
        求闭合平面曲线面积
        :param obj: 需要变换的物体
        :param scaler: 缩放比例 float
        :param center: 缩放中心 Point3d
        :param keep: 是否保留原obj，默认True
        :return
        """
        transformation = rg.Transform.Scale(centre, scaler)
        if keep is True:
            obj.Transform(transformation)
            return obj
        elif keep is False:
            if hasattr(obj, "Duplicate"):
                obj_copied = obj.Duplicate()
                obj_copied.Transform(transformation)
                return obj_copied
            else:
                raise Exception("该物体无法被复制，需使用原位变换")

    @staticmethod
    def rotate(obj, angle, axis, center, keep=True):
        """
        求闭合平面曲线面积
        :param obj: 需要变换的物体
        :param angle: 旋转角度 float
        :param axis: 旋转轴 Vector3d
        :param center: 旋转中心 Point3d
        :param keep: 是否保留原obj，默认True
        :return
        """
        angle = (math.pi/180)*angle
        transformation = rg.Transform.Rotation(angle,axis,center)
        #
        if keep is True:
            obj.Transform(transformation)
            return obj
        # 判断物体能否被复制
        elif keep is False:
            if hasattr(obj, "Duplicate"):
                obj_copied = obj.Duplicate()
                obj_copied.Transform(transformation)
                return obj_copied
            else:
                raise Exception("该物体无法被复制，需使用原位变换")


if __name__ == '__main__':
    pass

    # a = join_curves(crvs)
    #
    # b = offset(a, 100, both=True)
    # print b
    ##crv1 = polyline_to_bar(join_curves(crvs),100)
    ##crv2 = polyline_to_bar(join_curves(crvs),100)
    # print len(offset(test,100))
    # d = offset(test,100)[0]
    # e = offset(test,100)[1]
    # print type(d)
    # #c = polyline_to_bar(a, 100)
    # a = polyline_to_bar(test, 100, planar=True)
    # 测试test内偏移还是外偏移
    # a = offset(test, 100)
    # for i in test:
    #     print i.ClosedCurveOrientation()
    #a = transformOrientation(tests)
    #b = _offset(tests, 100)
