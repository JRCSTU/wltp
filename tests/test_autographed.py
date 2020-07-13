from wltp import autograph, cycles


def test_preserve_ops():
    aug = autograph.Autograph()
    op = cycles.calc_capped_distances
    got = aug.wrap_fn(cycles.calc_capped_distances)
    assert got == op
    assert got.needs == op.needs
    assert got.provides == op.provides
