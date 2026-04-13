import pyppmd
import os
import time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def run_ppmd_test():
    filename = "input.txt"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return
    with open(filename, "rb") as f:
        data = f.read()
    orig_sz = len(data)
    start = time.time()
    compressed = pyppmd.compress(data, max_order=8)
    duration = time.time() - start
    comp_sz = len(compressed)
    ratio = (1 - comp_sz / orig_sz) * 100
    print(f"--- V7.0 PPMd 巅峰实验结果 ---")
    print(f"原始文件: {filename}")
    print(f"原始大小: {orig_sz} B")
    print(f"压缩大小: {comp_sz} B")
    print(f"最终压缩率: {ratio:.2f}%")
    print(f"耗时: {duration:.4f}s")
if __name__ == "__main__":
    run_ppmd_test()