import json
import os
import time

import win32api
import win32gui
import win32con
from caitong_trade.util.win32_util import pos_in_window_rect, GuiPosition, HwndType


def login_window_open() -> bool:
    home_hwnd = -1
    hwnd_list = []
    win32gui.EnumWindows(lambda handle, param: param.append(handle), hwnd_list)
    for hwnd in hwnd_list:
        if win32gui.GetWindowText(hwnd) == "网上股票交易系统5.0" and "Afx:400000" in win32gui.GetClassName(hwnd):
            home_hwnd = hwnd
            break
    # TODO 判断是否登录的逻辑需要优化
    if home_hwnd >= 0:
        child_list = []
        win32gui.EnumChildWindows(home_hwnd, lambda hwnd, param: param.append(hwnd), child_list)
        for hwnd in child_list:
            if win32gui.GetWindowText(hwnd) == "用户登录":
                return False
        return True
    return False


class LoginWindow:
    login_title = '用户登录'
    login_win_class = '#32770'

    def __init__(self, json_file=None, username=None, password=None, comm_password=None, exe_path=None):
        if json_file:
            with open(json_file, encoding='utf-8') as f:
                config = json.load(f)
                self.__exe_path = config["exe_path"]
                account = config["account"]
                self.__username = account["username"]
                self.__password = account["password"]
                self.__comm_password = account["comm_password"]
        if username and password and comm_password and exe_path:
            self.__exe_path = exe_path
            self.__username = username
            self.__password = password
            self.__comm_password = comm_password
        self.__login_hwnd = -1
        # 账号输入框, 交易密码输入框, 通讯密码输入框, 登录按钮 的位置中心
        #
        self.__pos_username_input = GuiPosition(HwndType.Edit, 99, 113, 114, 14)
        self.__pos_password_input = GuiPosition(HwndType.Edit, 96, 134, 117, 20)
        self.__pos_comm_password_input = GuiPosition(HwndType.Edit, 96, 158, 137, 18)
        self.__pos_login_button = GuiPosition(HwndType.Button, 248, 38, 75, 21)

    def __open_login_windows(self, ):
        login_hwnd = win32gui.FindWindow(self.login_win_class, self.login_title)
        if login_hwnd <= 0:
            if self.__exe_path is None:
                # TODO
                win32api.WinExec("D:\\Program Files (x86)\\haitongsec\\xiadan.exe", win32con.SW_SHOWNORMAL)
            else:
                win32api.WinExec(self.__exe_path, win32con.SW_SHOWNORMAL)
            # while True:
            #     if self.__login_hwnd > 0:
            #         return
            #     else:
            time.sleep(10)
            self.__login_hwnd = win32gui.FindWindow(self.login_win_class, self.login_title)
        else:
            self.__login_hwnd = login_hwnd

    def __get_useful_handle(self):
        child_list = []
        win32gui.EnumChildWindows(self.__login_hwnd, lambda hwnd, param: param.append(hwnd), child_list)

        handles = {}
        for child in child_list:
            if pos_in_window_rect(self.__pos_username_input, win32gui.GetWindowRect(self.__login_hwnd), child):
                handles.update(username_hwnd=child)
            elif pos_in_window_rect(self.__pos_password_input, win32gui.GetWindowRect(self.__login_hwnd), child):
                handles.update(password_hwnd=child)
            elif pos_in_window_rect(self.__pos_comm_password_input, win32gui.GetWindowRect(self.__login_hwnd), child):
                handles.update(comm_password_hwnd=child)
            elif pos_in_window_rect(self.__pos_login_button, win32gui.GetWindowRect(self.__login_hwnd), child):
                handles.update(login_btn_hwnd=child)
        return handles

    def login(self):
        if login_window_open():
            return
        else:
            # 打开登录窗口
            self.__open_login_windows()

            # 找到各个句柄
            handles = self.__get_useful_handle()

            # 使用 windows 消息机制 登录
            win32gui.SendMessage(handles["username_hwnd"], win32con.WM_SETTEXT, None, self.__username)
            win32gui.SendMessage(handles["password_hwnd"], win32con.WM_SETTEXT, None, self.__password)
            win32gui.SendMessage(handles["comm_password_hwnd"], win32con.WM_SETTEXT, None, self.__password)
            win32gui.SendMessage(handles["login_btn_hwnd"], win32con.WM_LBUTTONDOWN, None, None)
            win32gui.SendMessage(handles["login_btn_hwnd"], win32con.WM_LBUTTONUP, None, None)
            time.sleep(6)


if __name__ == '__main__':
    conf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ht_config.json")
    login = LoginWindow(json_file=conf_path)
    login.login()
