"""
パラメータ
"""
THREAD_TYPE = 0
SCREW_NAME = "R3/8"
DATABASENAME = "screw_standard"
HEAD = 2    #HEAD1=1、HEAD2=2
SP = 1      #SP1加工=1、SP2加工=2
MARGIN = 2      #位置決め余裕の距離
LENGTH = 50
DIAMETER =10
PITCH = 0.8
S = 1
VELOCITY = 60
FEED =0.2
AP = 0.025 #片肉切り込み量

CUTTING_LENGTH =10


import math
import sqlite3
import pandas as pd


"""設定"""

#抽象
class Setting:
    def __init__(self,head,sp,margin):
        pass
    
#具体  テーパねじと共用
class ThreadSetting(Setting):
    def __init__(self,head,sp,margin,s):
        self.head = head
        self.sp = sp
        self.margin = margin
        self.s = s
        
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
        self.p = 0
        self.d_D = 0
        self.d1_D1 = 0
        
    def search_parameter(self,screw_name):
        conn = sqlite3.connect(self.database_name)
        c = conn.cursor()
        df = pd.read_sql(f"select id,p,d_D,d1_D1 from G where id='{screw_name}'", conn)
        conn.commit()
        conn.close()
        
        self.name = df.at[0,"id"]
        self.p = df.at[0,"p"]
        self.d_D = df.at[0,"d_D"]
        self.d1_D1 = df.at[0,"d1_D1"]
        

#具体
class RStandard(Standard):
    def __init__(self,database_name,thread_type):
        self.database_name = database_name
        self.thread_type = thread_type
        self.name = None
        self.p = 0
        self.d_D = 0
        self.d1_D1 = 0
        self.a = 0
        self.f = 0
        self.l = 0
        self.t = 0

    def search_parameter(self,screw_name):
        conn = sqlite3.connect(self.database_name)
        c = conn.cursor()
        df = pd.read_sql(f"select name,p,d_D,d1_D1,a,f,l,t from R where name='{screw_name}'", conn)
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
class MStandard(Standard):
    def __init__(self,a):
        pass

    def search_parameter(self):
        pass


#具体
class UStandard(Standard):
    def __init__(self,a):
        pass


    def search_parameter(self):
        pass


#具体
class NStandard(Standard):
    def __init__(self,a):
        pass


    def search_parameter(self):
        pass

        
        
        
        
        

""" ワーク """
#抽象
class Work:
    def __init__(self,length,diameter):
        pass
    
#具体
class ThreadWork(Work):
    def __init__(self,length,diameter,standard,cutting_length):
       self.length = length
       self.diameter = diameter

       self.standard = standard
       self.cutting_length = cutting_length


#具体　テーパねじ
class TaperThreadWork(Work):
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
        self.total_path = []
    
   
    def tool_select(self,program):
        self.program1 = f"N3G10P0Z0\n\
G0G97G99S{int(program.cutting_condition.rpm)}\
T303M{93 if program.setting.sp==1 else 193}M{28 if program.setting.head==1 else 128}P{11 if program.setting.sp==1 else 21}\n\
G18\n"
        return self.program1
        
    def positioning(self,program):
        self.program2 = f"Z{float(program.work.length+program.setting.margin if program.setting.sp==1 else -program.setting.margin)}\
{'Y0.0' if program.setting.head==1 else ''}M{91 if program.setting.sp==1 else 191}\n\
X{round(float(program.work.standard.d_D+1.0 if program.work.standard.thread_type==0 else program.work.standard.d1_D1-1.0),3)}\n"
        return self.program2

    def cutting(self,program):
        if program.work.standard.thread_type==0:
            for n in range(1,int((program.work.standard.d_D - program.work.standard.d1_D1)//(2*program.cutting_condition.ap))+1):
                self.total_path.append(f"X{round((program.work.standard.d_D - 2*n*program.cutting_condition.ap),3)}\n")
            self.total_path.append(f"X{round(program.work.standard.d1_D1,3)}")
    
        else:
            for n in range(1,int((program.work.standard.d_D-program.work.standard.d1_D1)//(2*program.cutting_condition.ap))+1):
                self.total_path.append(f"X{round((program.work.standard.d1_D1 + 2*n*program.cutting_condition.ap),3)}\n")
            self.total_path.append(f"X{round(program.work.standard.d_D,3)}")
        thread_cycle = "".join(self.total_path)
       
        self.program3 = f"G92X{float(program.work.standard.d_D if program.work.standard.thread_type==0 else program.work.standard.d1_D1)}\
Z{float(program.work.length-program.work.cutting_length-program.setting.s if program.setting.sp==1 else program.work.length+program.setting.s)}\
F{float(program.work.standard.p)}\n\
{thread_cycle}"
        return self.program3


    def returning(self,program):
        self.program4 = f"G0X100.0\n\
Z{50.0 if program.setting.sp==1 else -50.0}\n\
G28{'U0Y0' if program.setting.head==1 else 'U0'}\n"
        return self.program4
    
    def output_program(self,program):
        print(self.program1)
        print(self.program2)
        print(self.program3)
        print(self.program4)


class TaperThreadProcess(ThreadProcess):
    
    def positioning(self,program):
        male_start_x = program.work.standard.d_D - (program.work.standard.a + program.setting.margin)/16
        female_start_x = program.work.standard.d1_D1+ program.setting.margin/16
       
        self.program2 = f"Z{float(program.work.length+program.setting.margin if program.setting.sp==1 else -program.setting.margin)}\
{'Y0.0' if program.setting.head==1 else ''}M{91 if program.setting.sp==1 else 191}\n\
X{round(float(male_start_x+1.0 if program.work.standard.thread_type==0 else female_start_x-1.0),3)}\n"
        return self.program2


    def cutting(self,program):
        l = program.work.standard.a+program.work.standard.f+program.setting.margin
        h = round(float(0.5*l/16),3)
        male_start_x = program.work.standard.d_D - (program.work.standard.a + program.setting.margin)/16
        male_end_x = male_start_x + 2*h
        female_start_x = program.work.standard.d1_D1+ program.setting.margin/16
        female_end_x = female_start_x - 2*h
        
        if program.work.standard.thread_type==0:
            for n in range(1,int((program.work.standard.d_D - program.work.standard.d1_D1)//(2*program.cutting_condition.ap))+1):
                self.total_path.append(f"X{round((male_end_x - 2*n*program.cutting_condition.ap),3)}\n")
            self.total_path.append(f"X{round(male_end_x-(program.work.standard.d_D - program.work.standard.d1_D1),3)}")
    
        else:
            for n in range(1,int((program.work.standard.d_D-program.work.standard.d1_D1)//(2*program.cutting_condition.ap))+1):
                self.total_path.append(f"X{round((female_end_x + 2*n*program.cutting_condition.ap),3)}\n")
            self.total_path.append(f"X{round(female_end_x+(program.work.standard.d_D-program.work.standard.d1_D1),3)}")
        thread_cycle = "".join(self.total_path)
       
        self.program3 = f"G92X{round(float(male_end_x if program.work.standard.thread_type==0 else female_end_x),3)}\
Z{round(float(program.work.length + program.setting.margin - l if program.setting.sp==1 else -program.work.setting.margin+l),3)}\
R{-h if program.work.standard.thread_type==0 else h }\
F{float(program.work.standard.p)}\n\
{thread_cycle}"
        return self.program3

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



def main():
    if SCREW_NAME[0]=="g":
        setting = ThreadSetting(HEAD,SP,MARGIN,S)   #共通
        standard = GStandard(DATABASENAME,THREAD_TYPE)
        standard.search_parameter(SCREW_NAME)
        work = ThreadWork(LENGTH,DIAMETER,standard,CUTTING_LENGTH)
        cutting_condition = ThreadCuttingCondition(work,VELOCITY,FEED,AP)
            
       
        thread_program = Program(setting,work,cutting_condition,ThreadProcess())
        thread_program.tool_select()
        thread_program.positioning()
        thread_program.cutting()
        thread_program.returning()
        thread_program.output_program()

    elif SCREW_NAME[0]=="R":
        setting = ThreadSetting(HEAD,SP,MARGIN,S)   #共通
        standard = RStandard(DATABASENAME,THREAD_TYPE)
        standard.search_parameter(SCREW_NAME)
        work = TaperThreadWork(LENGTH,DIAMETER,standard)
        cutting_condition = ThreadCuttingCondition(work,VELOCITY,FEED,AP)
            
        thread_program = Program(setting,work,cutting_condition,TaperThreadProcess())
        thread_program.tool_select()
        thread_program.positioning()
        thread_program.cutting()
        thread_program.returning()
        thread_program.output_program()


if __name__ == "__main__":
    main()
