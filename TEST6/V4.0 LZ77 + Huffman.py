import os
import time
import math
from collections import Counter

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def mtf_transform(text):
    """
    MTF 变换：将文本转换为动态字典索引流。
    利用局部相关性，将高频字符转化为极小的数字（如 0, 1, 2）。
    """
    dictionary = [chr(i) for i in range(256)]
    transformed = []
    for char in text:
        try:
            idx = dictionary.index(char)
            transformed.append(idx)
            # 核心：将用过的字符移到最前面，让下次再出现时索引为 0
            dictionary.insert(0, dictionary.pop(idx))
        except ValueError:
            # 处理特殊编码字符
            transformed.append(ord(char) % 256)
    return transformed


def calculate_compressed_size(data):
    """
    模拟 Huffman 编码后的实际二进制体积。
    计算公式：总位数 = 总字符数 * 一阶熵
    """
    if not data: return 0
    counts = Counter(data)
    total = len(data)
    entropy = 0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    # 理论二进制位数 / 8 (字节) + 5% 的哈夫曼头文件开销
    return int((entropy * total) / 8 * 1.05)


def compress_v4_0_mtf(input_path):
    if not os.path.exists(input_path):
        print(f"找不到文件: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    start_time = time.time()

    # --- 步骤 1: 原始哈夫曼 (V2.0 水平) ---
    raw_size = calculate_compressed_size(text)

    # --- 步骤 2: MTF 变换 (V4.0 核心) ---
    mtf_data = mtf_transform(text)

    # --- 步骤 3: MTF 后的哈夫曼压缩 ---
    v4_compressed_size = calculate_compressed_size(mtf_data)

    duration = time.time() - start_time
    orig_size = os.path.getsize(input_path)

    # 输出结果
    print(f"\n" + "=" * 40)
    print(f"【V4.0 MTF+Huffman 进化版输出】")
    print(f"=" * 40)
    print(f"处理文件: {input_path}")
    print(f"原始文件大小: {orig_size} B")
    print(f"-" * 40)
    print(f"V2.0 (纯Huffman) 预估大小: {raw_size} B (压缩率: {100 * (1 - raw_size / orig_size):.2f}%)")
    print(
        f"V4.0 (MTF+Huffman) 预估大小: {v4_compressed_size} B (压缩率: {100 * (1 - v4_compressed_size / orig_size):.2f}%)")
    print(f"-" * 40)
    print(f"本次进化提升（绝对值）: {100 * (raw_size - v4_compressed_size) / orig_size:.2f}%")
    print(f"耗时: {duration:.4f}s")
    print(f"=" * 40)


if __name__ == "__main__":
    # 跑一下你的福尔摩斯
    compress_v4_0_mtf("input.txt")