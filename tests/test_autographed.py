from wltp import autograph, cycles


def test_preserve_ops():
    aug = autograph.Autograph()
    op = cycles.calc_wltc_distances
    got = aug.wrap_fn(op)
    assert got == op
    assert got.needs == op.needs
    assert got.provides == op.provides
