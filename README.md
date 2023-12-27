# AVF 压缩格式 V1.4.2 (Python 实现)

## 使用说明

```python
from avfcomp import AVFComp, AVFDecomp, CompHandler

# compress
path = "your/path/raw.avf"
# choose from plain, gzip, bzip2, lzma(default)
Compressor = AVFComp(handler=CompHandler.LZMA)
Compressor.process_in(path)
Compressor.process_out("comp.cvf")

# decompress
path = "your/path/comp.cvf"
# choose from plain, gzip, bzip2, lzma(default)
Decompressor = AVFDecomp(handler=CompHandler.LZMA)
Decompressor.process_in(path)
Decompressor.process_out("raw.avf")
```

## 格式说明 (目前支持 Arbiter 0.52+)

- 对录像先进行一轮预压缩（此时压缩率能够达到15%左右）
- 可选 gzip, bzip2, lzma 二次压缩，默认采用 lzma 进行二次压缩（此时压缩率接近8%）
- 1字节: 大版本号
- 4字节: `prefix`
- 1字节: 模式
- 对于自定义, 用额外的字节存储参数

  - 1字节: 宽w
  - 1字节: 高h
- 雷的排布

  - 01串表示, 长度可以通过长宽推出来。通过排布可以推出雷数和3BV。
- `prestamp`

  - 由 `[]`标志的录像信息
- `preevent`

  - 2字节: `\x00\x01`表示 `preevent` 结束
- 事件列, 目前除了按键列其他都存的差分序列, 坐标序列差分后采取zigzag编码, 如果是某些时间段移动距离小的事件, 会把整个事件全部压缩到事件列表上面, 然后根据事件出现的频率进行了从小到大的编码 ~~（压缩什么的交给lzma）~~

  - 3个字节的预压缩数据总量（~~应该够了吧~~）
  - 按键序列（1-2个变长字节, 一般是一个字节）
  - 1字节 `\xff`表示按键序列结束（用来得出事件数量）
  - 时间戳差分序列（1-2个变长字节）
  - x坐标差分序列（1-2个变长字节）
  - y坐标差分序列（1-2个变长字节）
- `presuffix`
- 文件结尾的字符串录像信息, 只保留数据信息, 不保留文字说明信息
