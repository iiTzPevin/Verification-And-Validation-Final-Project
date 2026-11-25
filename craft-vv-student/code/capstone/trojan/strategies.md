# Strategies: Track C Group #15

## Strategy 1: Assertions

**What It Is, And Why Here.** We wrote a checker with 7 assertions and attached it to secure_gate with bind, so the rules get checked on every clock of every test without changing the RTL. Every assertion has a cover next to it so we can show it was actually checked and did not just pass because its condition never happened. Features F1 to F7 and F9 in our vplan call for it, since P1, P2, and P3 have to hold on every cycle and not just at the moments the scoreboard looks.

**What We Did.** The checker is in `sva/checker.sv` and `sva/bind.sv` connects it to the gate. `make SVA=1` runs all 5 tests on Verilator with the checker bound in, and the cover counts are in `nonvacuity.md`. We ran it on both the clean variant and the trojan variant.

**What It Showed.** On the clean variant all 7 assertions held through all 5 tests and every cover was hit, with the lowest at 31:

```text
[covers] what each `cover property` counted this run:
[covers]   count_hold_cover   line  39   count 572
[covers]   count_up_cover     line  35   count 433
[covers]   no_backdoor_cover  line  19   count 433
[covers]   no_leak_cover      line  27   count 510
[covers]   pass_data_cover    line  31   count 411
[covers]   reset_count_cover  line  43   count 31
[covers]   unlock_cover       line  23   count 433
```

On the trojan variant the no_leak assertion fired once test_magic_key held 0xDEADBEEF across a rising edge:

```text
  5263.00ns INFO     cocotb.regression                  test_random_keys passed
  8289.00ns INFO     cocotb.regression                  running test_magic_key (5/5)
[8329000] %Error: checker.sv:26: Assertion failed in secure_gate.u_sva.no_leak: 'assert' failed.
```

**What It Cannot Show.** The checker only checks the keys our tests send. test_random_keys ran 500 cycles on the trojan with the checker on and nothing fired, since random keys never hit 0xDEADBEEF. It only caught the backdoor because we wrote the magic key into a test by hand, so a different hidden trigger would get past it. It also only samples on the rising edge so it would miss a glitch in the middle of a cycle.

## Strategy 2: Formal

**What It Is, And Why Here.** We used SymbiYosys to check P1, P2, and P3 for every possible key on every cycle instead of only the keys we drive. Risk 2 in our vplan calls for it, since random stimulus has almost no chance of hitting one 32 bit trigger value, and features F2, F4, and F9 list formal as how they are verified.

**What We Did.** `formal/secure_gate_formal.sv` wraps the gate and has 5 checks, and `formal/secure_gate.sby` runs three tasks. bmc checks the clean variant for 20 cycles, prove runs k-induction on the clean variant, and trojan runs BMC on the trojan variant and is marked expect fail. There are no assume statements, so key, data_in, and rst_n are completely free. The counterexample is saved in `formal/traces/trojan_cex.vcd` and read back in `proofs.md`.

**What It Showed.** The clean variant passed both BMC and the proof, and the solver broke the trojan at step 1 with the key 0xDEADBEEF without ever being told about it:

```text
SBY 22:37:57 [secure_gate_trojan] summary:   failed assertion secure_gate_formal.$assert$secure_gate_formal.sv:43$32 at secure_gate_formal.sv:43.22-43.51 in step 1
SBY 22:37:57 [secure_gate_trojan] DONE (FAIL, rc=0)
SBY 22:37:57 [secure_gate_prove] summary: successful proof by k-induction.
SBY 22:37:57 [secure_gate_prove] DONE (PASS, rc=0)
SBY 22:37:58 [secure_gate_bmc] summary: engine_0 (smtbmc z3) returned pass
SBY 22:37:58 [secure_gate_bmc] DONE (PASS, rc=0)
```

**What It Cannot Show.** The proofs only cover the default DW = 8 and EXPECTED_KEY = 0xA5A5_1234. BMC stops at the first failed check, so on the trojan it only reports P1 even though P2 is broken on the same cycle. Our formal file has 5 checks while the checker has 7, so the right key always unlocking and data passing through while unlocked are only checked in simulation.

## What Each One Found That The Other Could Not

Formal found the backdoor at step 1 with no hint, while the checker went 500 random cycles on the trojan without firing and only caught it at 8329 ns because test_magic_key drove the key by hand. The checker covers more of the spec, with 7 properties against formal's 5, and its covers show how often each rule was really exercised, from 31 resets up to 572 locked cycles. Formal shows the rules hold for every key, which the checker could only ever show for the keys we tried.