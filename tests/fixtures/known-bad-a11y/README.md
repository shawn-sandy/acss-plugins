# known-bad-a11y fixture

Used by `tests/run_axe.mjs --self-test` to verify the jsdom + axe-core
harness can still detect at least one serious or critical violation. If
this fixture starts passing axe, the harness has regressed — investigate
before trusting any green result on real component output.

The deliberate violations are documented inline in `violation.html`.
