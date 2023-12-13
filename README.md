# AVF 压缩格式 V1.1 (Python 实现)

## 使用说明

项目根目下的avfcomp为包目录

```python
from avfcomp import AVFComp, AVFDecomp

# compress
path = "your/path/raw.avf"
cvf = AVFComp.from_file(path)
cvf.process_out("compress.cvf")

# decompress
path = "your/path/comp.cvf"
avf = AVFDecomp.from_file(path)
avf.process_out("raw.avf")
```

## 格式说明

- 整体使用 lzma 编码

* 1字节：压缩算法
* 1字节：大版本号
* 4字节：`prefix`
* 1字节：模式
* 对于自定义，用额外的字节存储参数

  * 1字节：宽w
  * 1字节：高h
* 雷的排布

  * 01串表示，长度可以通过长宽推出来。通过排布可以推出雷数和3BV。
* `prestamp`
* 由 `[]`标志的录像信息
* `preevent`
* 1字节：\0表示事件列开始
* 事件列，目前除了按键列其他都存的差分序列

  * 按键序列（每个1字节）
  * 1字节\0表示按键序列结束（即可得出事件数量）
  * 时间戳序列（每个3字节）
  * x坐标序列（每个2字节）
  * y坐标序列（每个2字节）
* `presuffix`
* 文件结尾的字符串录像信息
