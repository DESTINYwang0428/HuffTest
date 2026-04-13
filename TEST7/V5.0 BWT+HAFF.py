import os, time, math
from collections import Counter


def bwt_transform(text):
    block_size = 5000  # 可以尝试增加到 10000
    transformed = []
    for i in range(0, len(text), block_size):
        s = text[i:i + block_size] + "\0"
        n = len(s)
        table = sorted(range(n), key=lambda idx: s[idx:] + s[:idx])
        transformed.append("".join(s[idx - 1] for idx in table))
    return "".join(transformed)


def rle_process(text):
    """
    游程编码：专门对付 BWT 产生的一长串重复字符。
    例如：'eeeeee' -> 'e6'
    """
    if not text: return ""
    res = []
    i = 0
    while i < len(text):
        count = 1
        while i + 1 < len(text) and text[i] == text[i + 1] and count < 255:
            i += 1
            count += 1
        # 如果重复超过3次，就启用 RLE
        if count >= 3:
            res.append(text[i] + str(count))
        else:
            res.append(text[i] * count)
        i += 1
    return "".join(res)


def calculate_huffman_size(data):
    if not data: return 0
    counts = Counter(data)
    total = len(data)
    entropy = sum(-(count / total) * math.log2(count / total) for count in counts.values())
    return int((entropy * total) / 8 * 1.02)  # 稍微降低 Header 预估


def run_v4_complete(input_path):
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    start_time = time.time()
    v2_size = calculate_huffman_size(text)

    # --- 核心进化链条 ---
    bwt_data = bwt_transform(text)
    rle_data = rle_process(bwt_data)  # 关键：让 BWT 的聚集效应变现
    v4_size = calculate_huffman_size(rle_data)

    duration = time.time() - start_time
    orig_size = os.path.getsize(input_path)

    print(f"\n【V5.0 完全体：BWT + RLE + Huffman】")
    print(f"原始大小: {orig_size} B")
    print(f"V2.0 预估: {v2_size} B ({100 * (1 - v2_size / orig_size):.2f}%)")
    print(f"V5.0 预估: {v4_size} B ({100 * (1 - v4_size / orig_size):.2f}%)")
    print(f"绝对提升: {v2_size - v4_size} 字节")
    print(f"耗时: {duration:.4f}s")


if __name__ == "__main__":
    run_v4_complete("input.txt")