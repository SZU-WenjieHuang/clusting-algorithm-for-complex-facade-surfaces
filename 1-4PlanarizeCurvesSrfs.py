import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
"""Transforms non-planar curves and surfaces into planar cuves or surfaces
using either best-fit plane or current view CPlane. Works best with "near planar"
objects. Non-polyline curves will be "sampled" with 100 points to find best fit
plane, surfaces will be internally meshed and use mesh vertices as sample points.
Option to delete input or not.
Script by Mitch Heynick 17.06.15
Revised 05.11.20
- added possibility to transform surfaces in addition to curves"""
"""
使用最佳拟合平面或当前视图CPlane将非平面曲线和曲面转换为平面曲线或曲面。适用于“近平面”物体。非折线曲线将被“采样”100点，以找到最佳拟合平面，表面将在内部网格和使用网格顶点作为采样点。
选择是否删除输入。
脚本:Mitch Heynick 17.06.15
修订05.11.20
增加了变换曲面和曲线的可能性
"""

"""
定义rhino的输入端
"""
def CommandLineOptions(prompt,msg1,b_opts1,msg2,b_opts2):
    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt(prompt)    
    # set up the options
    boolOption1 = Rhino.Input.Custom.OptionToggle(*b_opts1)
    boolOption2 = Rhino.Input.Custom.OptionToggle(*b_opts2)
    go.AddOptionToggle(msg1, boolOption1)
    go.AddOptionToggle(msg2, boolOption2)
    go.AcceptNothing(True)
    
    #let the user input
    while True:
        get_rc = go.Get()
        if go.CommandResult()== Rhino.Commands.Result.Cancel:
            return
        elif go.CommandResult()== Rhino.Commands.Result.Nothing:
            break
        elif get_rc==Rhino.Input.GetResult.Option:
            continue
        break
    return boolOption1.CurrentValue, boolOption2.CurrentValue

"""
rs库 自己定义一个 bounding box
输入：待优化的物体obj, 对齐的平面plane
输出：box一半高的距离 （底点到上点）
"""
def MaxDeviationInPlane(obj, plane):
    bb = rs.BoundingBox(obj, plane, False)
    if bb: return (bb[0].DistanceTo(bb[4]))*0.5

"""
用surface的参数构建一个mesh,并返回这些mesh的points
输入：surface
输出：Mesh_Points
"""
def GetSurfaceMeshPts(srfID):
    brep=rs.coercebrep(srfID)
    mp=Rhino.Geometry.MeshingParameters.Smooth
    mesh=Rhino.Geometry.Mesh.CreateFromBrep(brep,mp)
    if mesh:
        verts=mesh[0].Vertices
        pts=rs.coerce3dpointlist(verts)
        return pts

"""
用surface的参数构建一个mesh,并返回这些mesh的points
输入：surface
输出：Mesh_Points
"""
def PlanarizeCurvesSrfs():
    #定义到输入端
    sample = 100
    msg="Select near-planar curves or single surfaces to planarize"
    objIDs = rs.GetObjects(msg,4+8,preselect=True)
    if not objIDs: return
    pick_view = rs.CurrentView()
    
    #get previous settings
    if "Planarize_CS_Proj" in sc.sticky: pc_proj = sc.sticky["Planarize_CS_Proj"]
    else: pc_proj = True
    if "Planarize_CS_Del" in sc.sticky: pc_del = sc.sticky["Planarize_CS_Del"]
    else: pc_del = True
    
    #get user input
    prompt="Planarize options:"
    msg1="ProjectionType"
    msg2="DeleteInput"
    opts1=(pc_proj,"ActiveCPlaneParallel", "BestFitPlane")
    opts2=(pc_del,"No","Yes")
    user_opts=CommandLineOptions(prompt,msg1,opts1,msg2,opts2)
    if not user_opts: return
    plane_choice, del_choice=user_opts
    
    #initialize and run
    prec = rs.UnitDistanceDisplayPrecision()
    unit_sys_name = rs.UnitSystemName(False, False, True)
    max_dev = 0.0 ; bad_objs = 0 ; new_objs=[]  
    rs.EnableRedraw(False)
    for objID in objIDs:
        if plane_choice:
            if rs.IsCurve(objID):
                if rs.IsPolyline(objID) :
                    pts = rs.CurvePoints(objID)
                else:
                    #not a polyline, divide curve
                    pts = rs.DivideCurve(objID, sample, False)
            else:
                #surface, mesh surface and get mesh vertices as points
                pts=GetSurfaceMeshPts(objID)
                #surface, get edit points (should be on surface)
                #pts=rs.SurfaceEditPoints(objID)
            #rs.AddPoints(pts) #debug
            if not pts:
                bad_objs+=1
                continue
            bf_plane = rs.PlaneFitFromPoints(pts)
        else:
            bb = rs.BoundingBox(objID, pick_view, False)
            bf_plane = rs.ViewCPlane(pick_view)
            bf_plane.Origin = (bb[0]+bb[6])/2
            
        if bf_plane:
            dev = MaxDeviationInPlane(objID, bf_plane)
            xform = rs.XformPlanarProjection(bf_plane)
            new_obj = rs.TransformObject(objID, xform, not del_choice)
            if new_obj: new_objs.append(new_obj)
            if dev is not None and dev > max_dev: max_dev = dev
        else: bad_objs+=1
    if new_objs: rs.SelectObjects(new_objs)
    
    #reporting
    msg="{} objects planarized - max deviation: ".format(len(objIDs)-bad_objs)
    msg+="{} {}".format(round(max_dev,prec+1),unit_sys_name)
    if bad_objs>0: msg+=" || {} objects unable to be processed".format(bad_objs)
    print msg
    #store options
    sc.sticky["Planarize_CS_Proj"] = plane_choice
    sc.sticky["Planarize_CS_Del"] = del_choice
PlanarizeCurvesSrfs()