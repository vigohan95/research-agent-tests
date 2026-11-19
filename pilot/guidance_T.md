# Agent instructions

## Testing conventions

- Statistical/numerical claims should be validated against an existing
  package or known closed-form result wherever possible (this project
  follows a test-driven-development norm for new models/statistical
  functions) — an internal-consistency-only test suite (e.g. "shape is
  right", "output is finite") is necessary but not sufficient.
- A regression test must fail on `main` and pass with the fix: run it on both,
  and check that each branch the change adds is guarded (alter the changed
  line and a test must fail). Parametrize over the cases the code branches on.
- Use `rtol`, and give a reason for every `atol` (the default `atol` of
  `np.isclose` is 1e-8 and treats small valid values as zero). Do not assert
  exact zero or NaN for a value that is zero only because of rounding, and do
  not assert on where an optimizer stops; compare at fixed parameters.
