# -*- coding: utf-8 -*-
import os
import sys

# 临时添加allure到PATH
os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + r'C:\allure\bin'

# 测试allure命令
print("测试Allure安装...")
result = os.system('allure --version')

if result == 0:
    print("\n✅ Allure安装成功！")
    print("\n现在可以运行测试了：")
    print("python run.py")
else:
    print("\n❌ Allure未正确配置")
    print("请按照说明配置环境变量")
