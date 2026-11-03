# Simulation track

Spec: `docs/superpowers/specs/2026-10-20-simulation-track-design.md` (r1).
Plan: `docs/superpowers/plans/2026-10-20-simulation-a-implementation.md`.
ODD: `docs/simulation/ODD.md`. Operational rules: `docs/simulation/simulation_a_rules.md`.

Simulated outputs are never field observations (spec §2).

## Toolchain

| Tool | Version | Location |
|---|---|---|
| GAMA | 2025.06.4, Windows, bundled JDK (Eclipse Adoptium OpenJDK 21.0.7+6) | `D:\tools\GAMA_2025.06.4\headless\gama-headless.bat` |
| R | R version 4.6.1 (2026-06-24 ucrt) | `C:\Users\admin\AppData\Local\Programs\R\R-4.6.1\bin\Rscript.exe` (wrapper `D:\vcpf\bin\Rscript.cmd`) |
| R packages | data.table 1.18.6.1<br>glmmTMB 1.1.15.2<br>MASS 7.3.65<br>simr 1.0.11<br>abc 2.2.2<br>sensitivity 1.31.0<br>lhs 1.3.0<br>testthat 3.3.2<br>ggplot2 4.0.3 | user library (`R_LIBS_USER` = `C:\Users\admin\AppData\Local/R/win-library/4.6`) |

R install note: `winget install --scope user` reports "no applicable installer" for `RProject.R`, and the machine-scope install was cancelled because no one approved the UAC prompt. R was therefore installed per user by running the winget-downloaded, hash-verified, Authenticode-signed installer `R-4.6.1-win.exe` with `/CURRENTUSER /VERYSILENT /SUPPRESSMSGBOXES /NORESTART`.

## Local setup

1. Copy `simulation/local_paths.example.csv` to `simulation/local_paths.csv`. Git ignores the copy. Set `gama_headless` and `runs_root` in it.
2. Run outputs go to `runs_root/<cell_id>/rep_<n>/`, outside the repository. Generated cell files go to `runs_root/_cells/`, and XML plans and headless logs go to `runs_root/_plans/`.

## Headless launcher (GAMA 2025.06.4)

- `gama-headless.bat` resolves `..\plugins`, `..\GAMA.ini` and `.\configuration` relative to the current directory. It fails ("The system cannot find the file ..\GAMA.ini") unless the working directory is `D:\tools\GAMA_2025.06.4\headless`. Runner code must set the working directory to `dirname(gama_headless)` before calling it. This replaces the plan's `Set-Location D:\vcpf\runs` before the headless calls.
- Without `-ws`, the launcher creates a workspace `.work<random>` in the working directory (inside the GAMA install). Pass `-ws <dir>` to put it elsewhere, for example `-ws D:/vcpf/runs/_plans/ws`. Two concurrent headless processes sharing one `-ws` both finished with exit code 0 in the probe.
- `-help` (saved in `D:\vcpf\runs\gama_headless_help.txt`) lists these options: `-m [mem]`, `-ws [path]`, `-c`, `-v`, `-hpc [core]`, `-p`, `-ping_interval`, `-help`, `-version`, `-validate`, `-test`, `-socket [port]`, `-batch [experiment] [model.gaml]`, `-xml [experiment] [model.gaml] [out.xml]` and the default form `[plan.xml] [outputDirectory]`. `-hpc` and `-xml` both exist, so `run_headless()` (Task 7) passes `-hpc <cores>`. The probe ran its three simulations with `-hpc 3` in about 10 s of wall time.
- Default memory is `-Xmx16G` from `GAMA.ini` (`-m` overrides it).
- A model with compile errors makes `-xml` exit with code 13 and prints an empty error list ("Model didn't compile because of the following compilation errors:"). The reason is not shown. Bisect the model with small test models to find the failing idiom.
- `-xml` template (probe): `<Simulation experiment="headless_run" finalStep="1000" id=".." seed="1.0" sourcePath="..\probe.gaml"><Parameters><Parameter name="kv_file" type="STRING" value="" var="kv_file"/><Parameter name="rep_id" type="INT" value="0" var="rep_id"/></Parameters><Outputs/></Simulation>`. The `<Parameter>` attributes are `name`, `type`, `value`, `var`, the same names as `probe_plan.xml`.
- Fast compile check (about 8 s, no simulation): from the `headless` folder run `.\gama-headless.bat -ws <dir>/ws -xml headless_run <model.gaml> <dir>/template.xml`; exit code 0 means the model compiles. Under `cmd /c` the launcher needs the `.\` prefix. The headless runner in `analysis/R/gama_runner.R` (`run_headless()`) sets the working directory to `dirname(gama_headless)`, passes `-ws <out_dir>/ws` and calls the launcher by absolute path (`system2()` quotes the command itself, so do not `shQuote()` it).
- Output `timing.csv` holds `wall_ms` as cumulative wall milliseconds since the model's `init` (it is not reset per day); the time of day `d` is the difference of consecutive rows.

## Commands (repository root)

- R tests: `D:\vcpf\bin\Rscript.cmd tests/run_r_tests.R`
- Platform probe (Task 1 Step 10 of the plan, run with the working directory set to the GAMA `headless` folder for the two GAMA calls):
  - Delete old outputs first: `Remove-Item D:/vcpf/runs/_probe/probe_*.csv -ErrorAction SilentlyContinue`. A GAMA compile failure exits 13 and leaves earlier outputs in place, and the checker fails on any `probe_*.csv` older than `probe.gaml`, `probe_plan.xml` or `probe_kv.csv`.
  - `gama-headless.bat -ws D:/vcpf/runs/_probe/ws -xml headless_run D:/vcpf/repo/simulation/gama/VerticalFlow/models/probe.gaml D:/vcpf/runs/_probe/template.xml`
  - `gama-headless.bat -ws D:/vcpf/runs/_probe/ws -hpc 3 D:/vcpf/repo/simulation/probe/probe_plan.xml D:/vcpf/runs/_probe/out`
  - `D:\vcpf\bin\Rscript.cmd simulation/probe/check_probe.R D:/vcpf/runs/_probe` (prints `PROBE PASSED`)
- A0: `D:\vcpf\bin\Rscript.cmd analysis/R/experiments/a0_verify.R <cores>`
- Experiments: `D:\vcpf\bin\Rscript.cmd analysis/R/experiments/<driver>.R <pass_tag> <cores>`

## Seeds

`seed_for(cell_id, rep_id)` in `analysis/R/gama_runner.R` sets every seed. Each seed goes to GAMA through the `seed` attribute of the headless XML `<Simulation>` element.

`seed_for()` hashes the cell id with a 31-bit polynomial string hash `h` (`h <- (h * 131 + code point) %% 2147483647` over the code points, exact in doubles) and returns `(h * 10007 + rep_id) %% 2147483647`, with 0 mapped to 1. Seeds lie in 1..2147483646 and are distinct across replicates `0..10006` of one cell; `rep_id` outside that range is an error. Distinct cell ids can in principle share a seed (a 31-bit hash), which a campaign driver may check; the test suite checks 500 `first_morris_NNN` ids.

## Run keys and stale outputs

`run_cells()` writes `runs_root/<cell_id>/rep_<n>/run_key.txt` before a replicate is run. The key holds the md5 of the cell file, the model file and every input file named in the cell file (facility CSVs, protocols, schedule), plus the seed. A replicate is skipped only if its `timing.csv` has one row per day and its `run_key.txt` equals the current key. When a replicate is (re)scheduled, its folder is emptied first, so no output of an older cell or model survives. `collect_runs(cell_id, what, reps = NULL)` reads every `rep_<n>` folder by default; pass `reps` to read only those replicates and ignore folders left by an earlier, larger campaign.

## GAML idioms verified by the platform probe (GAMA 2025.06.4)

Two idioms from the plan failed and use a different working form. Tasks 7, 8 and 16 use the working form wherever their code would use the original.

| Idiom | Form used | Result |
|---|---|---|
| CSV to key-value map | `matrix m <- matrix(csv_file(path, ",", true)); if (m.rows > 0) { loop r from: 0 to: m.rows - 1 { kv[string(m[0, r])] <- string(m[1, r]); } }`. Always keep the `if (m.rows > 0)` guard | works; `string(m[0, r])` is the key and `string(m[1, r])` the value, the header row is skipped, `kv["n_agents"]` is `4`. A header-only CSV gives `m.rows = 0`, and an unguarded `loop r from: 0 to: m.rows - 1` then runs 2 phantom iterations (ranges count down); a header plus one data row gives `m.rows = 1` and one iteration |
| append a CSV row | `save list to: path format: "csv" rewrite: false header: false` | works; one line per call, appended |
| list of lists | `rows <+ [a, b]` appends one element | works; `length(rows[0])` is `3` |
| function-style action call | `twice(1.5)` inside the defining agent | works; `3.0`. Species-level `twice_w(1.0)` inside a `create` block also works |
| named `do` | `do bump(by: 3);` | works; `bumped` is `3` (a parameter named `by` compiles) |
| empty range loop | `loop k from: 0 to: -1` runs 2 iterations | runs 2 iterations, counting down through 0 and -1. GAML ranges iterate downward. Guard every `loop v from: lo to: hi` whose `hi` can fall below `lo` with `if (hi >= lo) { loop ... }` (for a count `n`: `if (n > 0) { loop i from: 0 to: n - 1 { ... } }`). The probe asserts the 2 iterations |
| closures | locals visible inside `create` and `ask` blocks | works; `create_closure` is `168` (4 x 42) and `ask_closure` is `28` (4 x 7) |
| random operators | `rnd_choice`, `poisson`, `binomial`, `gauss`, `rnd` | work; rep 1 (seed 777) drew `rnd_choice` 2, `poisson` 3, `binomial(10, 0.5)` 4, `gauss` -0.2808202764076406, `rnd(0.999)` 0.16005871451106105. `binomial(n, 1.0)` does not work, see the next table |
| seed reproducibility | identical draws for identical XML seeds | works; reps 1 and 2 (seed 777) gave identical `rnd_choice`, `poisson`, `binomial`, `gauss`, `rnd` and `walker_v_sum`, rep 3 (seed 778) differed. Both XML seed forms were verified: integer-style `seed="777"` and the template's `seed="1.0"` parse, and `"1.0"` / `"1"` (and `"777"` / `"777.0"`) give identical draws |
| CSV quoting of strings | `save` of a string with a space | not quoted; raw line `1,text_with_space,a b`. Commas, double quotes and newlines are also written raw (checked: `1,a,b,say "hi",x` then `y,plain` for the values `1`, `a,b`, `say "hi"`, `x<newline>y`, `plain`), which splits or corrupts the row. Strings written to CSV must not contain commas, quotes or newlines |
| `time` at cycle 3 | `time` with `step <- 10.0 #s` | `30.0` (cycle x step in seconds) |
| other idioms checked | `split_with`, `contains`, `contains_key`, `list_with`, `list[i] <- x`, `loop while: true` with `break`, `remove index: 0 from: q`, ternary `(a) ? b : c`, `min`/`max` of a list, `exp(ln(x))`, `sum` of an empty `collect` | all work; `sum(walker collect each.v)` on an empty species is `0.0` |

Idioms that differ from the plan (original form, working form):

| Original form | Working form | Reason |
|---|---|---|
| `machine_time` | `gama.machine_time` | `machine_time` alone is a compile error in 2025.06.4 (it is an attribute of the `gama` platform agent). `machine_time()` also fails to compile |
| `binomial(n, 1.0)` | `(p >= 1.0) ? n : binomial(n, p)` | `binomial(10, 1.0)` never returns: `Random.opBinomial` runs out of memory (`OutOfMemoryError: Requested array size exceeds VM limit`) and the whole headless process fails. Any `p` below 1.0 works (`0.0`, `0.5`, `0.999`, `1.0 - 1e-12`). The ternary evaluates only the taken branch, so the guard is safe. Guard every `binomial` call whose probability can reach 1.0 |
| `action load_x (string path)` and `csv_file(path, ...)` | `action load_x (string file_name)` and `csv_file(file_name, ...)` | `path` is a GAML built-in type name. An action parameter named `path` makes the model fail to compile with an empty error list (exit 13), found by bisecting `vertical_flow.gaml` into one-member variants. Do not name a variable or parameter after a GAML type (`path`, `file`, `list`, `map`, `matrix`, `graph`, `geometry`, `point`, ...) |
