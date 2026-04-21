# -*- coding: utf-8 -*-
import shutil
import pytest
import os
import webbrowser
from conf.setting import REPORT_TYPE

# 自动添加Allure到PATH（如果环境变量未配置）
allure_bin = r'C:\allure\bin'
if os.path.exists(allure_bin) and allure_bin not in os.environ.get('PATH', ''):
    os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + allure_bin
    print(f"✅ 已自动添加Allure到PATH: {allure_bin}")

if __name__ == '__main__':

    if REPORT_TYPE == 'allure':
        # 运行pytest测试
        print("\n" + "="*60)
        print("开始执行接口自动化测试...")
        print("="*60 + "\n")
        
        pytest.main(
            ['-s', '-v', '--alluredir=./report/temp', './testcase', '--clean-alluredir',
             '--junitxml=./report/results.xml'])

        # 复制环境配置文件
        shutil.copy('./environment.xml', './report/temp')
        
        # 生成并打开Allure报告
        print("\n" + "="*60)
        print("生成Allure测试报告...")
        print("="*60 + "\n")
        
        os.system(f'allure serve ./report/temp')

    elif REPORT_TYPE == 'tm':
        pytest.main(['-vs', '--pytest-tmreport-name=testReport.html', '--pytest-tmreport-path=./report/tmreport'])
        webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')
