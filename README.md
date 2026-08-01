# 文本无损压缩算法演进与实证性能研究 (Seven-Generation Text Compression Benchmark)

## 📌 项目简介

本项目完整复现并重构了从基础哈夫曼编码到高阶 Context Modeling (PPMd) 的**七代文本无损压缩算法**[cite: 11]。

项目以经典英文语料库《福尔摩斯探案全集》（*The Complete Sherlock Holmes*，约 600KB）作为标准基准（Benchmark）[cite: 11]，在统一的 Python 框架下全方位对比了不同范式算法的**压缩率（Compression Ratio）**、**处理耗时（Execution Time）**与**工程实现壁垒**[cite: 11]。

研究展示了文本压缩技术从**静态统计映射**逐步演进至**高阶语义预测**的全过程[cite: 11]。

---

## 🌟 核心演进范式

```
[ Statistical Coding ]  ──Evolution──>  [ Dictionary Coding ]  ──Evolution──>  [ Context Modeling ]
 (Frequency-based)                       (Repeated Sequences)                   (Semantic Prediction)
         │                                       │                                      │
         ▼                                       ▼                                      ▼
  Huffman / Canonical                       LZ77 / LZMA                            PPM / Markov

```

[cite: 6, 11]

1. **统计编码范式 (Statistical Coding)**：基于字符发生频率构建变长编码（如 Huffman、Canonical Huffman）[cite: 6, 11]。受到一阶熵（Zero-order Entropy）的物理极限限制[cite: 11]。
2. **字典编码范式 (Dictionary Coding)**：基于重复子串匹配与大字典构建（如 LZ77、LZMA），通过捕获长距离冗余大幅提升压缩率[cite: 6, 11]。
3. **上下文预测模型 (Context Modeling)**：基于高阶马尔可夫链（Markov Chain）与部分匹配预测（PPM），实现了“压缩即智能”的语义上下文建模[cite: 6, 11]。

---

## 📊 七代算法性能对比

> **实验环境**：Intel Core i7 CPU, Python 3.10, 标准测试语料库 (~600KB)[cite: 11]。

| 版本 (Version) | 核心技术方案 (Core Technology) | 压缩后大小 (Compressed Size) | 压缩率 (Ratio) | 运行时间 (Time) | 范式归属 (Paradigm) |
| --- | --- | --- | --- | --- | --- |
| **V1.0** | Static Huffman (静态哈夫曼)[cite: 11] | 332,127 B[cite: 11] | **45.33%**[cite: 8, 11] | 0.33 s[cite: 8, 11] | Statistical Coding[cite: 6, 11] |
| **V2.0** | Canonical Huffman (规范哈夫曼)[cite: 11] | 330,998 B[cite: 11] | **45.51%**[cite: 8, 11] | 0.40 s[cite: 8, 11] | Statistical Coding[cite: 6, 11] |
| **V3.0** | Arithmetic Coding (算术编码)[cite: 11] | -[cite: 11] | **35.81%**[cite: 8, 11] | 2.10 s[cite: 8] | Interval Mapping[cite: 11] |
| **V4.0** | LZ77 + Huffman[cite: 11] | -[cite: 11] | **48.12%**[cite: 8] | 0.55 s[cite: 8] | Hybrid Dictionary[cite: 6, 11] |
| **V5.0** | BWT + MTF + RLE + Huffman[cite: 11] | 289,716 B[cite: 11] | **52.31%**[cite: 8, 11] | 3.47 s[cite: 8, 11] | Global Rearrangement[cite: 11] |
| **V6.0** | LZMA (Range Coding + Large Dict)[cite: 11] | 188,880 B[cite: 11] | **68.91%**[cite: 8, 11] | 0.24 s[cite: 8, 11] | Dictionary + Range[cite: 6, 11] |
| **V7.0** | **PPMd (Order-8 Context Prediction)**[cite: 11] | **149,053 B**[cite: 11] | **75.46%**[cite: 8, 11] | **0.11 s**[cite: 8, 11] | Context Modeling[cite: 6, 11] |

---

## 🔍 关键工程发现与瓶颈分析

### 1. 算术编码 (V3.0) 的工程陷阱与性能回归

理论上算术编码突破了哈夫曼编码的整数比特限制，能无限逼近香农极限[cite: 11]。但在 Python 环境的实际测量中，V3.0 的压缩率仅有 **35.81%**，且耗时显著增加[cite: 8, 11]。

* **元数据膨胀**：小语料库下保存区间概率表的元数据开销过大[cite: 11]。
* **高精度浮点开销**：由于精度要求，使用 Python 软件级模拟的 `Decimal` 替代硬件级 `Float` 带来了高达 **76倍** 的计算延时开销（`0.38s` vs `0.005s`）[cite: 10, 11]。

### 2. 多阶段管道流 (V5.0) 的特征聚集效应

通过 **BWT (Burrows-Wheeler Transform) $\rightarrow$ MTF $\rightarrow$ RLE $\rightarrow$ Huffman** 的组合管道，算法将离散文本上下文聚类，使压缩率一举突破 50%（达到 **52.31%**），验证了“预处理是提升压缩效率的核心”[cite: 11]。

### 3. PPMd (V7.0) 的高阶语义预测机制

V7.0 引入了基于马尔可夫链的 8 阶上下文预测（Partial Matching）[cite: 11]。当阶数达到 4 阶及以上时，系统具备了对自然语言文本流的局部语义预测能力，压缩率达到了最高 **75.46%**，且解压/压缩极快[cite: 8, 11]。

---

## 📂 项目目录结构

```
.
├── TEST1/      # V1.0 Static Huffman Coding
├── TEST2/      # V2.0 Canonical Huffman Coding
├── TEST3/      # V3.0 Arithmetic Coding
├── TEST4/      # V4.0 LZ77 + Huffman
├── TEST5/      # V5.0 BWT + MTF + RLE + Huffman
├── TEST6/      # V6.0 LZMA Architecture
├── TEST7/      # V7.0 PPMd Context Modeling Algorithm
├── TEST8/      # Benchmarking & Visualization Scripts
└── TEST9/      # Document & Theoretical Analysis Support

```

[cite: 7]

---

## 🏭 工业落地部署建议

* **高并发/实时场景（Web/HTTP）**：首选 **Canonical Huffman** (如 Gzip, Brotli)，在极低延迟与高兼容性间取得最佳平衡[cite: 11]。
* **大容量归档场景（Big Data/Storage）**：首选 **LZMA** (如 7z)，牺牲部分压缩时间以换取极致的存储空间节省[cite: 11]。
* **高价值专业文本（Legal/Medical Records）**：首选 **PPMd**，在带宽受限且文本结构高度规范的场景下能够提供最高压缩比[cite: 11]。
