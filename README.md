# AVF 压缩格式 V1.2 (Python 实现)

## 使用说明

项目根目下的avfcomp为包目录

```python
from avfcomp import AVFComp, AVFDecomp

# compress
path = "your/path/raw.avf"
cvf = AVFComp()
cvf.process_in(path)
cvf.process_out("comp.cvf")

# decompress
path = "your/path/comp.cvf"
avf = AVFDecomp()
avf.process_in(path)
avf.process_out("raw.avf")
```

## 格式说明 (目前支持 Arbiter 0.52+)

- 整体使用 lzma 编码

- 1字节：大版本号

- 4字节：`prefix`

- 1字节：模式

- 对于自定义，用额外的字节存储参数
  - 1字节：宽w
  - 1字节：高h

- 雷的排布
  - 01串表示，长度可以通过长宽推出来。通过排布可以推出雷数和3BV。

- `prestamp`
  - 由 `[]`标志的录像信息
- `preevent`
  - 2字节：\x00\x01表示 `preevent` 结束

- 事件列，目前除了按键列其他都存的差分序列，坐标序列差分后采取zigzag编码
  - 按键序列（每个1字节）
  - 1字节\0表示按键序列结束（即可得出事件数量）
  - 1字节表示每个时间戳差分值需要的字节数量 `byte_len_dt`
  - 时间戳差分序列（每个 `byte_len_dt` 字节）
  - 1字节表示每个x坐标差分值所需的字节数量 `byte_len_dx`
  - x坐标差分序列（每个 `byte_len_dx` 字节）
  - 1字节表示每个y坐标差分值所需的字节数量 `byte_len_dy`
  - y坐标差分序列（每个 `byte_len_dy` 字节）

- `presuffix`

- 文件结尾的字符串录像信息，只保留数据信息，不保留文字说明信息
