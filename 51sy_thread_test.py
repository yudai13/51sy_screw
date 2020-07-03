"""
パラメータ
"""
THREAD_TYPE = 1
SCREW_NAME = "R1/8"
DATABASENAME = "screw_standard"
HEAD = 1    #HEAD1=1、HEAD2=2
SP = 1      #SP1加工=1、SP2加工=2
MARGIN = 2      #位置決め余裕の距離
LENGTH = 10
DIAMETER =10
PITCH = 0.8
S = 1
VELOCITY = 60
FEED =0.2
AP = 0.025 #片肉切り込み量




import math
import sqlite3
import pandas as pd


"""設定"""

#抽象
class Setting:
    def __init__(self,head,sp,margin):
        pass
    
#具体
class ThreadSetting(Setting):
    def __init__(self,head,sp,margin):
        self.head = head
        self.sp = sp
        self.margin = margin
        
"""ねじ規格"""
#抽象
class Standard:
    def __init(self):
        pass

    def search_parameter():
        pass

#具体
class GStandard(Standard):
    def __init__(self,database_name,thread_type):
        self.database_name = database_name
        self.thread_type = thread_type
        self.name = None
        self.p = None
        self.d_D = None
        self.d1_D1 = None
        self.a = None
        self.f = None
        self.l = None
        self.t = None

    def search_parameter(self,screw_name):
        conn = sqlite3.connect(self.database_name)
        c = conn.cursor()
        df = pd.read_sql(f"select name,p,d_D,d1_D1,a,f,l,t from G where name={screw_name}", conn)
        conn.commit()
        conn.close()
        
        self.name = df.at[0,"name"]
        self.p = df.at[0,"p"]
        self.d_D = df.at[0,"d_D"]
        self.d1_D1 = df.at[0,"d1_D1"]
        self.a = df.at[0,"a"]
        self.f = df.at[0,"f"]
        self.l = df.at[0,"l"]
        self.t = df.at[0,"t"]

#具体
class RStandard(Standard):
    def __init__(self,a):
        pass

    def search_standard(self):
        pass

#具体
class MStandard(Standard):
    def __init__(self,a):
        pass

    def search_standard(self):
        pass


#具体
class UStandard(Standard):
    def __init__(self,a):
        pass


    def search_standard(self):
        pass


#具体
class NStandard(Standard):
    def __init__(self,a):
        pass


    def search_standard(self):
        pass

        
        
        
        
        

""" ワーク """
#抽象
class Work:
    def __init__(self,length,diameter):
        pass
    
#具体
class ThreadWork(Work):
    def __init__(self,length,diameter,standard):
       self.length = length
       self.diameter = diameter

       self.standard = standard
        


"""切削条件"""
#抽象
class CuttingCondition:
    def __init__(self,work,velocity,feed,ap):
        pass

class ThreadCuttingCondition(CuttingCondition):
    def __init__(self,work,velocity,feed,ap):
        self.work = work
        self.rpm = 1000*velocity/(math.pi * work.diameter)
        self.ap = ap
    

"""加工工程"""
# プログラムの出力を抽象化したクラス(抽象戦略)
class Process:
    def __init__(self):
        pass

    def tool_select(self):
        pass

    def positioning(self):
        pass

    def cutting(self):
        pass

    def returning(self):
        pass
    
    def output_program(self):
        raise 'Called abstract method !!'



#具体戦略
class ThreadProcess(Process):
    def __init__(self):
        self.program1 = None
        self.program2 = None
        self.program3 = None
        self.program4 = None
    
   
    def tool_select(self,program):
        self.program1 = f"N3G10P0Z0\n\
G0G97G99S{int(program.cutting_condition.rpm)}\
T303M{93 if program.setting.sp==1 else 193}M{28 if program.setting.head==1 else 128}P{11 if program.setting.sp==1 else 21}\n\
G18\n"
        return self.program1
        
    def positioning(self,program):
        program2 = f"Z{float(program.work.length+program.setting.margin if program.setting.sp==1 else -program.setting.margin)}\
{'Y0.0' if program.setting.head==1 else ''}M{91 if program.setting.sp==1 else 191}\n\
X{float(program.work.diameter+1.0 if program.work.standard.thread_type==0 else program.work.diameter-1.0)}\n"
        return self.program2

    def cutting(self,program):
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

        self.program3 = f"G92X{float(self.work_geometry.outer_diameter if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter)}\
Z{float(self.position-self.work_geometry.length-self.thread_insert.s if self.sp==1 else self.work_geometry.length+self.thread_insert.s)}F{float(self.work_geometry.pitch)}\n\
{thread_cycle}"
        return self.program3


    def returning(self,program):
        self.program4 = f"G0X100.0\n\
Z{50.0 if self.sp==1 else -50.0}\n\
G28{'U0Y0' if self.head==1 else 'U0'}\n"
        return self.program4
    
    def output_program(self,program):
        print(self.program1)
        print(self.program2)
        print(self.program3)
        print(self.program4)




#NCプログラムを表す(コンテキスト)
class Program:
    def __init__(self,setting,work,cutting_condition,process):
        self.setting = setting
        self.work = work
        self.cutting_condition = cutting_condition
        self.process = process

    def tool_select(self):
        self.process.tool_select(self)

    def positioning(self):
        self.process.positioning(self)

    def cutting(self):
        self.process.cutting(self)

    def returning(self):
        self.process.returning(self)

    def output_program(self):
        self.process.output_program(self)


        
"""
class CuttingCondition:
    def __init__(self,velocity,feed,ap,outer_diameter,inner_diameter):
        self.work_geometry = WorkGeometry
        self.rpm = 1000*velocity/(math.pi * outer_diameter) if selfwork_geometry.thread_type==0 else 1000*velocity/(math.pi * inner_diameter)
        self.feed = feed
        self.ap = ap
                                  
class ThreadProcess(object):
    def __init__(self,thread_insert,cutting_condition,work_geometry,head,sp,margin):
        self.thread_insert = thread_insert
        self.cutting_condition = cutting_condition
        self.work_geometry = work_geometry
        self.head = head
        self.sp = sp
        self.margin = margin
        

    def tool_select(self):
        program1 = f"N3G10P0Z0\n\
G0G97G99S{int(self.cutting_condition.outer_rpm if self.work_geometry.thread_type==0 else self.cutting_condition.inner_rpm)}\
T303M{93 if self.sp==1 else 193}M{28 if self.head==1 else 128}P{11 if self.sp==1 else 21}\n\
G18\n"
        print(program1)
        
    def positioning(self):
        program2 = f"Z{float(self.position+self.margin if SP==1 else 0.0-self.margin)}{'Y0.0' if self.head==1 else ''}M{91 if SP==1 else 191}\n\
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
    def __init__(self):
        super().__init__(ThreadInsert(S),CuttingCondition(VELOCITY,FEED,AP,DIAMETER),work_geometry,HEAD,SP,MARGIN,POSITION)
        self.l = self.work_geometry.standard_length + self.work_geometry.effective_thread_length + self.margin
        self.h = 0.5* self.l/16
        self.a_x = self.work_geometry.outer_diameter if self.work_geometry.thread_type==0 else self.work_geometry.root_diameter
        self.a_z = self.position - self.work_geometry.standard_length if self.work_geometry.thread_type==0 else self.position - self.work_geometry.standard_length
        self.start_x = self.work_geometry.outer_diameter-(self.work_geometry.standard_length + self.margin)/16 if self.work_geometry.thread_type==0 \
                  else self.work_geometry.root_diameter + (self.work_geometry.standard_length + self.margin)/16
        self.start_z = self.position + self.margin if self.sp==1 else -self.margin
        self.end_x = self.start_x+self.h if self.work_geometry.thread_type==0 else self.start_x-self.h
        self.end_z = self.start_z-self.l if self.sp==1 else self.start_z+self.l
        self.total_path=[]

        
    def positioning(self):
        program2 = f"Z{float(self.position+self.margin if SP==1 else 0.0-self.margin)}{'Y0.0' if self.head==1 else ''}M{91 if SP==1 else 191}\n\
X{float(self.start_x+1.0 if self.work_geometry.thread_type==0 else self.start_x-1.0)}\n"
        print(program2)
        
    def cutting(self):
        
        
        if self.work_geometry.thread_type==0:   #おねじの場合
            for n in range(1,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
                self.total_path.append(f"X{round((self.start_x - 2*n*self.cutting_condition.ap),3)}\n")
            self.total_path.append(f"X{round(self.start_x-(self.work_geometry.outer_diameter-self.work_geometry.root_diameter),3)}")
    
        else:    #めねじの場合    
            for n in range(1,int((self.work_geometry.outer_diameter-self.work_geometry.root_diameter)//(2*self.cutting_condition.ap))+1):
                self.total_path.append(f"X{round((self.start_x + 2*n*self.cutting_condition.ap),3)}\n")
            self.total_path.append(f"X{round(self.start_x+(self.work_geometry.outer_diameter-self.work_geometry.root_diameter),3)}")
        thread_cycle = "".join(self.total_path)

        program3 = f"G92X{float(self.start_x)}\
Z{float(self.end_z)}\
R{-self.h if self.work_geometry.thread_type==0 else self.h}F{float(self.work_geometry.pitch)}\n\
{thread_cycle}"
        print(program3)

"""
def main():
    setting = ThreadSetting(HEAD,SP,MARGIN)
    standard = GStandard(DATABASENAME,THREAD_TYPE)
    work = ThreadWork(LENGTH,DIAMETER,standard)
    cutting_condition = ThreadCuttingCondition(work,VELOCITY,FEED,AP)
    
    thread_program = Program(setting,work,cutting_condition,ThreadProcess())
    thread_program.tool_select()
    thread_program.positioning()
    thread_program.cutting()
    thread_program.returning()
    thread_program.output_program()

    """
    screw_standard = ScrewStandard(THREAD_TYPE)
    screw_standard.search_parameter(DATABASE_NAME,SCREW_NUMB,SCREW_NAME)
    print(screw_standard.p)

    
    work_geometry = WorkGeometry(LENGTH,THREAD_NAME,THREAD_TYPE)
    p=work_geometry.screw_standard.p
    print(p)
    if THREAD_NAME == 1:
        thread_process = TaperThreadProcess()
    else:
        thread_process = ThreadProcess(HEAD,SP,MARGIN,POSITION)
    thread_process.tool_select()
    thread_process.positioning()
    thread_process.cutting()
    thread_process.returning()
"""   
if __name__ == "__main__":
    main()
