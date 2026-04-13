import lzma
import os
import time

# 锁定当前文件夹，确保能读到你的 input.txt
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def run_final_test():
    filename = "input.txt"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found in current directory.")
        return

    # 读取你的原始文件
    with open(filename, "rb") as f:
        data = f.read()

    orig_sz = len(data)
    start = time.time()

    # 极致压缩 (LZMA: 字典查找 + 区间编码)
    # 不再生成哈夫曼树，而是直接映射到 0-1 之间的概率区间
    compressed = lzma.compress(data, preset=9)

    duration = time.time() - start
    comp_sz = len(compressed)
    ratio = (1 - comp_sz / orig_sz) * 100

    # 仅输出必要的核心数据
    print(f"--- V6.0 LZMA 实验结果 ---")
    print(f"原始文件: {filename}")
    print(f"原始大小: {orig_sz} B")
    print(f"压缩大小: {comp_sz} B")
    print(f"压缩率: {ratio:.2f}%")
    print(f"耗时: {duration:.4f}s")


if __name__ == "__main__":
    run_final_test()