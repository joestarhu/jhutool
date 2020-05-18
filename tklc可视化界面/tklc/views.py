from tklc import tklc
from flask import render_template
from pyecharts import options as opts
from pyecharts.charts import Bar,Line,Timeline
from pyecharts.globals import ThemeType
from .pjinfo import PJinfo,WorkhourInfo,TestInfo
from .axure import Axure

@tklc.route('/')
def main():
    return render_template('home.html',HTML_TITLE='项目管理数据')

@tklc.route('/axure')
def axure():
    id = 2
    a = Axure(id)
    #print(a.tree)
    content = node_print(a.tree)
    return render_template('axure.html',id=id,content=content)

def node_print(tree,msg=None):
    msg = msg or ''
    msg += '<ul>'
    for node in tree:
        pn = node['pageName']
        url = node['url']
        msg += f'<li class="nav-item"><a>{pn}</a><p id={pn} hidden>{url}</p>'
        if 'children' in node:
            msg += node_print(node['children'])
        msg+='</li>'
    msg += '</ul>'
    return msg


@tklc.route('/testinfo')
def testinfo_get():
    df = TestInfo().df[-12:]

    xdata = df['月份'].tolist()
    ratio = df['通过率'].tolist()

    fig = Line()
    fig.add_xaxis(xdata)
    fig.add_yaxis('一次通过率',ratio)
    fig.set_global_opts(
        title_opts = opts.TitleOpts(title="最近12月测试通过率"),
        yaxis_opts = opts.AxisOpts(name='通过率',type_='value',axislabel_opts=opts.LabelOpts(formatter="{value} %")),
    )
    return fig.dump_options_with_quotes()


@tklc.route('/memberhour')
def member_month_workhour():
    p = PJinfo()
    m = p.member_workhour_get()
    tl = Timeline()

    li_month = sorted(m.keys(),reverse=True)
    for i in li_month:
        month = m[i].sort_values(0,axis=1,ascending=False)
        fig = Bar()
        fig.add_xaxis(month.columns.tolist())
        fig.add_yaxis('投入工时',month.values.flatten().tolist())
        fig.set_global_opts(
            title_opts = opts.TitleOpts(title=f"2020年{i}月人员工时投入"),
            yaxis_opts = opts.AxisOpts(name='工时'),
        )
        tl.add(fig,time_point=f'{i}月')
    return tl.dump_options_with_quotes()


@tklc.route('/workhour')
def workhour_get():
    p = WorkhourInfo()
    # 获取最近的12月
    df = p.df.dropna()[-12:]

    xdata = df['月份'].tolist()
    # fig = Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
    fig = Bar()

    fig.add_xaxis(xdata)
    fig.add_yaxis('总投入',df['实际投入工时'].tolist(),label_opts = opts.LabelOpts(position='inside'))
    for v in df.columns[6:]:
        fig.add_yaxis(v,df[v].tolist(),stack='detail',is_selected = False,label_opts=opts.LabelOpts(is_show=False))

    fig.set_global_opts(
        title_opts = opts.TitleOpts(title="最近12月工时投入"),
        tooltip_opts = opts.TooltipOpts(is_show=True, trigger="axis", axis_pointer_type="shadow"),
        yaxis_opts = opts.AxisOpts(name='工时'),
    )

    #"""
    df['投入总工时比率'] = (df['投入总工时比率']*100).round(0)
    maxratio = df['投入总工时比率'].max()
    maxratio = 100 if maxratio <= 100 else maxratio
    ratio = df['投入总工时比率'].tolist()

    line = Line()
    line.add_xaxis(xdata)
    line.add_yaxis('投入工时率',ratio,yaxis_index=1)

    fig.extend_axis(
        yaxis=opts.AxisOpts(
            name="投入工时率",type_="value",
            min_=0,max_=maxratio,
            axislabel_opts=opts.LabelOpts(formatter="{value} %")
        )
    )
    fig.overlap(line)
    #"""
    return fig.dump_options_with_quotes()
