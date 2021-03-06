#! /usr/bin/env python3
from pjinfo import PJinfo
from zendao import ZenTao

def create_task(xlsx_id,module_id=None):
    p = PJinfo()
    df = p.pjinfo_get()
    pj = df[xlsx_id-3:xlsx_id-2]

    # 开发组成员
    member = pj['DT'].values[0].split(' ')

    # 任务标题
    bus = pj['业务线'].values[0]
    prod = pj["产品"].values[0]
    ver = pj["版本"].values[0]
    title = pj["内容范围简介"].values[0]
    task_name = f'#{prod}{ver}# {title}'


    z = ZenTao('***','****')
    z.task(bus,module_id,task_name,member)


if __name__ == '__main__':
    Excel_id = 11
    Moudle_id = 1239
    #create_task(Excel_id,Moudle_id)
