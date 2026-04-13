import os
import json
import time
from collections import Counter
from decimal import Decimal, getcontext

# 设置超高精度，防止在处理长文本时区间“塌陷”
getcontext().prec = 2000

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def compress_v3_0(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text: return

    start_time = time.time()

    # 1. 统计频率并建立累积概率区间 [start, end)
    counts = Counter(text)
    total = Decimal(len(text))
    probs = {}
    current = Decimal(0)
    for char in sorted(counts.keys()):
        prob = Decimal(counts[char]) / total
        probs[char] = (current, current + prob)
        current += prob

    # 2. 算术编码核心迭代
    low = Decimal(0)
    high = Decimal(1)
    for char in text:
        width = high - low
        start, end = probs[char]
        high = low + width * end
        low = low + width * start

    # 3. 存储：为了论文对比，我们将元数据和编码值序列化
    # 注意：工业级会将其转为二进制位流，这里为了演示算法逻辑使用字符串存储
    output_data = {
        "value": str(low),
        "probs": {k: [str(v[0]), str(v[1])] for k, v in probs.items()},
        "length": len(text)
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f)

    comp_size = os.path.getsize(output_path)
    orig_size = os.path.getsize(input_path)
    print(f"V3.0 完成。压缩率: {100 * (1 - comp_size / orig_size):.2f}%")
    return time.time() - start_time


def decompress_v3_0(compressed_path, output_path):
    start_time = time.time()
    with open(compressed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    encoded_val = Decimal(data["value"])
    probs = {k: [Decimal(v[0]), Decimal(v[1])] for k, v in data["probs"].items()}
    length = data["length"]

    # 4. 解码逻辑：在概率区间中不断反推字符
    res = []
    current_val = encoded_val
    for _ in range(length):
        for char, (start, end) in probs.items():
            if start <= current_val < end:
                res.append(char)
                current_val = (current_val - start) / (end - start)
                break

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(res))
    return time.time() - start_time


if __name__ == "__main__":
    fin, fcmp, fout = "input.txt", "compressed_v3.json", "output_v3.txt"
    # 测试前确保输入文件不要太大（Decimal运算很慢），建议先用1KB左右的文本测试
    print(">>> 执行 V3.0 (Arithmetic Coding)...")
    c_time = compress_v3_0(fin, fcmp)
    d_time = decompress_v3_0(fcmp, fout)
    print(f"压缩耗时: {c_time:.4f}s, 解压耗时: {d_time:.4f}s")