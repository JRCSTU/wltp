from boltons.iterutils import first
from wltp import autograph, cycles, pipelines


def test_preserve_ops():
    aug = autograph.Autograph()
    op = pipelines.calc_wltc_distances
    got = first(aug.yield_wrapped_ops(op))
    assert got == op
    assert got.needs == op.needs
    assert got.provides == op.provides
