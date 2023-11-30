#!/usr/bin/env python3

"""
作者:J.Hu
日期:2023-10-17
内容:
> 修复更新了在win操作系统下不能运行的原因,主要是因为.exe后缀带来的文件匹配不到的原因,同时将无用的zip文件和文件夹目录删除
> 追加了针对115版本以上chrome的驱动下载,请确保网络能够访问 https://googlechromelabs.github.io/chrome-for-testing/
> 追加了experimental_option的初始化设定,运行自定义参数,默认加入不会自动关闭浏览器操作.
> 针对新版本selenum4.X进行了部分方法的更新,支持By多类型的ActionInfo
> 自动分析系统并下载匹配最新的驱动,免除了手动下载匹配驱动
> 抽象化部分操作,通过简单的结构化配置即可实现脚本运行
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from requests import session
from shutil import move as sh_move
import json
import zipfile
import os
import platform

# 淘宝镜像谷歌浏览器驱动下载地址(115版本之前的)
DRIVER_URL = 'https://registry.npmmirror.com/-/binary/chromedriver/'

# 115版本及以后用此链接进行下载
DRIVER_URL_115_PREFIX = 'https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/'
DRIVER_URL_115 = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'


def get_driver_name(plat_sys: str) -> str:
    """获取浏览器下载驱动地址
    Parameters:
        plat_sys: 系统名称
    Returns:
        驱动地址
    """
    if plat_sys == 'Darwin':
        return 'chromedriver'
    elif plat_sys == 'Linux':
        return 'chromedriver'
    else:
        return 'chromedriver.exe'


def get_chromedriver_type(plat_sys: str, plat_machine: str, plat_bits: str, idx: int) -> str:
    """根据系统类型获取下载驱动
    Parameters:
        plat_sys: 系统名称
        plat_machine: 系统架构
        plat_bits: 系统位数
        idx: 0代表使用115之前的版本,1代表使用115之后的版本
    Returns:
        下载驱动的zip名称
    """
    # 下载文件名(第一个为115之前的,第二个为115版本及以后得.)
    mac_x64 = ['chromedriver_mac64.zip', 'mac-x64/chromedriver-mac-x64.zip']
    mac_arm64 = ['chromedriver_mac64_m1.zip', 'mac-arm64/chrome-mac-arm64.zip']
    linux64 = ['chromedriver_linux64.zip', 'linux64/chromedriver-linux64.zip']
    win32 = ['chromedriver_win32.zip', 'win32/chromedriver-win32.zip']
    win64 = ['chromedriver_win32.zip', 'win64/chromedriver-win64.zip']

    if plat_sys == 'Darwin':
        return mac_x64[idx] if plat_machine == 'x86_64' else mac_arm64[idx]
    elif plat_sys == 'Linux':
        return linux64[idx]
    else:
        return win32[idx] if plat_bits == '32bit' else win64[idx]


def get_chromedriver_list(idx: int = 0) -> list:
    """获取谷歌驱动的下载链接
    Parameters:
        idx: 0代表使用115之前的版本,1代表使用115之后的版本
    """
    url = [DRIVER_URL, DRIVER_URL_115]

    with session() as conn:
        rsp = conn.get(url[idx])
        chrome_list = json.loads(rsp.text)

    if idx == 0:
        # 获取到的版本号为最后有一个/,舍弃掉,并且分割出版本数字,版本号中含有非数字的全都作为非版本数据处理掉,为后续版本比较处理,全部int化掉
        result = [[int(i) for i in val['name'][:-1].split('.')]
                  for val in chrome_list if val['name'][0].isdigit()]
    else:
        result = []
        r_fn = result.append
        for d in chrome_list['versions']:
            r_fn(list(map(int, d['version'].split('.'))))
    return result


def download_chrome_driver(url: str, driver_name: str) -> None:
    """下载驱动文件并解压缩和设置权限
    Paramters
    ---------
    url:下载驱动的地址
    """
    zip_driver_name = 'chromedriver.zip'
    with session() as conn:
        rsp = conn.get(url, stream=True)
    with open(zip_driver_name, 'wb') as f:
        for chunk in rsp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
            else:
                break

    with zipfile.ZipFile(zip_driver_name) as zf:
        # 获取ZIP文件中的所有文件和文件夹列表
        file_list = zf.namelist()

        # 逐个解压文件
        for file in file_list:
            # 从文件路径中提取文件名
            file_name = os.path.basename(file)
            # 将文件解压到目标路径
            if file_name == driver_name:
                zf.extract(file, './')

                # 判断是否是设定的标准路径,如果不是,则移动到标准路径,并移除文件夹
                if (file != driver_name):
                    sh_move(file, driver_name)
                    file_dirname = os.path.dirname(file)
                    os.removedirs(file_dirname)

    os.remove(f'./{zip_driver_name}')
    os.chmod(driver_name, 766)


def get_chrome_version(message: str) -> str:
    """从错误信息中寻找浏览器的版本信息
    Parameters
    ----------
    message:出错信息
    Returns
    -------
    返回版本号信息,如果没有获取到版本号信息,返回空
    """
    start_msg = 'Current browser version is '
    end_msg = 'with binary path'

    end_idx = message.find(end_msg)
    start_idx = len(start_msg) + message.find(start_msg)
    if end_idx == -1:
        return ''
    return message[start_idx:end_idx].strip()


def fit_chrome_version(cur_version: str, check_list: list, prefix_url: str = DRIVER_URL) -> str:
    """根据当前的版本,匹配下载版本. 匹配的下载版本号不大于当前版本号,且是最接近的一个版本号
    Parameters
    ----------
        cur_version:当前版本信息
        check_list:可供下载的版本列表
        prefix_url:前置通用url
    Returns
    -------
    返回一个供下载的版本url
    """
    # 如果没有版本信息,返回一个默认值
    if cur_version == '':
        return prefix_url + '.'.join([str(val) for val in check_list[0]]) + '/'

    cur_list = [int(i) for i in cur_version.split('.')]
    cur_size = len(cur_list)
    version_info = ''
    for i in range(cur_size):
        ver_dif = min([cur_list[i] - val[i]
                       for val in check_list if cur_list[i] >= val[i]])
        check_list = [val for val in check_list if val[i]
                      == cur_list[i] - ver_dif]
        if i == 0:
            version_info = str(cur_list[i] - ver_dif)
        else:
            version_info = version_info + '.' + str(cur_list[i] - ver_dif)
    return prefix_url + version_info + '/'


def setup_dirver(cur_version: str, chrome_list: list, plat_sys: str, plat_machine: str, plat_bits: str, driver_name: str):
    prefix_url = [DRIVER_URL, DRIVER_URL_115_PREFIX]
    if cur_version:
        # 如果当前版本大于等于115
        if [int(i) for i in cur_version.split('.')][0] >= 115:
            ver_idx = 1
        else:
            ver_idx = 0
    else:
        ver_idx = 0
    download_type = get_chromedriver_type(
        plat_sys, plat_machine, plat_bits, ver_idx)

    # 重新获取一次,因为不同版本的下载地址是不一样的.
    chrome_list = get_chromedriver_list(ver_idx)

    print('开始匹配和下载驱动')
    download_url = fit_chrome_version(
        cur_version, chrome_list, prefix_url=prefix_url[ver_idx]) + download_type
    download_chrome_driver(download_url, driver_name)
    print(f'匹配下载驱动完毕')
    return chrome_list


def init_chrome_options(experimental_option: dict = None):
    """初始化设定ChromeOptions
    """
    options = webdriver.ChromeOptions()

    # 忽略SSL验证
    options.add_argument('ignore-certificate-errors')

    # 伪装浏览器
    options.add_argument(
        'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')

    # 屏蔽chrome正受到自动测试软件的控制
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    # 不自动关闭浏览器
    options.add_experimental_option('detach', True)

    # 自定义的追加相关experimental_option的设置
    if experimental_option:
        for k in experimental_option:
            options.add_experimental_option(k, experimental_option[k])

    return options


class ActionInfo:
    def __init__(self, by_val, func, val, by=By.XPATH):
        self.by = by
        self.by_val = by_val
        self.func = func
        self.val = val


class WebdriveChrome:
    def __init__(self, experimental_option: dict = None):
        """初始化Webdriver Chrome
        """
        # 浏览器当前版本(默认浏览器版本为88.0.4324.27,低于该版本,可能造成无法正常运行)
        cur_version = '88.0.4324.27'
        # 浏览器驱动下载列表
        chrome_list = []

        # 获取当前脚本的运行环境
        plat_system = platform.system()
        plat_machine = platform.machine()
        plat_bits = platform.architecture()[0]
        print(f'您的运行系统环境为:{plat_system},架构为:{plat_machine},位数为:{plat_bits}')

        driver_name = get_driver_name(plat_system)
        driver_path = f'./{driver_name}'

        if not os.path.exists(driver_path):
            chrome_list = setup_dirver(
                cur_version, chrome_list, plat_system, plat_machine, plat_bits, driver_name)

        # 初始化浏览器配置项
        options = init_chrome_options(experimental_option)

        # 默认等待时间(单位:秒)
        waittime = 5

        # 默认尝试3次.
        for _ in range(3):
            try:
                # 初始化Service服务
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                driver.implicitly_wait(waittime)  # 避免模拟器运行慢获取不到元素
                self.driver = driver
                break
            except Exception as e:
                cur_version = get_chrome_version(e.msg)
                chrome_list = setup_dirver(
                    cur_version, chrome_list, plat_system, plat_machine, plat_bits, driver_name)

    def run(self, url: str, info: list[ActionInfo]):
        """运行Web动作
        Parameters
        ----------
        url:运行的url
        info: 运行动作对象列表
        """
        driver = self.driver
        driver.get(url)
        for t in info:
            obj = driver.find_element(t.by, t.by_val)
            t.func(obj) if t.val is None else t.func(obj, t.val)


if __name__ == '__main__':

    # 运行测试用例
    url = 'https://space.bilibili.com/2136075?spm_id_from=333.1296.0.0'

    # 登录Bilibili,点击为我充电按钮
    info = [ActionInfo(
        '//*[@id="page-index"]/div[2]/div[4]/div/div[1]', WebElement.click, None)]

    try:
        wb = WebdriveChrome()
        wb.run(url, info)
        print('太棒啦,webdriver成功运行')
    except Exception as e:
        print(f'啊哦,真糟糕,运行失败了{e}')
    finally:
        wb.driver.close()
