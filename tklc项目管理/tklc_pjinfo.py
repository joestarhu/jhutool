#! /usr/bin/env python3
import pandas as pd
from datetime import datetime,timedelta

EXCEL_PATH = '/Users/jhu/Downloads/tklc.xlsx'
class ExlCfg:
    # Sheet相关
    SHT_PJINF:str       = 'pjinfo'
    SHT_CITYLIST:str    = 'citylist'

    # 列名相关
    COL_STS:str         = '状态'
    COL_KO:str          = '立项'
    COL_DT:str          = 'DT'
    COL_PJTYPE:str      = '项目类型'
    COL_WORKHOUR:str    = '月detail' # 月份需要拼接
    COL_WORKHOUR_TOTAL:str    = '月total' # 月份需要拼接,每个月的总工时

    ## 里程碑需要拼接
    COL_MSPLAN  = '计划'
    COL_MSACT   = '实际'
    COL_MSDELAY = '延期'

    # 初始化的时候自行追加的列，非原始数据
    COL_END_PLAN:str =  '计划完结'
    COL_END_ACT:str  =  '实际完结'

    # 列的可用值
    ## 状态
    STS_DOING   = '进行'
    STS_DELAY   = '延迟'
    STS_WAIT    = '等待'
    STS_DONE    = '完成'
    STS_VAL     = (STS_DOING,STS_DELAY,STS_WAIT,STS_DONE)

    ## 项目类型
    PJTYPE_NORMAL   = '常规'
    PJTYPE_UPGRADE  = '优化'
    PJTYPE_FIX      = '修复'
    PJTYPE_ABORT    = '终止'
    PJTYPE_VAL      = (PJTYPE_NORMAL,PJTYPE_UPGRADE,PJTYPE_FIX,PJTYPE_ABORT)

    ## 里程碑
    MS_PC = 'PC'
    MS_DC = 'DC'
    MS_CC = 'CC'
    MS_TC = 'TC'
    MS_GA = 'GA'
    MS_VAL = (MS_PC,MS_DC,MS_CC,MS_TC,MS_GA)

    # 里程碑进度特殊值
    SCH_UNDEF   = '-'
    SCH_TBD     = 'TBD'
    SCH_TODO    = 'todo'
    SCH_DOING   = 'doing'
    SCH_WAIT    = 'wait'
    SCH_VAL     = (SCH_UNDEF,SCH_TBD,SCH_TODO,SCH_DOING,SCH_WAIT)


class PJinfo:
    def __init__(self,path=EXCEL_PATH):
        # 读取Excel文件信息
        df = pd.read_excel(path,ExlCfg.SHT_PJINF,header=1,usecols='b:ak')

        # 非法状态数据移除
        mask = ~df[ExlCfg.COL_STS].isin(ExlCfg.STS_VAL)
        df.drop(index=df[mask].index,inplace=True)

        # 计划完成日和实际完成日的设定
        for ms in ExlCfg.MS_VAL:
            plan = ms + ExlCfg.COL_MSPLAN
            act = ms + ExlCfg.COL_MSACT
            delay = ms + ExlCfg.COL_MSDELAY

            # 找出非日程的row(即这些日程是尚未确定或完成)
            plmsk  = df[plan].apply(str).isin(ExlCfg.SCH_VAL)
            actmsk = df[act].apply(str).isin(ExlCfg.SCH_VAL)

            # 计算计划完成日
            mask = ~plmsk
            df.loc[mask,ExlCfg.COL_END_PLAN] = df.loc[mask,plan]

            # 里程碑实际完成日设定
            mask = (df[ExlCfg.COL_STS] == ExlCfg.STS_DONE) & (~actmsk)
            df.loc[mask,ExlCfg.COL_END_ACT] = df.loc[mask,act]

        # 格式化日期
        def month_total_get(val):
            hour = 0.
            if pd.isnull(val): return hour
            for data in val.split(' '):
                hour += float(data.split(':')[1])
            return hour

        # 计算各个项目每个月的工时
        for month in range(1,13):
            col_hour = f'{month}{ExlCfg.COL_WORKHOUR}'
            col_total = f'{month}{ExlCfg.COL_WORKHOUR_TOTAL}'
            df[col_total] = df[col_hour].apply(month_total_get)

        self.__df = df

    def pjinfo_get(self):
        return self.__df

    def pjytpe_get(self) ->pd.DataFrame:
        '''获取每月完成项目类型数量'''
        pjtype = pd.DataFrame(None,columns=ExlCfg.PJTYPE_VAL,index=range(1,13))
        pjtype.fillna(0,inplace=True)

        df = self.__df
        mask = df[ExlCfg.COL_STS] == ExlCfg.STS_DONE
        df = df[mask]

        today = datetime.today()
        year = today.year

        for month in range(1,13):
            start = datetime(year,month,1)
            end  = datetime(year,month+1,1) if month < 12 else datetime(year+1,1,1)

            msk = (df[ExlCfg.COL_END_ACT] >= start) & (df[ExlCfg.COL_END_ACT] < end)
            m_df = df[msk]

            for type in ExlCfg.PJTYPE_VAL:
                cnt = m_df[m_df[ExlCfg.COL_PJTYPE] == type].shape[0]
                pjtype.loc[month,type] = cnt
        return pjtype

    def pjhour_get(self) ->dict:
        '''获取每月项目的完成工时'''
        df = self.__df
        pjhour = {}
        for month in range(1,13):
            col_total = f'{month}{ExlCfg.COL_WORKHOUR_TOTAL}'
            pjhour[month] = df[col_total].sum()
        return pjhour

    def pjres_get(self,periods=30,name=None) ->pd.DataFrame:
        '''获取项目资源的使用情况'''
        df = self.__df

        # 清洗出未完成的项目数据
        msk = df[ExlCfg.COL_STS] == ExlCfg.STS_DONE
        df = df[~msk]

        today = datetime.today()
        start = datetime(today.year,today.month,today.day)
        end = start + timedelta(periods)
        pjres = pd.DataFrame(pd.date_range(start,end),columns=['date'])
        pjres.set_index('date',inplace=True)

        # 清洗出在计算时间段内的数据
        msk = (df[ExlCfg.COL_KO] > end) | (df[ExlCfg.COL_END_PLAN] < start)
        df = df[~msk]

        for i in df.index:
            dt = df.loc[i,ExlCfg.COL_DT]
            if pd.isnull(dt):
                continue
            m_list = dt.split(' ')
            pjstart = df.loc[i,ExlCfg.COL_KO]
            pjend =  df.loc[i,ExlCfg.COL_END_PLAN]

            pjperiod = pd.date_range(pjstart,pjend)
            for m in m_list:
                msk = pjres.index.isin(pjperiod)
                if m in pjres.columns:
                    pjres.loc[msk,m] += 1.
                else:
                    pjres.loc[msk,m] = 1.
        pjres.fillna(0,inplace=True)

        if name in pjres.columns:
            pjres = pjres[name]

        pjres = pjres.T
        return pjres

if __name__ == '__main__':
    p = PJinfo()
    p.pjres_get(10)
    p.pjhour_get()

