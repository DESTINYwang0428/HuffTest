import heapq, os, json, time
from collections import defaultdict

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char, self.freq, self.left, self.right = char, freq, left, right

    def __lt__(self, other): return self.freq < other.freq


def build_huffman_tree(freq_dict):
    heap = [HuffmanNode(c, f) for c, f in freq_dict.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        l, r = heapq.heappop(heap), heapq.heappop(heap)
        heapq.heappush(heap, HuffmanNode(freq=l.freq + r.freq, left=l, right=r))
    return heap[0] if heap else None


def get_bit_lengths(node, code="", lengths=None):
    if lengths is None: lengths = {}
    if node.char is not None:
        lengths[node.char] = len(code)
        return lengths
    get_bit_lengths(node.left, code + "0", lengths)
    get_bit_lengths(node.right, code + "1", lengths)
    return lengths


# --- V2.0 核心：生成范式编码 ---
def generate_canonical_book(bit_lengths):
    # 按照 1.长度 2.字符ASCII码 排序
    sorted_chars = sorted(bit_lengths.items(), key=lambda x: (x[1], x[0]))
    canonical_book = {}
    code = 0
    prev_len = sorted_chars[0][1]

    for char, length in sorted_chars:
        code <<= (length - prev_len)  # 长度增加时，左移对齐
        canonical_book[char] = format(code, f'0{length}b')
        code += 1
        prev_len = length
    return canonical_book


def compress_v2_0(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text: return

    # 1. 统计并获取位长度
    freq_dict = defaultdict(int)
    for c in text: freq_dict[c] += 1
    root = build_huffman_tree(freq_dict)
    bit_lengths = get_bit_lengths(root)

    # 2. 转化为范式编码
    canonical_book = generate_canonical_book(bit_lengths)

    # 3. 编码数据
    encoded = ''.join(canonical_book[c] for c in text)
    pad = (8 - len(encoded) % 8) % 8
    encoded += '0' * pad

    # 4. 写入文件：Header只存字符和长度，非常精简
    with open(output_path, "wb") as f:
        header = json.dumps({"lengths": bit_lengths, "pad": pad}).encode()
        f.write(len(header).to_bytes(4, 'big'))
        f.write(header)
        f.write(bytearray(int(encoded[i:i + 8], 2) for i in range(0, len(encoded), 8)))

    orig, comp = os.path.getsize(input_path), os.path.getsize(output_path)
    print(f"V2.0 完成。大小: {comp}B, 压缩率: {100 * (1 - comp / orig):.2f}%")


def decompress_v2_0(compressed_path, output_path):
    start_time = time.time()
    with open(compressed_path, "rb") as f:
        header_len = int.from_bytes(f.read(4), 'big')
        header = json.loads(f.read(header_len).decode())
        bit_lengths, pad = header["lengths"], header["pad"]
        data = f.read()

    # 5. 核心：无需建树，直接由长度表生成解码字典
    decoding_book = {v: k for k, v in generate_canonical_book(bit_lengths).items()}

    res, curr = [], ""
    for i, byte in enumerate(data):
        bits = format(byte, '08b')
        if i == len(data) - 1 and pad > 0: bits = bits[:-pad]
        for bit in bits:
            curr += bit
            if curr in decoding_book:
                res.append(decoding_book[curr])
                curr = ""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(''.join(res))
    return time.time() - start_time


if __name__ == "__main__":
    fin, fcmp, fout = "input.txt", "compressed_v2.huff", "output_v2.txt"
    compress_v2_0(fin, fcmp)
    print(f"V2.0 解压耗时: {decompress_v2_0(fcmp, fout):.4f}s")