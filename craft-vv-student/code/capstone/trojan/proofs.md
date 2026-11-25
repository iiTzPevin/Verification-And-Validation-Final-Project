# Proofs — Final Project — Minh Hoang Ho, Matias Guillen, William Wright, Adrian Emeterio

## 1. What We Ran

SymbiYosys is not installed on eustis, but yosys 0.33, z3, and yosys-smtbmc are. We downloaded the matching version of sby into our home folder and ran it from there.

```bash
$ git clone --branch yosys-0.33 https://github.com/YosysHQ/sby.git
$ cd craft-vv-student/code/capstone/trojan/formal
$ python3 ~/sby/sbysrc/sby.py -f secure_gate.sby
```

| Task | Variant | Mode | Depth | Result | Expected |
|------|---------|------|------:|--------|----------|
| bmc | Clean | BMC | 20 | PASS | PASS |
| prove | Clean | k-induction | 10 | PASS | PASS |
| trojan | Trojan | BMC | 10 | FAIL at step 1 | FAIL |

**Raw Output:**

```text
SBY 18:37:04 [secure_gate_trojan] summary: counterexample trace: secure_gate_trojan/engine_0/trace.vcd
SBY 18:37:04 [secure_gate_trojan] summary:   failed assertion secure_gate_formal.$assert$secure_gate_formal.sv:43$32 at secure_gate_formal.sv:43.22-43.51 in step 1
SBY 18:37:04 [secure_gate_trojan] DONE (FAIL, rc=0)
SBY 18:37:04 [secure_gate_prove] summary: successful proof by k-induction.
SBY 18:37:04 [secure_gate_prove] DONE (PASS, rc=0)
SBY 18:37:04 [secure_gate_bmc] summary: engine_0 (smtbmc z3) returned pass
SBY 18:37:04 [secure_gate_bmc] DONE (PASS, rc=0)
```

The trojan task says rc=0 because the .sby file marks it as expect fail, so the run counts as a success when the backdoor is caught.

## 2. Properties Proven

| Property | Spec Line | Formal Check | Clean | Trojan |
|----------|-----------|--------------|-------|--------|
| No backdoor | P1 | `formal/secure_gate_formal.sv` line 43 | Proven | Fails at step 1 |
| No leak | P2 | `formal/secure_gate_formal.sv` line 46 | Proven | Also broken, see section 4 |
| Count goes up when unlocked | P3 and the counter rule | `formal/secure_gate_formal.sv` line 49 | Proven | Not reached since BMC stopped at P1, see section 4 |
| Count holds when locked | P3 and the counter rule | `formal/secure_gate_formal.sv` line 52 | Proven | Not reached since BMC stopped at P1, see section 4 |
| Reset clears the count | The counter rule | `formal/secure_gate_formal.sv` line 55 | Proven | Not reached since BMC stopped at P1 |

The wrapper uses a few registers (started, last_rst_n, last_unlocked, last_count) to save last cycle's values, so the counter checks compare this cycle to the cycle before.

## 3. Every Assume

There are no assume statements in our formal files. key, data_in, and rst_n are left completely free so the solver can try every value on every cycle, including the magic key.

| # | Assume | What It Rules Out | Why That Is Safe |
|---|--------|-------------------|------------------|
| None | None | Nothing | Lecture 5 showed that one assume can hide a backdoor, so we did not use any. The only setup is `reg started = 1'b0`, which is a starting value and not an assume, and it only makes the counter checks wait one cycle so last_count has a real value before it gets used |

## 4. Counterexample

Saved trace: `formal/traces/trojan_cex.vcd`

```bash
$ grep -n "key" secure_gate_trojan/engine_0/trace_tb.v
57:    PI_key = 32'b11011110101011011011111011101111;
```

The solver set the key to 11011110101011011011111011101111, which is 0xDEADBEEF in hex. That is not EXPECTED_KEY, but line 29 of secure_gate_trojan.sv has `assign backdoor = (key == MAGIC_KEY);` and line 30 ORs it into unlocked, so the gate opens. That breaks the P1 check on line 43. The solver was never told about the magic key, it tried every key and found the one that opens the gate on its own.

On that same cycle the gate also passes data_in to data_out with the wrong key, so P2 is broken too. BMC stops at the first failed check so only P1 shows up in this run. Our SVA run on the trojan shows the P2 side, where the no_leak assertion fired at 8329 ns during test_magic_key.

P3 does not break on the trojan. The backdoor only changes unlocked, and the counter in the trojan still goes up only when unlocked is 1, just like the clean one. So when the magic key opens the gate the count goes up by 1, which is what P3 says should happen on an unlocked cycle. The trojan breaks who is allowed in, not how the visits are counted, so P1 and P2 catch it and P3 does not.

## 5. What These Proofs Do Not Establish

The proofs only cover the default DW = 8 and EXPECTED_KEY = 0xA5A5_1234, so other values are not proven. They only cover the two RTL files we were given and not any other version of the design. The unlock rule in the other direction (the right key always opens the gate) and the pass through of data while unlocked are not in the formal file, so those are only checked by the assertions and the scoreboard in simulation. Formal also treats the design one clock cycle at a time so it says nothing about glitches in the middle of a cycle.