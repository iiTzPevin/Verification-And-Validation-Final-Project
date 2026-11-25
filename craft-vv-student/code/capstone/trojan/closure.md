# Coverage Closure — Final Project — Minh Hoang Ho, Matias Guillen, William Wright, Adrian Emeterio

## 1. The Number

| Measure | Result |
|---|---|
| Coverpoints that were fully hit | 4 / 4 for key type, data type, unlocked, and reset |
| Cross of key type and data type | 21 / 21 bins |
| Cross of reset and unlocked | 4 / 4 bins |
| Goal from our vplan | 100% |
| Reached | 100% with 39 / 39 bins |
| Cycles it took to hit every bin | Between 200 and 300 cycles of test_random_keys with seed 6434 |
| Cycles that kept running after every bin was hit | About 200 more random cycles, from cycle 300 to cycle 500 |

**How The Report Was Produced:**

```bash
$ source /opt/course/cocotb-env/bin/activate
$ cd craft-vv-student/code/capstone/trojan
$ make
  3273.00ns INFO     cocotb.secure_gate                 cycle 100 coverage 89.7
  4273.00ns INFO     cocotb.secure_gate                 cycle 200 coverage 94.9
  5273.00ns INFO     cocotb.secure_gate                 cycle 300 coverage 100.0
  6273.00ns INFO     cocotb.secure_gate                 cycle 400 coverage 100.0
  7273.00ns INFO     cocotb.secure_gate                 cycle 500 coverage 100.0
  7273.00ns INFO     cocotb.secure_gate                 top : <cocotb_coverage.coverage.CoverItem object at 0x77f890bdc950>, coverage=39, size=39
  7273.00ns INFO     cocotb.secure_gate                    top.did_reset_x_unlocked : <cocotb_coverage.coverage.CoverCross object at 0x77f890bdcbc0>, coverage=4, size=4
  7273.00ns INFO     cocotb.secure_gate                       BIN (1, 1) : 2
  7273.00ns INFO     cocotb.secure_gate                    top.key_type_x_data_type : <cocotb_coverage.coverage.CoverCross object at 0x77f890ca9d90>, coverage=21, size=21
  7273.00ns INFO     cocotb.secure_gate                       BIN ('low_half_only', 'ones') : 4
  7273.00ns INFO     cocotb.secure_gate                       BIN ('one_bit_off', 'ones') : 4
```

The full bin counts are also saved in coverage.yml.

## 2. The Convergence Argument

**Shape Of The Curve:** The curve climbs fast at the start and is already at 89.7% by cycle 100 since most bins only need a common key type and a common data type. It slows down to 94.9% at cycle 200 because the only bins left are the ones that need two rare things to happen in the same cycle. It reaches 100% by cycle 300 and stays flat after that.

**The Last Bins To Close, And What It Took:** For seed 6434 the bin with the fewest hits was reset while unlocked with 2 hits. After that it was low half only with all ones data and one bit off with all ones data, with 4 hits each. These are the hardest bins to reach.

| Bin | Why It Was Rare | What I Changed To Hit It |
|-----|-----------------|--------------------------|
| Reset while unlocked (1, 1) | Reset is only on 4% of cycles and the right key is sent on 25% of cycles so both happen together about 1% of the time | We weighted the right key at 25% instead of leaving it to chance since a plain random key would almost never be the right key |
| Low half only with all ones data | The low half only key is 10% of cycles and all ones data is 15% so both happen together about 1.5% of the time | We made all ones its own data type at 15% instead of 1 out of 256 random values |
| One bit off with all ones data | Same reason as low half only since one bit off is also 10% of cycles | We made all ones its own data type at 15% instead of 1 out of 256 random values |
| All the near miss key bins | A plain random 32 bit key has almost no chance of matching half of the right key or being one bit away from it | We added the high half only, low half only, and one bit off key types with their own constraints |

**Why I Stopped Where I Stopped:** All 39 bins were hit by cycle 300 so the model was finished. We kept the test running to cycle 500 so a bad count from an early cycle could still get caught later, and the counter wrap test runs another 300 cycles to push the count past 255.

## 3. Bin Justification

| Bin | Illegal / Ignore | The Claim | Authority (Spec Line, Or The Argument) |
|-----|------------------|-----------|----------------------------------------|
| None | None | Every key and every data value is legal | The unlock, masking, and counter rules in SPEC.md say what the gate does for every key and every data value |

**Corner Bins That Are Legal And Must Be Covered, Not Excluded:** Reset while unlocked is legal since the spec says reset clears the count, so it has to be covered and not ignored. A wrong key with all zeros data is also legal and was covered, but it can not show a leak by itself since a leak of 0 looks the same as masking, which is why the cross also needs the all ones and other data bins.

## 4. What The Cross Is Aimed At

**The Bug The Key Type X Data Type Cross Is Aimed At:** It is aimed at a weak key compare that leaks data, like the key_compare_low16 mutant where a key that only matches the low half unlocks the gate. That bug can only be seen when a low half only key is sent with data that is not 0.

**A Bug It Would *Not* See, Even Fully Closed:** It would not see the trojan. The magic key 0xDEADBEEF just falls into the random key bin, so the cross can be at 100% without ever sending it.

## 5. Coverage VS. Correctness — The Blind Spots

1. **Specific Trigger Values:** The key type bins only track what kind of key was sent and not the exact value, so coverage reached 100% without ever sending 0xDEADBEEF. On the trojan variant the random test still passed with full coverage and only the magic key tests, the assertions, and formal caught it.
2. **The Counter Value:** There is no coverpoint on the counter value itself so coverage does not show that the counter ever got near 255. Only the counter wrap test pushes it past 255.
3. **Other DW And EXPECTED_KEY Values:** The bins are only built for the default size and key so a bug that only happens at other values would never show up.

**Transients In Particular:** Our model would miss a glitch where data_out or unlocked is wrong for a moment and then goes back to the right value because we only read the outputs once per cycle 1 ns after the falling edge. The SVA checker only samples at the rising edge so it would miss it too. To catch it we would need to check the outputs every time they change and not just once per cycle.

## 6. Correlation With Mutation

| | found / total |
|---|---|
| Before closing holes | 7 / 7 with only the smoke test |
| After closing holes | 7 / 7 with the full suite |

**Did Closing Holes Raise The Score?** No. All 39 bins were hit on the first full run so we did not have any holes left to close, and the smoke test alone already found all 7 released mutants so the released pool can not show any change. The interesting case is the trojan since coverage was at 100% and the scoreboard passed but the backdoor was still there, which makes it a reachability gap because the random stimulus never creates the magic key.

---

- [ X ] Every `illegal` and `ignore` bin in section 3 cites an authority.
- [ X ] Section 5 names blind spots of this design, not of coverage in general.
- [ X ] The numbers here agree with `coverage.yml` and `FINDINGS.md`.