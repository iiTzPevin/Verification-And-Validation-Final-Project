# Non-Vacuity Evidence — Final Project — Minh Hoang Ho, Matias Guillen, William Wright, Adrian Emeterio

## 1. Per-Property Evidence

Every property in `sva/checker.sv` has a `cover property` right next to it that covers the antecedent. The hit counts come from the clean run with `make SVA=1` on Verilator, which runs all 5 tests.

| # | Property | The Bug It Catches | Antecedent | Evidence Kind | Hits | Non-Vacuous? |
|---|----------|--------------------|------------|---------------|-----:|--------------|
| 1 | no_backdoor (P1) | The gate opening on any key that is not the right key, like the trojan's magic key | `unlocked` | cover | 433 | yes |
| 2 | unlock | The right key not opening the gate, like the unlock_inverted mutant | `key == EXPECTED_KEY` | cover | 433 | yes |
| 3 | no_leak (P2) | When data_out showing data while locked, like the data_leak_when_locked mutant | `key != EXPECTED_KEY && data_in != 0` | cover | 510 | yes |
| 4 | pass_data | When data_out being wrong while unlocked, like the data_zero_when_unlocked mutant | `unlocked && data_in != 0` | cover | 411 | yes |
| 5 | count_up (P3) | The count not going up on an unlocked cycle, like the count_never_increments mutant | `unlocked` | cover | 433 | yes |
| 6 | count_hold (P3) | The count going up on a locked cycle, like the count_increments_when_locked mutant | `!unlocked` | cover | 572 | yes |
| 7 | reset_count | Reset not clearing the count | `!rst_n` | cover | 31 | yes |

The covers for no_leak and pass_data also need data_in to not be 0, because a wrong key with data 0 would pass no_leak even if the gate leaked, so those cycles do not count as real evidence.

**Raw Evidence:**

```text
$ make SVA=1
                                                        ** TESTS=5 PASS=5 FAIL=0 SKIP=0                   10340.00          12.29        841.15  **
$ python3 ../../demos/wk07-s1-sva/show_covers.py coverage.dat
[covers] what each `cover property` counted this run:
[covers]   count_hold_cover   line  39   count 572
[covers]   count_up_cover     line  35   count 433
[covers]   no_backdoor_cover  line  19   count 433
[covers]   no_leak_cover      line  27   count 510
[covers]   pass_data_cover    line  31   count 411
[covers]   reset_count_cover  line  43   count 31
[covers]   unlock_cover       line  23   count 433
```

## 2. Corner Coverage

| Corner | Driven? | Times Reached | Which Properties It Arms |
|--------|---------|---------------|--------------------------|
| Right key sent | Yes | 129 in test_random_keys and 300 in test_count_wrap | no_backdoor, unlock, pass_data, count_up |
| Near miss keys (high half only, low half only, one bit off) | Yes | 134 in test_random_keys | no_leak, count_hold |
| Wrong key with data that is not 0 | Yes | 510 | no_leak |
| Reset while unlocked | Yes | 2 in test_random_keys | reset_count |
| When access_count wraps from 255 back to 0 | Yes | 1 in test_count_wrap | count_up |
| Magic key held across a rising edge | Yes | 1 in test_magic_key | no_leak, count_hold |
| Seeded random keys and data (breadth) | Yes | 500 cycles | All 7 |

**Seed(s) Used:** 6434 for test_random_keys, which is the default in test_final.py. test_smoke.py uses its own fixed seed of 0x5EC for its 200 random wrong keys.

## 3. Antecedents That Never Fired

Every property in section 1 has a nonzero hit count, so none of them passed without being checked.

## 4. What The Bound Contract Does Not Watch

**What The Scoreboard Covers That No Assertion Does:** For this design the assertions and the scoreboard check the same contract so they overlap a lot. The difference is when and where they look. The scoreboard only runs inside test_final.py and reads the outputs 1 ns after the falling edge, while the assertions watch every rising edge in all 5 tests, including the starter smoke tests that only check the count at a few points.

| Bug | Caught By | Why The Other Mechanism Misses It |
|-----|-----------|-----------------------------------|
| The count goes up by 2 on an unlocked cycle during the smoke tests | Caught by assertion #5 count_up | test_access_count only checks the count at 3 points and the scoreboard does not run during the smoke tests, so the assertion is the only check that runs every cycle there |
| The magic key opens the trojan during test_magic_key | Caught by assertion #3 no_leak and the test's own check | Both catch it here, but the assertion fires right at the rising edge and points to the exact line in checker.sv while the test only reports that it failed |
| The count is wrong right after a reset in the middle of random stimulus | Caught by scoreboard and assertion #7 reset_count | Both catch it, so this is a place where the two overlap and back each other up |

**Still Watched By Neither:** A glitch on data_out or unlocked in the middle of a cycle, since both only look once per cycle. Anything before the first reset, since the assertions are turned off while reset is low and the scoreboard starts after reset. A backdoor on a trigger value the stimulus never sends, which is only covered by the formal proof.

---

- [ X ] Every property in `sva/checker.sv` has a row in section 1.
- [ X ] Every row carries a hit count from a real run, not an expectation.
- [ X ] Any zero-hit antecedent appears in section 3 rather than being dropped.
- [ X ] On clean RTL, every assertion holds.
