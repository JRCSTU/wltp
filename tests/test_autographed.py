from boltons.iterutils import first
from wltp import autograph, cycles, pipelines


def test_preserve_ops():
    aug = autograph.Autograph()
    ops = aug.wrap_funcs([cycles.calc_wltc_distances])
    got = aug.wrap_funcs(ops)
    assert got == ops
