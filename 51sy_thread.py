"""パラメータ設定"""

HEAD = 1        #HEAD1=1、HEAD2=2
SP = 1          #SP1加工=1、SP2加工=2
POSITION = 20   #ワーク左側端面をz=0.0とした時の右側端面のz位置
MARGIN = 2      #位置決め余裕の距離

THREAD_NAME = 1       #管用平行ねじ=0、管用テーパねじ=1、メートルねじ=2、ユニファイねじ=3、アメリカ管用テーパねじ=4
THREAD_TYPE = 1       #おねじ=0、めねじ=1
OUTER_DIAMETER =15    #おねじ外径、もしくはめねじの谷径
ROOT_DIAMETER = 7.77  #おねじの谷径、もしくはめねじの内径
LENGTH = 10
PITCH = 0.8

S = 1

VELOCITY = 60
FEED =0.2
AP = 0.025 #片肉切り込み量

STANDARD_LENGTH = 4
EFFECTIVE_THREAD_LENGTH = 2.5

import math


class ThreadInsert:
    def __init__(self,s):
        self.s = s  #ホルダ端からチップ刃先までの距離(mm)


class WorkGeometry:
    def __init__(self,outer_diameter,root_diameter,length,pitch,tread_name,thread_type,standard_length,effective_thread_length):
        self.outer_diameter = outer_diameter
        self.root_diameter = root_diameter
        self.length = length
        self.pitch = pitch
        self.thread_name = tread_name
        self.thread_type = thread_type
        self.standard_length = standard_length
        self.effective_thread_length = effective_thread_length

class CuttingCondition:
    def __init__(self,velocity,feed,ap):
        self.outer_rpm = 1000*velocity/(math.pi * WorkGeometry(OUTER_DIAMETER,ROOT_DIAMETER,LENGTH,PITCH,THREAD_NAME,THREAD_TYPE,STANDARD_LENGTH,EFFECTIVE_THREAD_LENGTH).outer_diameter)
        self.inner_rpm = 1000*velocity/(math.pi * WorkGeometry(OUTER_DIAMETER,ROOT_DIAMETER,LENGTH,PITCH,THREAD_NAME,THREAD_TYPE,STANDARD_LENGTH,EFFECTIVE_THREAD_LENGTH).root_diameter)
        self.feed = feed
        self.ap = ap

class ThreadProcess:
    def __init__(self,head,sp,margin,position):
        self.thread_insert = ThreadInsert(S)
        self.cutting_condition = CuttingCondition(VELOCITY,FEED,AP)
        self.work_geometry = WorkGeometry(OUTER_DIAMETER,ROOT_DIAMETER,LENGTH,PITCH,THREAD_NAME,THREAD_TYPE,STANDARD_LENGTH,EFFECTIVE_THREAD_LENGTH)
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
        program2 = f"Z{float(self.position+self.margin if SP==1 else 0.0-self.margin)}Y0M{91 if SP==1 else 191}\n\
X{float(self.work_geometry.outer_diameter+1.0 if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter-1.0)}\n"
        print(program2)

    def cutting(self):
        total_path=[]
        if self.work_geometry.thread_type==0:
            for n in range(1,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
                total_path.append(f"X{round((self.work_geometry.outer_diameter - 2*n*self.cutting_condition.ap),3)}\n")
            total_path.append(f"X{round(self.work_geometry.root_diameter,3)}")
    
        else:
            for n in range(1,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
                total_path.append(f"X{round((self.work_geometry.root_diameter + 2*n*self.cutting_condition.ap),3)}\n")
            total_path.append(f"X{round(self.work_geometry.outer_diameter,3)}")
        thread_cycle = "".join(total_path)

        program3 = f"G92X{float(self.work_geometry.outer_diameter if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter)}\
Z{float(self.position-self.work_geometry.length-self.thread_insert.s if self.sp==1 else self.work_geometry.length+self.thread_insert.s)}F{float(self.work_geometry.pitch)}\n\
{thread_cycle}"
        print(program3)


    def returning(self):
        program4 = f"G0X100.0\n\
Z{50.0 if self.sp==1 else -50.0}\n\
G28{'U0Y0' if self.head==1 else 'U0'}\n"
        print(program4)


class TaperThreadProcess(ThreadProcess):
    def cutting(self):

        l = self.work_geometry.standard_length + self.work_geometry.effective_thread_length + self.margin + self.thread_insert.s
        h = 0.5*l/16
        a_x = self.work_geometry.outer_diameter
        a_z = self.position - self.work_geometry.standard_length
        start_x =self.work_geometry.outer_diameter - (self.position + self.margin)/16
        start_z = self.position + self.margin
        total_path=[]
        if self.work_geometry.thread_type==0:
            for n in range(1,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
                total_path.append(f"X{round((self.work_geometry.outer_diameter - 2*n*self.cutting_condition.ap),3)}\n")
            total_path.append(f"X{round(self.work_geometry.root_diameter,3)}")
    
        else:
            for n in range(1,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
                total_path.append(f"X{round((self.work_geometry.root_diameter + 2*n*self.cutting_condition.ap),3)}\n")
            total_path.append(f"X{round(self.work_geometry.outer_diameter,3)}")
        thread_cycle = "".join(total_path)

        program3 = f"G92X{float(self.work_geometry.outer_diameter if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter)}\
Z{float(self.position-self.work_geometry.length-self.thread_insert.s if self.sp==1 else self.work_geometry.length+self.thread_insert.s)}\
R{}FFFFF{float(self.work_geometry.pitch)}\n\
{thread_cycle}"
        print(program3)


def main():
    if THREAD_NAME == 1:
        thread_process = TaperThreadProcess(HEAD,SP,MARGIN,POSITION)
    else:
        thread_process = ThreadProcess(HEAD,SP,MARGIN,POSITION)
    thread_process.tool_select()
    thread_process.positioning()
    thread_process.cutting()
    thread_process.returning()
   
if __name__ == "__main__":
    main()
