# FINDINGS — Final Project — Minh Hoang Ho, Matias Guillen, William Wright, Adrian Emeterio

## Score

| Pool | found | total | % |
|------|------:|------:|--:|
| Released | 7 | 7 | 100% |
| Hidden | — | 20 | — |

**Command Run:**

```bash
$ source /opt/course/cocotb-env/bin/activate
$ cd craft-vv-student/code
$ just mutate trojan
[baseline] running clean secure_gate_clean.sv through trojan ...
  clean RTL: 5 tests passed.

  [found  ] key_always_ok        (test-failed)  -- gate ignores the key and is always unlocked
  [found  ] key_compare_low16    (test-failed)  -- key check compares only the low 16 bits (near-miss keys unlock)
  [found  ] unlock_inverted      (test-failed)  -- unlocked is inverted (wrong key opens, right key locks)
  [found  ] data_leak_when_locked (test-failed)  -- data_out always passes data_in (no masking while locked)
  [found  ] data_zero_when_unlocked (test-failed)  -- data path inverted: outputs zero when unlocked, data when locked
  [found  ] count_never_increments (test-failed)  -- access_count is stuck (never advances while unlocked)
  [found  ] count_increments_when_locked (test-failed)  -- access_count advances every cycle, even while locked

==== found/total = 7/7  =  100.0%  (threshold 90%) ====
```

## Survivors

No mutant in the released pool survived, so the rows below are bugs we think our program would miss.

| Mutant | What It Changes | Reachable By My Stimulus? | Observable By My Checks? | Why It Survived |
|--------|-----------------|---------------------------|--------------------------|-----------------|
| A backdoor on a key we did not test | The gate unlocks on some other secret 32 bit key | No | Yes | Random keys almost never hit one exact value out of 2^32, which makes this a reachability gap. test_random_keys even passes on the trojan variant by itself. The formal proof of P1 and P2 covers every key and would catch it |
| A bug only at a DW or EXPECTED_KEY other than the default | Something like the masking breaking at DW = 16 | No | Yes | We only test the default size and key so a bug that needs other values never happens, which makes this a reachability gap |
| A bug only before the first reset | The outputs are wrong at power up | No | Yes | Every test resets first so this state is never reached, which makes this a reachability gap |

## What I Changed, And What It Bought

| Change | Score Before | Score After | Which Survivors It Caught |
|--------|-------------:|------------:|---------------------------|
| Added test_final.py with test_random_keys and test_count_wrap on top of the starter smoke test | 7 / 7 | 7 / 7 | None new since our smoke only run already found all 7 released mutants, so the hidden pool is where these tests matter |
| Added test_magic_key | 7 / 7 | 7 / 7 | No pool mutant, but it holds the magic key across a rising edge so the no_leak assertion fires on the trojan |

## Residual Risk

1. Our simulation would not catch a backdoor on a trigger value we do not know about because random keys can not hit one exact 32 bit value, which makes this a reachability gap. Only the formal proof covers it.
2. Our code would not catch bugs that only show up at other DW or EXPECTED_KEY values because we only test the defaults, which makes this a reachability gap.
3. Our code would not catch a glitch in the middle of a cycle because we only read the outputs once per cycle, which makes this an observability gap.
4. Our code would not catch anything that goes wrong before the first reset because every test resets first, which makes this a reachability gap.
5. Our code would not catch a backdoor that leaks through timing or power because we only check the output values, which makes this an observability gap.

**If I Had Another Day:** Run the tests and the formal proof again at a couple of other DW and EXPECTED_KEY values since that is the biggest gap we can close.