"""生成一个最小 scvi stub：只提供 SATURN 需要的 ZeroInflatedNegativeBinomial

为什么：
    SATURN 的 `model/saturn_model.py:10` 只用 `from scvi.distributions import
    ZeroInflatedNegativeBinomial`。而完整 `scvi-tools` 依赖 jax + numpyro
    + 整个 scvi 包（几百 MB，本地下载极慢）。

    实测 `scvi/distributions/_negative_binomial.py` 里：
      - `NegativeBinomial` 与 `ZeroInflatedNegativeBinomial` 是**纯 torch** 实现；
      - 只额外用到 `settings.warnings_stacklevel`（一个 int）和同目录的
        `_utils.py` / `_constraints.py`（都是纯 torch）。
      - jax / numpyro 只被 `JaxNegativeBinomialMeanDisp` 用。

做法：
    从 wheel 解出的源码里切出类定义，去掉 jax/numpyro 依赖，装成 `scvi` stub。
    这样得到的是**与官方逐字一致**的 log_prob，不是自己猜的公式。

用法：
    python scripts/make_scvi_stub.py
"""
from __future__ import annotations

import io
import re
import shutil
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tmp" / "scvix" / "scvi" / "distributions"
DEST = ROOT / ".venv39" / "Lib" / "site-packages" / "scvi"


def main() -> int:
    nb = SRC / "_negative_binomial.py"
    if not nb.exists():
        print("缺 wheel 解包目录：", SRC)
        return 2
    lines = nb.read_text(encoding="utf-8").splitlines()

    # 定位两个类
    def find(cls: str) -> int:
        for i, l in enumerate(lines):
            if l.startswith(f"class {cls}"):
                return i
        return -1

    i_nb = find("NegativeBinomial(")
    i_zinb = find("ZeroInflatedNegativeBinomial(")
    i_mix = find("NegativeBinomialMixture(")
    if min(i_nb, i_zinb, i_mix) < 0:
        print("类定位失败", i_nb, i_zinb, i_mix)
        return 3
    seg = lines[i_nb:i_mix]
    # 类体依赖三个模块级函数：log_zinb_positive / log_nb_positive / _gamma
    # 行号按 scvi-tools 1.1.6 实测定位（1-based）：26-119、247-254
    helpers = lines[25:119] + [""] + lines[246:254]
    body = ("\n".join(helpers) + "\n\n" + "\n".join(seg))
    # 只在**类型注解**里出现 jnp.ndarray（源码 `from __future__ import annotations`
    # 下注解是字符串，不触发 import）。替换成 torch.Tensor，语义不变。
    body = body.replace("jnp.ndarray", "torch.Tensor")
    # 只检查真正来自 jax/numpyro 的符号；`self._validate_sample` 是 torch 原生方法，不算
    for bad in ("jnp.", "numpyro", "promote_shapes", "jax.", " dist."):
        if bad in body:
            print(f"!! 类体里出现 {bad}，需要人工处理")
            return 4

    header = (
        '"""Minimal scvi.distributions stub (NegativeBinomial + ZeroInflatedNegativeBinomial).\n\n'
        '切自 scvi-tools 1.1.6 `scvi/distributions/_negative_binomial.py`，'
        '去掉了 jax/numpyro 依赖。\n'
        '"""\n'
        "from __future__ import annotations\n\n"
        "import warnings\n\n"
        "import torch\n"
        "import torch.nn.functional as F\n"
        "from torch.distributions import Distribution, Gamma, constraints\n"
        "from torch.distributions import Poisson as PoissonTorch\n"
        "from torch.distributions.utils import (\n"
        "    broadcast_all,\n"
        "    lazy_property,\n"
        "    logits_to_probs,\n"
        "    probs_to_logits,\n"
        ")\n\n"
        "from scvi import settings\n"
        "from ._constraints import optional_constraint\n\n\n"
    )

    DEST.mkdir(parents=True, exist_ok=True)
    dist_dir = DEST / "distributions"
    dist_dir.mkdir(parents=True, exist_ok=True)

    (DEST / "__init__.py").write_text(
        '"""Minimal local scvi stub.\n\n'
        '只为了让 SATURN 的 `from scvi.distributions import ZeroInflatedNegativeBinomial`\n'
        '能跑起来，不含 scvi-tools 的模型/数据功能。\n"""\n'
        "from types import SimpleNamespace\n\n"
        "# 下游只用到 warnings_stacklevel（传给 warnings.warn 的 stacklevel）\n"
        "settings = SimpleNamespace(warnings_stacklevel=2)\n\n"
        '__version__ = "1.1.6-stub"\n',
        encoding="utf-8")

    (dist_dir / "_nb_stub.py").write_text(header + body + "\n", encoding="utf-8")
    for f in ("_utils.py", "_constraints.py"):
        shutil.copyfile(SRC / f, dist_dir / f)
    (dist_dir / "__init__.py").write_text(
        "from ._nb_stub import NegativeBinomial, ZeroInflatedNegativeBinomial\n\n"
        '__all__ = ["NegativeBinomial", "ZeroInflatedNegativeBinomial"]\n',
        encoding="utf-8")

    print("已生成 stub:", DEST)
    print("  distributions/_nb_stub.py 行数:", len((header + body).splitlines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())