"""パラメータ設定"""

HEAD = 1        #HEAD1=1、HEAD2=2
SP = 1          #SP1加工=1、SP2加工=2
POSITION = 20   #ワーク左側端面をz=0.0とした時の右側端面のz位置
MARGIN = 2      #位置決め余裕の距離

THREAD_NAME = 0       #管用平行ねじ=0、管用テーパねじ=1、メートルねじ=2、ユニファイねじ=3、アメリカ管用テーパねじ=4
THREAD_TYPE = 0       #おねじ=0、めねじ=1
OUTER_DIAMETER =15    #おねじ外径、もしくはめねじの谷径
ROOT_DIAMETER = 7.77  #おねじの谷径、もしくはめねじの内径
LENGTH = 20
PITCH = 1

S = 1

VELOCITY = 60
FEED =0.2
AP = 0.05 #片肉切り込み量

import math


class ThreadInsert:
    def __init__(self,s):
        self.s = s  #ホルダ端からチップ刃先までの距離(mm)


class WorkGeometry:
    def __init__(self,outer_diameter,root_diameter,length,pitch,tread_name,thread_type):
        self.outer_diameter = outer_diameter
        self.root_diameter = root_diameter
        self.length = length
        self.pitch = pitch
        self.thread_name = tread_name
        self.thread_type = thread_type

class CuttingCondition:
    def __init__(self,velocity,feed,ap):
        self.outer_rpm = 1000*velocity/(math.pi * WorkGeometry(OUTER_DIAMETER,ROOT_DIAMETER,LENGTH,PITCH,THREAD_NAME,THREAD_TYPE).outer_diameter)
        self.inner_rpm = 1000*velocity/(math.pi * WorkGeometry(OUTER_DIAMETER,ROOT_DIAMETER,LENGTH,PITCH,THREAD_NAME,THREAD_TYPE).root_diameter)
        self.feed = feed
        self.ap = ap

class ThreadProcess:
    def __init__(self,head,sp,margin,position):
        self.cutting_condition = CuttingCondition(VELOCITY,FEED,AP)
        self.work_geometry = WorkGeometry(OUTER_DIAMETER,ROOT_DIAMETER,LENGTH,PITCH,THREAD_NAME,THREAD_TYPE)
        self.head = head
        self.sp = sp
        self.margin = margin
        self.position = position
        

    def tool_select(self):
        program1 = f"N3G10P0Z0\n\
G0G97G99S{int(self.cutting_condition.outer_rpm if self.work_geometry.thread_type==0 else self.cutting_condition.inner_rpm)}\
T303M{93 if self.sp==1 else 193}M{28 if self.head==1 else 128}P{11 if self.sp==1 else 21}\n\
G18\n"
        print(program1)
        
    def positioning(self):
        program2 = f"Z{float(self.position+self.margin if SP==1 else 0.0-margin)}Y0M{91 if SP==1 else 191}\n\
X{float(self.work_geometry.outer_diameter+1.0 if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter-1.0)}\n"
        print(program2)

    def cutting(self):
        total_path=[]
        for n in range(0,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
            total_path.append(f"X{self.work_geometry.outer_diameter - 2*n*self.cutting_condition.ap}\n")
        total_path.append(f"X{self.work_geometry.root_diameter}")
        thread_cycle = "".join(total_path)


        
        program3 = f"G92X{self.work_geometry.outer_diameter if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter}\
Z{self.position-self.work_geometry.length if self.sp==1 else self.work_geometry.length}F{float(self.work_geometry.pitch)}\n\
{thread_cycle}"
        print(program3)


    def returning(self):
        program4 = "G0X100.0\n\
G28U0Y0\n"
        print(program4)

def main():
   thread_process = ThreadProcess(HEAD,SP,MARGIN,POSITION)
   thread_process.tool_select()
   thread_process.positioning()
   thread_process.cutting()
   thread_process.returning()
if __name__ == "__main__":
    main()
