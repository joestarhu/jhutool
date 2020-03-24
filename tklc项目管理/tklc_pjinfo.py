"""
Author:Jian.Hu

--2020.03.24-------------------------------------------------
1) 初始化数据的时候,追加每个项目的总工时
"""

#! /usr/bin/env python3
import pandas as pd
from datetime import datetime,timedelta

EXCEL_PATH = '/Users/jhu/Downloads/tklc.xlsx'
class ExlCfg:
    # Sheet相关
    SHT_PJINF:str       = 'pjinfo'
    SHT_CITYLIST:str    = 'citylist'

    # 列名和其可用值
    COL_STS:str = '状态'
    STS_DOING   = '进行'
    STS_DELAY   = '延迟'
    STS_WAIT    = '等待'
    STS_DONE    = '完成'
    STS_VAL     = (STS_DOING,STS_DELAY,STS_WAIT,STS_DONE)

    COL_BUS:str     = '业务线'
    BUS_QR:str      = '扫码业务'
    BUS_OPE:str     = '运营业务'
    BUS_TEMP:str    = '临时需求'
    BUS_VAL         = (BUS_QR,BUS_OPE,BUS_TEMP)

    COL_KO:str          = '立项'
    COL_DT:str          = 'DT'

    COL_PJTYPE:str  = '项目类型'
    PJTYPE_NORMAL   = '常规'
    PJTYPE_UPGRADE  = '优化'
    PJTYPE_FIX      = '修复'
    PJTYPE_ABORT    = '终止'
    PJTYPE_VAL      = (PJTYPE_NORMAL,PJTYPE_UPGRADE,PJTYPE_FIX,PJTYPE_ABORT)

    COL_WORKHOUR        :str = '月detail' # 月份需要拼接
    COL_WORKHOUR_TOTAL  :str = '月total' # 月份需要拼接,每个月的总工时
    COL_WORKHOUR_ALL    :str ='总工时' # 项目总工时

    ## 里程碑需要拼接
    COL_MSPLAN  = '计划'
    COL_MSACT   = '实际'
    COL_MSDELAY = '延期'

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

    # 初始化的时候自行追加的列，非原始数据
    COL_END_PLAN:str =  '计划完结'
    COL_END_ACT:str  =  '实际完结'

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

        # 计算各项目每月的工时和项目总工时
        df[ExlCfg.COL_WORKHOUR_ALL] = 0.
        for month in range(1,13):
            col_hour = f'{month}{ExlCfg.COL_WORKHOUR}'
            col_total = f'{month}{ExlCfg.COL_WORKHOUR_TOTAL}'
            df[col_total] = df[col_hour].apply(month_total_get)
            df[ExlCfg.COL_WORKHOUR_ALL] += df[col_total]

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

    def pjhour_get(self) -> pd.DataFrame:
        """
        获取每个月项目的完成工时间
        输出结果如下:
        月份 扫码业务    运营业务    临时需求    合计
        ----------------------------------------
        1:  1000       2000       3000      6000
        ...
        12: 1000       2000       3000      6000
        """
        # 构建列
        df = self.__df
        col_list = ['月份','合计']
        col_list.extend(ExlCfg.BUS_VAL)

        # 初始化数据
        df_pjhour = pd.DataFrame(columns=col_list)
        df_pjhour['月份'] = range(1,13)
        df_pjhour = df_pjhour.fillna(0.)

        # 获取各个业务线的mask
        mask_bus = [df[ExlCfg.COL_BUS] == val for val in ExlCfg.BUS_VAL]

        # 填充数据
        for i in range(len(mask_bus)):
            for m in range(1,13):
                df_pjhour.loc[m-1,ExlCfg.BUS_VAL[i]] = df.loc[mask_bus[i],f'{m}月total'].sum()

        # 合计数值
        for val in ExlCfg.BUS_VAL:
            df_pjhour['合计'] += df_pjhour[val]

        return df_pjhour

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
    info = p.pjinfo_get()
    df = p.pjhour_get()
