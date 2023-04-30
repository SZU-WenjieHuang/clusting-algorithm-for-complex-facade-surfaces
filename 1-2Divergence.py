from Rhino.Geometry import EdgeAdjacency, Plane, Point, Surface
#from DAR_geometry_tools import dis_ptToCrv
from rhinoscript.curve import CurveMidPoint
from rhinoscript.surface import SurfaceSphere
from rhinoscript.utility import Distance
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import math


# Class01:得到每个面板与面板之间的 Divergence / SurfaceFitting
# input：Surface：Plane Surfaces
# output：List：每个 plane surface 和周围 plane surface 的平均 Divergence

class Get_Divergence:
    def __init__(self,Surfaces,TrueSurface,SingleSurface,DivergenceThershold,U,V):
        self.Plane_Surface = Surfaces #传入的平板曲面
        self.True_Surface = TrueSurface #传入的真实曲面
        self.U_division = int(U) #垂直划分的数量
        self.V_division = int(V) #水平划分的数量
        self.DivergenceThershold = DivergenceThershold #边界的阈值
        self.Single_Surface = SingleSurface #单曲面
 

    # def 1-1：定义边界的Plane数值
    # input：U，V
    # output: 边界的list

    def EdgeNumber(self):
        EdgeNumber = []
        for i in range (int(self.U_division)):
            EdgeN = i*int(self.V_division)
            EdgeNumber.append(EdgeN)
        return EdgeNumber

    # def 1-2：求每个plane周围的Plane
    # input：planes
    # output: list[[1,2,3],[1,2,3]...]

    def Get_Div(self):
        PlaneRound = []
        for i in range(len(self.Plane_Surface)):
            iRound = []
            Plane_i = self.Plane_Surface[i]
            # 下面的Plane
            if i >= self.V_division and i-self.V_division <= len(self.Plane_Surface)-1:
                iRound.append(i-self.V_division)
            # 上面的Plane
            if len(self.Plane_Surface) - i >= self.V_division and i+self.V_division <= len(self.Plane_Surface)-1 :
                iRound.append(i+self.V_division)
            # 右边的Plane
            if i in self.EdgeNumber() and i-1+self.V_division <= len(self.Plane_Surface)-1 :
                iRound.append(i-1+self.V_division)
            elif i-1 <= len(self.Plane_Surface)-1:
                iRound.append(i-1)
            # 左边的Plane
            if i+1 in self.EdgeNumber() and i+1-self.V_division <= len(self.Plane_Surface)-1 :
                iRound.append(i+1-self.V_division)
            elif i+1 <= len(self.Plane_Surface)-1:
                iRound.append(i+1)
            PlaneRound.append(iRound)
        return PlaneRound

    # def 1-3：求两条线的距离
    # input：curveA CurveB
    # output: Distance

    def CurveDistance(self,Curve1,Curve2):
        Point1 = CurveMidPoint(Curve1)
        Point2 = CurveMidPoint(Curve2)
        Dis = Distance(Point1,Point2)
        return Dis

    # def 1-4：求divergence
    # input：PlaneA PlaneB
    # output: divergence

    def EdgeNumber(self,PlaneA,PlaneB):
        Surface_id = PlaneA
        brep1 = rs.coercebrep(Surface_id)
        brep2 = rs.coercebrep(PlaneB)
        divergence = []
        for i in range(4):
            Edge1 = brep1.Edges[i]
            Edge2 = brep2.Edges[i]
            dis = self.CurveDistance(Edge1,Edge2)
            divergence.append(dis)
        AveDivergence = sum(divergence)/len(divergence)
        return AveDivergence
 
    # def 1-5：求divergence的平均值
    # input：U，V
    # output: 边界的list

    def DivergenceList(self,SurfaceA,SurfaceB):
        DiverageL = []
        for i in range(len(self.Plane_Surface)):
            div = self.EdgeNumber(SurfaceA[i],SurfaceB[i])  
            DiverageL.append(div)
        return DiverageL
    
    # def 1-6：求SurfaceFitting()
    # input：PlaneA PlaneB
    # output: SurfaceFitting

    def SurfaceFitting(self,PlaneA,PlaneB):
        SurfaceFitting = []
        for i in range(len(self.Plane_Surface)):
            brep1 = rs.coercebrep(PlaneA[i])
            brep2 = rs.coercebrep(PlaneB[i])
            Face1 = brep1.Faces[0]
            Face2 = brep2.Faces[0]
            c1 = rs.SurfaceAreaCentroid(Face1)[0]
            c2 = rs.SurfaceAreaCentroid(Face2)[0]
            print(type(c1))
            print(c1)
            dis = Distance(c1,c2)
            SurfaceFitting.append(dis)
        return SurfaceFitting

    # def 1-7：筛选出Divergence过大的Panels并且替换
    # input：U，V
    # output: 边界的list

    def ToPanels(self):
        Panels1 = [] #平板
        Panels2 = [] #双曲
        Panels3 = [] #单曲
        List_D1 = self.DivergenceList(self.Plane_Surface,self.True_Surface)
        List_D2 = self.DivergenceList(self.Single_Surface,self.True_Surface)
        #List_F1 = self.SurfaceFitting(self.Plane_Surface,self.True_Surface)
        #List_F2 = self.SurfaceFitting(self.Single_Surface,self.True_Surface)

        for i in range(len(self.Plane_Surface)):
            #Cost1 = List_D1[i] + List_F1[i]
            #Cost2 = List_D2[i] + List_F2[i]
            if List_D1[i] < self.DivergenceThershold:
                  Panels1.append(self.Plane_Surface[i])
            elif List_D2[i]/200 < self.DivergenceThershold:
                  Panels3.append(self.Single_Surface[i])
            else:
                print("D2",List_D2[i])
                print("D1",List_D1[i])
                Panels2.append(self.True_Surface[i])
        return Panels1,Panels2,Panels3   


if __name__=='__main__':
    GetD = Get_Divergence(Surfaces,TrueSurface,SingleSurface,DivergenceThershold,U,V)    
    #a = GetD.EdgeNumber()
    #b = GetD.Get_Div()
    c = GetD.ToPanels()[0]
    d = GetD.ToPanels()[1]
    e = GetD.ToPanels()[2]
