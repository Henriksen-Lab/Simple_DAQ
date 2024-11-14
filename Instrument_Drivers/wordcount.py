# Written by Yiwei Le 9/26/2023
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt

import re


def count_chinese_characters(text):
    # 去除标点符号
    cleaned_text = re.sub(r'[^\w\s]', '', text)

    # 统计中文字数
    chinese_count = sum(1 for char in cleaned_text if '\u4e00' <= char <= '\u9fff')

    return chinese_count


# 测试
text = "“大树园”。志地之产，而偶合于公孙故事，非欲以自况云。时乾隆三十四年五月既望，春和主人傅恒记。"
print(f"中文字数: {count_chinese_characters(text)}")