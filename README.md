# EEE4701/EEE5703 Verification & Validation Final Project

## Team Members

- Minh Hoang Ho
- William Wright
- Matias Guillen
- Adrian Emeterio

## Track

Track C — Using Assertions And Formal As Our Two Strategies

## Commits

All Commits To This Repo Were Pushed By Minh Hoang Ho But Every Member Wrote Their Own Part

- Minh Hoang Ho Wrote `sva/checker.sv`, `sva/bind.sv`, `formal/secure_gate.sby` & `formal/secure_gate_formal.sv`
- Matias Guillen, William Wright & Adrian Emeterio Wrote `test_final.py`
- The Write-Ups Were Done As A Group

## Where To Find The Files

Project Is Under `craft-vv-student/code/capstone/trojan/`

Everything Else In `craft-vv-student/` Is The Course Starter Packet

We Wrote Our Own `test_final.py` And `sva/` And `formal/` Files Instead Of Using The Ones From The Track C Guide And Only Changed The `Makefile` To Add `test_final` And The `SVA=1` Switch

```
craft-vv-student/code/capstone/trojan/
├── closure.md
├── CONTRIBUTIONS.md
├── FINDINGS.md
├── nonvacuity.md
├── proofs.md
├── README.md
├── SPEC.md
├── strategies.md
├── vplan.md
├── REPORT.pdf
├── test_final.py
├── test_smoke.py
├── secure_gate_clean.sv
├── secure_gate_trojan.sv
├── coverage.yml
├── mutants_released.yaml
├── lint.log
├── Makefile
├── formal/
│   ├── secure_gate.sby
│   ├── secure_gate_formal.sv
│   └── traces/
│       └── trojan_cex.vcd
└── sva/
    ├── bind.sv
    └── checker.sv
```

## How To Run

Run These From The `craft-vv-student/code/capstone/trojan/` Folder On Eustis

```bash
source /opt/course/cocotb-env/bin/activate
make
make SVA=1 SIM_BUILD=sim_build_sva
make SVA=1 SIM_BUILD=sim_build_sva_trojan DUT=$PWD/secure_gate_trojan.sv
```

The Default Seed Is 6434 And Can Be Changed With `make SEED=1234`

Running `make` Writes The Coverage Report To `coverage.yml`

The Mutation Score Is Run From The `craft-vv-student/code/` Folder

```bash
just mutate trojan
```

SymbiYosys Is Not Installed On Eustis So We Cloned The Matching Version Into Our Home Folder

```bash
git clone --branch yosys-0.33 https://github.com/YosysHQ/sby.git ~/sby
cd formal
python3 ~/sby/sbysrc/sby.py -f secure_gate.sby
```

## Results

- All 5 Tests Pass On The Clean Gate In About 21 Seconds
- Mutation Score Is 7/7 Released Mutants Found (100%)
- Hidden Pool Score Is —/20 (Fill In After Gradescope)
- Coverage Is 39/39 Bins (100%) By Cycle 300
- All 7 Assertions Hold On The Clean Gate And Every Cover Is Hit
- The no_leak Assertion Fires On The Trojan At 8329 ns
- Formal Proves P1, P2, And P3 On The Clean Gate And Finds The Trojan Key 0xDEADBEEF At Step 1
- Lint Is Clean With 1 Waiver For DECLFILENAME