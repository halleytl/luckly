#-*- coding:u8
import os

class BaseEngine():

    prefix = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "search" )
    alias = None
    def get_conn(self):
        """
        连接对象
        """
        pass

    def show(self, inf_name, request):
        """
        如果是sql 显示拼接后的sql
        """
        pass

    def search(self, inf_name, request):
        """
        返回执行结果
        """
        pass

    def debug(self, inf_name, request):
        """
        调试信息
        """
        return self.show(inf_name, request)

    def struct(self, show_type, request):
        """
        获得输入参数的结构
        """
        pass

    def get_file(self, inf_name):
        """
        返回文件路径：期望首先检测本地路径，如果没有检测共享路径
        """
        if self.alias:
            path = os.path.join(self.prefix, self.alias, inf_name + ".sql")
            if os.path.isfile(path):
                return path
            else:
                path = os.path.join(self.prefix, "share", inf_name + ".sql")
                if os.path.isfile(path):
                    return path
                return None
        else:
            path = os.path.join(self.prefix, "share", inf_name + ".sql")
            if os.path.isfile(path):
                return path
            return None

