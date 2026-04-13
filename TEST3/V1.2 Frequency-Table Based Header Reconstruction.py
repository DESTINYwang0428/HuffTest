# V1.2: Frequency-Table Based Header Reconstruction



"""
V1.2 优化点对比 (V1.2 vs V1.1):
1. 空间优化（核心）：修改文件头格式，将“编码表字典”替换为“原始频率字典”。
   - 理由：存整数频率比存01字符串码表更节省字节，显著缩小了文件头（Header）的体积。
2. 逻辑进化：引入“解码端重构”机制。
   - 进步：解压不再依赖存储的码表，而是通过频率自发重构哈夫曼树，提升了压缩率，同时保证了数据的自洽性。
3. 压缩率提升：实测在中小文件上，压缩后体积有进一步缩减。
"""




import heapq
import os
import json
import time
from collections import defaultdict

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


def compress_v1_2(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text: return

    # 1. 统计频率并建树
    freq_dict = defaultdict(int)
    for c in text: freq_dict[c] += 1
    root = build_huffman_tree(freq_dict)
    codebook = build_codebook(root)

    # 2. 生成编码数据
    encoded = ''.join(codebook[c] for c in text)
    pad = (8 - len(encoded) % 8) % 8
    encoded += '0' * pad

    # 3. 核心优化：只存频率表，不存码表
    with open(output_path, "wb") as f:
        header = json.dumps({"freq": freq_dict, "pad": pad}).encode()
        f.write(len(header).to_bytes(4, 'big'))
        f.write(header)
        byte_arr = bytearray(int(encoded[i:i + 8], 2) for i in range(0, len(encoded), 8))
        f.write(byte_arr)

    orig = os.path.getsize(input_path)
    comp = os.path.getsize(output_path)
    print(f"V1.2 压缩完成。大小: {comp}B, 压缩率: {100 * (1 - comp / orig):.2f}%")


def decompress_v1_2(compressed_path, output_path):
    """
    V1.2 进步点：从频率表重建哈夫曼树，实现自洽解压
    """
    start_time = time.time()
    with open(compressed_path, "rb") as f:
        header_len = int.from_bytes(f.read(4), 'big')
        header = json.loads(f.read(header_len).decode())
        freq_dict = header["freq"]
        pad = header["pad"]
        data = f.read()

    # 4. 关键：现场重构哈夫曼树
    rebuilt_root = build_huffman_tree(freq_dict)

    # 5. 使用 V1.1 的树导航逻辑解码
    res = []
    curr_node = rebuilt_root
    for byte in data:
        bits = format(byte, '08b')
        if byte is data[-1] and pad > 0:  # 最后一个字节处理补位
            bits = bits[:-pad]
        for bit in bits:
            curr_node = curr_node.left if bit == '0' else curr_node.right
            if curr_node.left is None and curr_node.right is None:
                res.append(curr_node.char)
                curr_node = rebuilt_root

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(''.join(res))
    return time.time() - start_time


if __name__ == "__main__":
    fin, fcmp, fout = "input.txt", "compressed_v12.huff", "output_v12.txt"
    print(">>> 执行 V1.2 ...")
    compress_v1_2(fin, fcmp)
    duration = decompress_v1_2(fcmp, fout)
    print(f"V1.2 解压耗时: {duration:.4f}s")