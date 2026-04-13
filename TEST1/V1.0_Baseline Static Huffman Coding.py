import heapq
import os
import json
import time
from collections import defaultdict

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


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
def compress_text_v1_0(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text: return None

    freq_dict = defaultdict(int)
    for c in text:
        freq_dict[c] += 1

    root = build_huffman_tree(freq_dict)
    codebook = build_codebook(root)

    encoded = ''.join(codebook[c] for c in text)
    pad = (8 - len(encoded) % 8) % 8
    encoded += '0' * pad

    with open(output_path, "wb") as f:
        header = json.dumps({"codebook": codebook, "pad_len": pad}).encode()
        f.write(len(header).to_bytes(4, 'big'))
        f.write(header)
        byte_arr = bytearray(int(encoded[i:i + 8], 2) for i in range(0, len(encoded), 8))
        f.write(byte_arr)

    orig = os.path.getsize(input_path)
    comp = os.path.getsize(output_path)
    print(f"压缩完成。原文件: {orig}B, 压缩后: {comp}B, 压缩率: {100 * (1 - comp / orig):.2f}%")


def decompress_text_v1_0(compressed_path, output_path):
    """
    V1.0 原型：使用巨大的 01 字符串和字典匹配进行解压
    """
    start_time = time.time()

    with open(compressed_path, "rb") as f:
        header_len = int.from_bytes(f.read(4), 'big')
        header = json.loads(f.read(header_len).decode())
        codebook = header["codebook"]
        pad = header["pad_len"]
        data = f.read()

    # 反转编码表用于查找
    rev = {v: k for k, v in codebook.items()}

    # 核心痛点：生成了一个巨大的比特字符串（耗内存）
    bits = ''.join(format(b, '08b') for b in data)
    if pad > 0: bits = bits[:-pad]

    # 核心痛点：频繁的字符串拼接和字典查找
    res, curr = [], ""
    for b in bits:
        curr += b
        if curr in rev:
            res.append(rev[curr])
            curr = ""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(''.join(res))

    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    fin, fcmp, fout = "input.txt", "compressed.huff", "output.txt"

    print(">>> 阶段 1: 执行压缩 (V1.0)...")
    compress_text_v1_0(fin, fcmp)

    print("\n>>> 阶段 2: 执行 V1.0 基础解码...")
    duration = decompress_text_v1_0(fcmp, fout)
    print(f"V1.0 解压耗时: {duration:.4f} 秒")