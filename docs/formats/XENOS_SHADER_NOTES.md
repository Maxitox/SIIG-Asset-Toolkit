# Xbox 360 compiled shader blobs

The 16 resources inside `shader.bin` are Xbox 360 Xenos compiled-shader containers. They begin with:

```text
+0x00  be u32 magic/stage   0x102A1100 pixel, 0x102A1101 vertex
+0x04  be u32 microcode offset
+0x08  be u32 microcode size
+0x10  be u32 metadata offset
+0x18  be u32 descriptor/control offset
```

For every supplied shader, `microcode_offset + microcode_size == file_size`. The blobs also preserve parameter names, `ps_3_0` / `vs_3_0` profiles, and compiler version `2.0.11164.0`.

`shader-info` validates the ranges, records the complete big-endian header words and printable metadata, hashes the microcode, and writes the raw microcode to a separate file. It intentionally does **not** claim to disassemble or translate the Xenos instruction set.

Validation: 16/16 parsed, comprising 9 pixel shaders, 7 vertex shaders, and 2,264 microcode bytes.
