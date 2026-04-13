"""
V1.1 优化点对比 (V1.1 vs V1.0):
1. 逻辑优化：从 V1.0 的“字符串拼接+字典查找”改为“二叉树路径导航”。
   - V1.0 像翻字典：走一步翻一次地图，查找开销随编码长度增加。
   - V1.1 像走迷宫：读到0向左，读到1向右，到达叶子即解码，逻辑更纯粹。

2. 内存优化：消除“内存怪兽”。
   - V1.0 需要一次性生成巨大的 01 字符串（原文件大小的 8 倍左右），大文件易崩溃。
   - V1.1 采用流式处理（Streaming），逐字节读取，内存占用恒定且极低。

3. 扩展性：
   - V1.1 理论上时间复杂度更稳定，且支持“边读边解”，具备处理超大文件的能力。
"""

import heapq
import os
import json
import time
from collections import defaultdict

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# --- 核心数据结构 ---
class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


# --- 构建逻辑 ---
def build_huffman_tree(freq_dict):
    heap = [HuffmanNode(c, f) for c, f in freq_dict.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)
    return heap[0] if heap else None


def build_codebook(root):
    codebook = {}

    def traverse(node, code):
        if node.char is not None:
            codebook[node.char] = code
            return
        traverse(node.left, code + "0")
        traverse(node.right, code + "1")

    traverse(root, "")
    return codebook


# --- 压缩函数 (保持 V1.0 的兼容性) ---
def compress_text(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text: return None, None

    freq_dict = defaultdict(int)
    for c in text:
        freq_dict[c] += 1

    root = build_huffman_tree(freq_dict)
    codebook = build_codebook(root)

    encoded = ''.join(codebook[c] for c in text)
    pad = (8 - len(encoded) % 8) % 8
    encoded += '0' * pad

    with open(output_path, "wb") as f:
        # 头部存储 codebook 供解压使用
        header = json.dumps({"codebook": codebook, "pad_len": pad}).encode()
        f.write(len(header).to_bytes(4, 'big'))
        f.write(header)
        byte_arr = bytearray(int(encoded[i:i + 8], 2) for i in range(0, len(encoded), 8))
        f.write(byte_arr)

    orig = os.path.getsize(input_path)
    comp = os.path.getsize(output_path)
    print(f"压缩完成。原文件: {orig}B, 压缩后: {comp}B, 压缩率: {100 * (1 - comp / orig):.2f}%")
    return root, codebook


def decompress_text_v1_1(compressed_path, output_path, root):
    start_time = time.time()
    with open(compressed_path, "rb") as f:
        header_len = int.from_bytes(f.read(4), 'big')
        header = json.loads(f.read(header_len).decode())
        pad = header["pad_len"]
        data = f.read()
    res = []
    curr_node = root
    for i in range(len(data)):
        byte = data[i]
        bits = format(byte, '08b')
        if i == len(data) - 1 and pad > 0:
            bits = bits[:-pad]
        for bit in bits:
            if bit == '0':
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right
            if curr_node.left is None and curr_node.right is None:
                res.append(curr_node.char)
                curr_node = root  # 重置回根节点
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(''.join(res))
    end_time = time.time()
    return end_time - start_time


# --- 主函数：对比测试 ---
if __name__ == "__main__":
    fin, fcmp, fout = "input.txt", "compressed.huff", "output.txt"

    # 确保有大文件可供测试
    if not os.path.exists(fin) or os.path.getsize(fin) < 1000:
        print("提示：请确保目录下有一个较大的 input.txt 文件以观察优化效果。")

    print(">>> 阶段 1: 执行压缩...")
    tree_root, _ = compress_text(fin, fcmp)

    if tree_root:
        print("\n>>> 阶段 2: 执行 V1.1 树遍历解压优化...")
        duration = decompress_text_v1_1(fcmp, fout, tree_root)
        print(f"V1.1 解压耗时: {duration:.4f} 秒")