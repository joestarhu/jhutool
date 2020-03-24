# 背景
现有一个Excel文件管理着所有的报表信息，每张报表信息都以sheet页面来展示，同时又有一个总体的sheet页

可快速一览所有的报表文件.

这样的形式存在以下几个缺点：
- 维护不易

	所有的信息在一个文件中，多人要同时维护的时候会产生冲突，只能等一个人维护完成后，另一个人才能维护

- 文件构造复杂

	各个信息内容以sheet方式来维护，后期信息量变大，sheet页就越多，查看十分不容易

# 解决方案
基于上述的缺点，进行如下的改造：

将sheet页移出来，单独做成一个Excel，同时根据分类，放到不同的文件夹下。

原有文件只统一管理信息，大致构造如下：
![文件夹结构](https://github.com/cantahu/cantahu.github.io/blob/master/pic/20170524-1.png?raw=true)

其中Total文件记录所有信息，并且使它通过一个宏能够自动的获取子文件夹中的Excel文件和内容(即分类A，分类B，分类C目录中的文件A，文件B等等内容)

# 代码实现

简单的步骤如下：
1. 获取当前文件夹下所有子文件中的文件名和其内容
2. 将步骤1获取到的数据自动填充到Excel的单元格中
3. 单元格涉及的内容有:
	- Report ID
	- Report Name
	- Report Dept
	- Report Description
	
其中ReportID需要用超链接到相关文件

整体全局代码如下：

```VBA
'Auto Get Report Information
'Creator:Jian.Hu
'Date：2017-05-19


Dim arr_directory(100) As String    'Directory
Dim g_direct_index As Integer

Dim g_cnt As Integer
Dim arr_report_id(500) As String    'Report ID
Dim arr_report_name(500) As String  'Report Name
Dim arr_report_dept(500) As String  'Report Dept
Dim arr_report_desc(500) As String  'Report Description
Dim arr_report_link(500) As String  'Report Link

Dim g_path As String

'入口函数
Sub GetInfo()
Dim mydir As String
Dim mypath As String
'Dim cnt

g_path = ThisWorkbook.Path & "\"

'获取当前路径
mypath = g_path

'获取当前路径下文件夹
mydir = Dir(mypath, vbDirectory)

g_cnt = 0
g_direct_index = 0
Do While mydir <> ""
    '首先跳过.和..
    If mydir <> "." And mydir <> ".." Then
        If (GetAttr(mypath & mydir) And vbDirectory) = vbDirectory Then
         arr_directory(g_direct_index) = mypath & mydir & "\"
         g_direct_index = g_direct_index + 1
        End If
    End If
    mydir = Dir
  Loop
  
  
  For i = 0 To g_direct_index - 1
    GetReportInfo (arr_directory(i))
  Next
  
  Call FillContent
End Sub
Sub GetReportInfo(v_path)
Dim m_file As String
Dim path_len As Integer
Dim temp As String
Dim f_type As String

path_len = Len(g_path)

m_file = Dir(v_path, vbDirectory)
Do While m_file <> ""
    '首先跳过.和..
    If m_file <> "." And m_file <> ".." Then
        '不是文件夹的文件
        If (GetAttr(v_path & m_file) And vbDirectory) <> vbDirectory Then
            '非Excel文件不读取
            temp = InStrRev(m_file, ".")
            f_type = Right(m_file, Len(m_file) - temp)
            If f_type = "xls" Or f_type = "xlsx" Then
            '获取其ID
            arr_report_id(g_cnt) = GetFileName(m_file)
            '获取超链接
            tmp_len = Len(v_path & m_file) - path_len
            arr_report_link(g_cnt) = Right(v_path & m_file, tmp_len)
            '打开文件,获取其内容信息
            GetReportDetailInfo (v_path & m_file)
            '一张报表操作完毕
            g_cnt = g_cnt + 1
            End If
        End If
    End If
    m_file = Dir
    
Loop
End Sub

Sub GetReportDetailInfo(v_path)
Dim wb As Workbook
Set wb = GetObject(v_path)
arr_report_name(g_cnt) = wb.Sheets(1).Cells(5, 7)
arr_report_dept(g_cnt) = wb.Sheets(1).Cells(6, 7)
arr_report_desc(g_cnt) = wb.Sheets(1).Cells(11, 7)
wb.Close
End Sub


Sub FillContent()

Set sht = ActiveWorkbook.Sheets(1)
sht.Cells.Clear

Cells(1, 1) = "报表ID"
Cells(1, 2) = "报表名称"
Cells(1, 3) = "报表描述"
Cells(1, 4) = "报表模块"

For i = 0 To g_cnt - 1
    '编号
    Cells(2 + i, 1) = arr_report_id(i)
    '超链接
    sht.Hyperlinks.Add anchor:=sht.Cells(2 + i, 1), Address:=arr_report_link(i)
    '名称
    Cells(2 + i, 2) = arr_report_name(i)
    '内容
    Cells(2 + i, 3) = arr_report_desc(i)
    '模块
    Cells(2 + i, 4) = arr_report_dept(i)
    
Next
End Sub

Function GetFileName(v_name) '获取文件名
    GetFileName = Left(v_name, InStr(1, v_name, ".") - 1)
End Function


```
