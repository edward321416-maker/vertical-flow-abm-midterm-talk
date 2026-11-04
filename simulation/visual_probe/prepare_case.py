#!/usr/bin/env python3
"""One-run GAMA visual-capture fixture: synthetic inputs, original model choices.

This is NOT the original four-day E1 replicate and NOT a reproduction of the
published 200-run mean. It is an independently seeded, executable smoke run
of the same GAML movement model with a visual-only experiment appended.
"""
import csv
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

base = Path(sys.argv[1]).resolve()
model = Path(sys.argv[2]).resolve()
inputs = base / "inputs"
outputs = base / "model_output"
inputs.mkdir(parents=True, exist_ok=True)
(outputs / "rep_0").mkdir(parents=True, exist_ok=True)

def csv_write(name, headers, rows):
    with (inputs / name).open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(headers)
        writer.writerows(rows)

csv_write("floors.csv",
    ["floor_code", "floor_index", "area_m2", "x_fnb", "dwell_offset", "elevator_served"],
    [[f"S{i:02}", i, 5000, 0.05, 0, 1] for i in range(9)])
csv_write("boundaries.csv",
    ["boundary_index", "boundary_id", "from_floor", "to_floor",
     "boundary_order", "esc_up", "esc_down", "stair_ok"],
    [[i, f"B{i+1}", i, i+1, i+1, 1, 1, 1] for i in range(8)])
csv_write("entries.csv",
    ["entry_id", "entry_floor_idx", "entry_floor", "entry_share"],
    [["E0", 0, "S00", 1.0]])
csv_write("blocks.csv", ["block_id", "block_start_min", "block_end_min"], [["all", 0, 240]])
csv_write("day_profile.csv", ["hour", "weekday", "weekend"],
    [[hour, 1.0 if hour < 4 else 0.0, 1.0 if hour < 4 else 0.0] for hour in range(24)])
csv_write("facility.csv", ["key", "value"], [["open_min", 0]])

params = {
    "cell_id": "actual_gama_visual_smoke_gamma0_cont",
    "out_root": str(outputs), "protocols_file": str(inputs / "empty_protocols.csv"),
    "schedule_file": str(inputs / "empty_schedule.csv"),
    "floors_file": str(inputs / "floors.csv"),
    "boundaries_file": str(inputs / "boundaries.csv"),
    "entries_file": str(inputs / "entries.csv"), "blocks_file": str(inputs / "blocks.csv"),
    "day_profile_file": str(inputs / "day_profile.csv"),
    "facility_file": str(inputs / "facility.csv"),
    "n_days": 1, "day_types": "WD", "sim_end_min": 240,
    "alpha": 1.4, "beta": 0.7, "gamma": 0,
    "delta_down": 0.4, "theta0": -3.0, "theta1": 0.06, "theta2": 0,
    "imp_escalator": 1.0, "imp_stairs": 1.8, "imp_elevator": 1.4,
    "tau_escalator": 0.08, "tau_stairs": 0.14, "tau_elevator": 0.08,
    "mode_mu": 1, "elevator_enabled": 1,
    "base_rate_gpm": 5.0, "group_extra_mean": 0.0, "day_sd": 0.0,
    "dwell_meanlog": 2.8, "dwell_sdlog": 0.3,
    "esc_s": 25, "stair_s": 50, "elev_wait_mean_s": 60,
    "elev_s_per_floor": 6,
    "log_crossings": 0, "log_decisions": 0,
    "observers_enabled": 0, "x_fnb_random": 0,
    "x_fnb_low": 0, "x_fnb_high": 0.5,
}
csv_write("cell.csv", ["key", "value"], list(params.items()))
for missing in ["empty_protocols.csv", "empty_schedule.csv"]:
    (inputs / missing).write_text("unused,unused\n", encoding="utf-8")

plan = ET.Element("Experiment_plan")
sim = ET.SubElement(plan, "Simulation",
    id="0", sourcePath=str(model), finalStep="1445",
    experiment="visual_capture", seed="15125")
plist = ET.SubElement(sim, "Parameters")
ET.SubElement(plist, "Parameter", name="cell_file", var="cell_file",
              type="STRING", value=str(inputs / "cell.csv"))
ET.SubElement(plist, "Parameter", name="rep_id", var="rep_id", type="INT", value="0")
out = ET.SubElement(sim, "Outputs")
ET.SubElement(out, "Output", id="1", name="Upward_Boundaries", framerate="240")
ET.SubElement(out, "Output", id="2", name="Mall_Scene", framerate="240")
ET.ElementTree(plan).write(base / "plan.xml", encoding="utf-8", xml_declaration=True)
print("Prepared real GAMA run fixture:", base / "plan.xml")
print("Settings: synthetic 9 floors, gamma=0, continuous, 1 day of 4h, seed 15125")
