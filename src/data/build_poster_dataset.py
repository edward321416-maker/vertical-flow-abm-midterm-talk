"""aik_boundary_rep.csv -> src/data/aik_boundary_rep.json 및 포스터 HTML 의 인라인 데이터 블록.

    python src/data/build_poster_dataset.py

시나리오 A = aik_e2_top1_g4_cont (최상층 집중), B = aik_e2_low3_g4_cont (저층 집중). 모든 값은 CSV 에서 계산하며 직접 입력한 숫자는 없다.
(명세의 alk_boundary_rep.csv 는 존재하지 않는 이름이라 실제 파일 aik_boundary_rep.csv 를 쓴다.)
"""
import collections
import csv
import json
import math
import os
import re

CSV = os.environ.get("AIK_BOUNDARY_REP_CSV", r"D:\vcpf\repo\analysis\outputs\sim\aik\aik_boundary_rep.csv")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "aik_boundary_rep.json")
HTML = os.path.join(os.path.dirname(HERE), "visualizer", "vertical_choreography_poster.html")
SCEN = {"A": ("aik_e2_top1_g4_cont", "최상층 집중 / Top-Heavy Anchor"), "B": ("aik_e2_low3_g4_cont", "저층 집중 / Bottom-Heavy Anchor")}


def quant(v, p):
    v = sorted(v)
    k = (len(v) - 1) * p
    f = int(k)
    return v[f] + (v[min(f + 1, len(v) - 1)] - v[f]) * (k - f)


rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
out = {
    "meta": {
        "title": "VERTICAL CHOREOGRAPHIES",
        "subtitle": "수직 동선의 안무 · 앵커 배치에 따른 층간 흐름 · 수직 동선을 거리처럼 펼친 시트",
        "model": "γ=4 연속형 · 100회 반복 평균 · 자료 aik_boundary_rep.csv",
        "source_csv": "aik_boundary_rep.csv",
        "gamma": 4,
        "n_runs": 100,
        "note": "명세의 alk_boundary_rep.csv 는 aik_boundary_rep.csv 의 오타로 보고 실제 파일을 사용했다.",
    },
    "labels": [f"{b}→{b+1}F" for b in range(1, 9)],
    "labels_ko": [f"{b}→{b+1}층" for b in range(1, 9)],
    "scenarios": {},
}
for key, (cid, name) in SCEN.items():
    sel = [r for r in rows if r["cell_id"] == cid]
    reps = sorted({int(r["rep_id"]) for r in sel})
    by = collections.defaultdict(dict)
    for r in sel:
        by[int(r["rep_id"])][int(r["boundary_order"])] = r
    bnds = []
    runs_u, runs_ev, runs_es = [], [], []
    for rid in reps:
        runs_u.append([float(by[rid][b]["U"]) for b in range(1, 9)])
        runs_ev.append([float(by[rid][b]["U_elev"]) / float(by[rid][b]["U"]) for b in range(1, 9)])
        runs_es.append([float(by[rid][b]["U_esc"]) / float(by[rid][b]["U"]) for b in range(1, 9)])
    prev = None
    for b in range(1, 9):
        us = [r[b - 1] for r in runs_u]
        n = len(us)
        m = {k: sum(float(by[rid][b][k]) for rid in reps) / n for k in ("U", "U_esc", "U_stairs", "U_elev")}
        mean = m["U"]
        sd = math.sqrt(sum((u - mean) ** 2 for u in us) / (n - 1))
        xs = [float(by[rid][b]["x_upper"]) for rid in reps]
        bnds.append({
            "b": b, "label": f"{b}→{b+1}F", "label_ko": f"{b}→{b+1}층",
            "flow": round(mean), "flow_mean": mean, "flow_sd": sd, "flow_p05": quant(us, 0.05), "flow_p95": quant(us, 0.95),
            "anchor": round(sum(xs) / len(xs), 2),
            "esc": m["U_esc"], "stairs": m["U_stairs"], "elev": m["U_elev"],
            "esc_share": m["U_esc"] / mean, "elev_share": m["U_elev"] / mean,
            "dominant_mode": "ESC" if m["U_esc"] > m["U_elev"] else "ELV",
            "retention_pct": None if prev is None else (round(mean) / prev - 1) * 100,
        })
        prev = round(mean)
    out["scenarios"][key] = {"id": cid, "name": name, "n_runs": len(reps), "boundaries": bnds,
                             "runs": {"U": [[round(v, 1) for v in r] for r in runs_u], "elev_share": [[round(v, 4) for v in r] for r in runs_ev],
                                      "esc_share": [[round(v, 4) for v in r] for r in runs_es]}}

json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved:", os.path.abspath(OUT_JSON), "| runs", {k: v["n_runs"] for k, v in out["scenarios"].items()})
for k in ("A", "B"):
    print(k, [(b["label"], b["flow"], b["anchor"], b["dominant_mode"]) for b in out["scenarios"][k]["boundaries"]])

if os.path.exists(HTML):                      # 인라인 데이터 블록 갱신(오프라인 실행용)
    t = open(HTML, encoding="utf-8").read()
    blob = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    t2, n = re.subn(r'(<script id="poster-data" type="application/json">)(.*?)(</script>)', lambda m: m.group(1) + blob + m.group(3), t, flags=re.S)
    if n:
        open(HTML, "w", encoding="utf-8").write(t2)
        print("inline data updated in", os.path.abspath(HTML))
