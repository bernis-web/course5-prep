# 复现环境清单（2026-11-11）

- 操作系统：`Windows-11-10.0.22631-SP0`
- 主机：`韩先生的笔记本`
- 说明：**不依赖 GPU / WSL / docker**；纯 CPU 可跑完 30 个步骤。

## 解释器与依赖

| 环境 | 路径 | Python | numpy | scipy | scikit-learn | python-docx | python-pptx | PyMuPDF | h5py | pandas |
|---|---|---|---|---|---|---|---|---|---|---|
| python_venv39 | `D:\projects\course5-prep\.venv39\Scripts\python.exe` | 3.9.6 | 1.26.4 | 1.12.0 | 1.6.1 | 缺(ModuleNotFoundError) | 1.0.2 | 1.26.5 | 3.8.0 | 2.3.3 |
| python313 | `C:\Users\28417\AppData\Local\Programs\Python\Python313\python.exe` | 3.13.0 | 2.4.3 | 1.17.0 | 1.8.0 | 1.2.0 | 1.0.2 | 1.27.2.3 | 3.16.0 | 2.2.3 |

## requirements.txt 声明值

| 包 | 声明版本 |
|---|---|
| numpy | 2.4.3 |
| scipy | 1.17.0 |
| scikit-learn | 1.8.0 |
| python-docx | 1.2.0 |
| python-pptx | 1.0.2 |
| h5py | 3.16.0 |
| pandas | 2.2.3 |

## 一键入口

```powershell
cd D:\projects\course5-prep
powershell -ExecutionPolicy Bypass -File scripts\reproduce_oneclick.ps1
```

脚本做的事：选解释器 → 建 sandbox → 跑 30 步 → 校验退出码 → 打印 manifest 路径。
