# Verification Plan — Secure Gate

**Author:** Minh Hoang Ho, Matias Guillen, William Wright, Adrian Emeterio **Spec Version:** 20260831 REV 8B9D934 2026-08-31 **Date:** 11-24-2026

## 1. Scope

**In Scope:** We are testing the secure_gate at its default size, with DW = 8 and EXPECTED_KEY = 0xA5A5_1234. This covers the unlock rule, the masking of data_out, the access_count counter, reset, and the three security properties P1, P2, and P3 from SPEC.md. We run the same checks on both the clean variant and the trojan variant to show the checks pass on the clean one and catch the backdoor on the trojan one.

**Out Of Scope:** We are not testing other DW or EXPECTED_KEY values. We also do not check anything before the first reset or what happens in the middle of a clock cycle.

**Assumptions About The Environment:** The gate runs on a single 10 ns clock. Inputs change on the falling edge and the outputs are read 1 ns later. Reset is active low and synchronous. Every test starts with a reset. Any 32 bit key and any 8 bit data_in is a legal input since the spec says what happens for every key.

## 2. Feature List

| ID | Feature | Req | Priority | How It Is Verified |
|----|---------|-----|----------|--------------------|
| F1 | The right key unlocks the gate | Unlock rule | H | Directed tests, CRV, and the unlock assertion |
| F2 | Any other key keeps the gate locked, so there is no backdoor | Unlock rule and P1 (no backdoor) | H | Directed tests, CRV, the no_backdoor assertion, and formal |
| F3 | When unlocked data_out matches data_in | Masking rule | H | Scoreboard checks every cycle and the pass_data assertion |
| F4 | When locked data_out is 0, so no data leaks | Masking rule and P2 (no leak) | H | Scoreboard checks every cycle, the no_leak assertion, and formal |
| F5 | When access_count goes up by 1 on every unlocked cycle | Counter rule and P3 (counter integrity) | H | Scoreboard checks every cycle, the count_up assertion, and formal |
| F6 | When access_count stays the same on every locked cycle | Counter rule and P3 (counter integrity) | H | Scoreboard checks every cycle, the count_hold assertion, and formal |
| F7 | Reset clears access_count to 0 | Counter rule | H | CRV with random resets, the reset_count assertion, and formal |
| F8 | When access_count wraps from 255 back to 0 | The access_count row in the ports table | M | Directed test |
| F9 | The magic key 0xDEADBEEF does not unlock the clean gate | The planted trojan section | H | Directed tests, the SVA run on the trojan, and formal |

## 3. Coverage Model

| ID | Coverpoint | Bins | Why These Bins |
|----|-----------|------|----------------|
| C1 | What type of key was sent | Right key, high half only, low half only, one bit off, all zeros, all ones, and random | A plain random 32 bit key almost never comes close to the right key so the near miss types each get their own bin since that is where a weak key compare would hide |
| C2 | What type of data was sent | Zero, all ones, and other | A leak only shows up if data_in is not 0 and all ones checks that every bit is masked |
| C3 | Whether the gate was unlocked | 0 and 1 | Both the locked and unlocked sides of the contract have to be seen |
| C4 | Whether reset was on that cycle | 0 and 1 | Reset has to be hit during random cycles and not just at the start of a test |

**Crosses**

| ID | Cross | The Interaction It Is Aimed At |
|----|-------|-------------------------------|
| X1 | C1 crossed with C2 for 21 bins | Bugs where a near miss key leaks data, which can only be seen when the data is not 0 |
| X2 | C4 crossed with C3 for 4 bins | Bugs where reset does not clear the count when the gate is unlocked at the same time |

**Illegal / Ignore Bins:** There are none because the spec says what happens for every key and every data value so every bin is legal and should be hit

## 4. Test Matrix

| Test | Features | Kind | Pass Criterion |
|------|----------|------|----------------|
| test_security_property | F1, F2, F3, F4, F9 | Directed | Every wrong key including the near misses, the magic key, and 200 random keys keeps the gate locked with data_out at 0, and the right key unlocks, which is the starter test |
| test_access_count | F5, F6 | Directed | The count is 5 after 5 unlocked cycles, stays at 5 while locked, and is 7 after 2 more unlocked cycles, which is the starter test |
| test_random_keys | F1, F2, F3, F4, F5, F6, F7 | Random with pyvsc | 500 cycles with seed 6434, random resets in the middle of traffic, and no mismatches against the model on unlocked, data_out, or access_count |
| test_count_wrap | F5, F8 | Directed | The right key is held for 300 cycles and the count matches the model the whole way including the wrap at 255 |
| test_magic_key | F2, F4, F9 | Directed | The magic key is held across a rising edge and the gate stays locked with data_out at 0 |
| sva/checker.sv on the clean variant | F1, F2, F3, F4, F5, F6, F7 | Assertion | All 7 assertions hold through all 5 tests and every cover is hit at least once |
| sva/checker.sv on the trojan variant | F2, F4, F9 | Assertion | The no_leak assertion fires during test_magic_key |
| secure_gate.sby bmc task | F2, F4, F5, F6, F7 | Formal | No assertion fails in the first 20 cycles on the clean variant |
| secure_gate.sby prove task | F2, F4, F5, F6, F7 | Formal | The k-induction proof passes on the clean variant |
| secure_gate.sby trojan task | F2, F9 | Formal | BMC fails on the trojan variant and saves a counterexample trace |

## 5. Risk & Spec Ambiguity

| # | Ambiguity Or Risk | Where In The Spec | How I Resolved It | Residual |
|---|-------------------|-------------------|-------------------|----------|
| 1 | The spec does not say what happens when access_count goes past 255 | The access_count row in the ports table | We assumed it wraps back to 0 since it is an 8 bit counter and test_count_wrap checks it | If the intended behavior was to stop at 255 our model would be wrong |
| 2 | Random stimulus has almost no chance of hitting one 32 bit trigger value | The planted trojan section | We added a directed magic key test and proved P1 and P2 with formal so we do not depend on luck | A trigger we do not know about would only be caught by formal and not by simulation |
| 3 | Both DW and EXPECTED_KEY can be changed but we only test the defaults | The parameters section | We only test the defaults | Bugs that only show up at other values would not get caught |
| 4 | The spec says reset clears access_count but does not say what unlocked and data_out do if reset comes in the middle of traffic | The rst_n and access_count rows in the ports table | The spec defines unlocked and data_out only from the key and data_in, so we expect them to keep following the key during reset and only access_count goes back to 0. test_random_keys resets on about 4% of cycles and the scoreboard checks all three outputs on those cycles | If the intended behavior was to lock the gate during reset our model would be wrong |

## 6. Closure Criteria

- Functional Coverage Target: **100%** of the model in section 3
- Mutation Target: **18/20** on the hidden pool, which is the 90% threshold
- Assertions: Every property is paired with a cover and every cover has to be hit at least once
- What I Will Report As **Not Verified**: Any DW or EXPECTED_KEY other than the defaults, anything before the first reset, and glitches in the middle of a clock cycle

## 7. What This Plan Does Not Verify

This plan does not verify the gate with any DW or EXPECTED_KEY other than the defaults, so if a bug only shows up at a different size or key we would not catch it. We also do not check anything before the first reset or in the middle of a clock cycle since we only read the outputs once every cycle. The only trigger we drive in simulation is 0xDEADBEEF since that is the one we know about, so if there was a different hidden trigger only formal would find it, and formal also only runs with the defaults. We do not look at timing, power, or anything after synthesis either, so a backdoor that leaks through timing or power would not be seen.