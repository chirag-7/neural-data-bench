"""Prepare shared real NWB fixture and hidden audited extraction answers."""
from pathlib import Path
import hashlib
import importlib.util
import json
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "data/cache/N05"
SOURCE = REPO / "data/cache/D02/464212181_ephys.nwb"

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare():
    assert SOURCE.exists(), "Run experiments/D02/adapter.py to acquire the shared real fixture first"
    CACHE.mkdir(parents=True, exist_ok=True)
    alias = CACHE / "fixture.nwb"
    if alias.is_symlink() or alias.exists():
        alias.unlink()
    # Portable relative alias inside ignored repo cache; no duplicated 62MB raw file.
    alias.symlink_to(Path("../D02/464212181_ephys.nwb"))
    spec = importlib.util.spec_from_file_location("n05_reference", Path(__file__).with_name("reference.py"))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    expected = module.extract(alias)
    sweeps = json.loads((REPO / "data/cache/D02/sweeps.json").read_text())
    lookup = {str(r["sweep_number"]):r for r in sweeps["msg"]}
    previous = json.loads((REPO / "data/cache/D02/sweep-manifest.json").read_text())
    old = {str(r["sweep"]):r for r in previous}
    with np.load(REPO / "data/cache/D02/data.npz", allow_pickle=False) as data:
        mean_deflections = {}
        for split in ["train", "test"]:
            for row, number in enumerate(data[split+"_units"]):
                mean_deflections[str(number)] = float(data[split+"_y"][row].mean())
    checks = []
    for n, e in expected["sweeps"].items():
        r = lookup[n]
        assert abs(e["main_pulse_amplitude_pa"] - r["stimulus_absolute_amplitude"]) < 1e-5
        assert abs(e["main_pulse_onset_s"] - r["stimulus_start_time"]) < 1e-9
        # Official API duration reports last-minus-first, one sample shorter.
        assert abs(e["main_pulse_duration_s"] - r["stimulus_duration"]) <= 1.01 * e["dt_seconds"]
        assert abs(e["pre_stimulus_voltage_mv"] - old[n]["pre_stimulus_voltage_mv"]) < 1e-9
        assert abs(e["mean_pulse_voltage_deflection_mv"] - mean_deflections[n]) < 1e-9
        checks.append({"sweep":int(n), "amplitude_onset_crosschecked_official_EphysSweep":True, "duration_difference_one_sample":True, "voltage_baseline_crosschecked_D02_preparation":True, "deflection_mean_crosschecked_independent_blockaverages":True})
    (CACHE / "expected.json").write_text(json.dumps(expected, indent=2)+"\n")
    tolerance = {"sampling_rate_hz":{"atol":1e-6,"rtol":0}, "n_samples":{"atol":0,"rtol":0}, "dt_seconds":{"atol":1e-12,"rtol":0}, "main_pulse_onset_s":{"atol":1e-9,"rtol":0}, "main_pulse_duration_s":{"atol":1e-9,"rtol":0}, "main_pulse_amplitude_pa":{"atol":1e-5,"rtol":1e-8}, "pre_stimulus_voltage_mv":{"atol":1e-5,"rtol":1e-8}, "mean_pulse_voltage_deflection_mv":{"atol":1e-5,"rtol":1e-8}}
    (CACHE / "tolerances.json").write_text(json.dumps(tolerance, indent=2)+"\n")
    (CACHE / "validation.json").write_text(json.dumps({"checks":checks,"passed":True},indent=2)+"\n")
    meta = {"benchmark_id":"N05", "slice_id":"allen-nwb-loading-units-six-sweeps-v1", "metric":"field_accuracy", "direction":"higher", "task_type":"deterministic file-extraction code synthesis", "interface":"extract(nwb_path) -> JSON-serializable dict", "task_description":"Load the one supplied real Allen NWB file and extract scientifically defined physical units, sweep timing, current amplitude, prestimulus voltage and mean voltage deflection for six sweeps; see experiments/N05/task.json. This measures loading/calculation correctness, not neural inference or discovery.", "n_scored_fields":61, "n_sweeps":6, "n_independent_files":1, "grouping":"One source file and one neuron; fields and six sweeps are not independent dataset replications", "fixture_path":"data/cache/N05/fixture.nwb", "fixture_alias_target":"../D02/464212181_ephys.nwb", "underlying_benchmark_dependency":"D02", "dataset_group":"Allen Cell Types Database cell464212183, shared with D02 and collection overlapping K01", "dataset":"Allen Cell Types NWB; transparent new N05 fixture beyond originally mapped DANDI/IBL candidates", "raw_sha256":sha256(SOURCE), "allowed_runtime_file_reads":["passed NWB path only"], "runtime_dependencies":["numpy", "h5py==3.15.1"], "baseline":"Audited reference extraction using HDF5/NumPy plus official EphysSweep and independent D02 array crosschecks", "baseline_role":"deterministic correct reference has field_accuracy1 by construction; not an empirical specialistSOTA comparison", "current_best_status":"not applicable to a single constructed extraction case; reference is a verified calculation", "source_urls":["https://brain-map.org/support/documentation/cell-types-database-api","https://alleninstitute.github.io/AllenSDK/cell_types.html"], "license":"Allen Institute Terms of Use research/noncommercial with attribution; shared raw fixture not covered by code license", "terms_url":"https://alleninstitute.org/terms-of-use/", "limitations":["Only one known legacy NWB file, not held-out formats/labs", "Prompt supplies exact calculation definitions; no end-to-end autonomous scientific workflow", "Numeric fields share calculations and the same cell, so no field-wise population significance test", "Shared source with D02 means modality breadth or independent dataset counts must not be inflated", "Correct reference score is tautological under deterministic construction; distinguish from measured model results", "Reference answers are hidden during generation but retained in ignored cache for audit; public source data allow potential contamination"]}
    (CACHE / "metadata.json").write_text(json.dumps(meta, indent=2)+"\n")
    manifest = {"benchmark_id":"N05", "accessed_on":"2026-10-30", "dependency":"D02", "files":[{"url":"https://api.brain-map.org/api/v2/well_known_file_download/491202878", "path":"data/cache/N05/fixture.nwb", "alias_of":"data/cache/D02/464212181_ephys.nwb", "bytes":SOURCE.stat().st_size, "sha256":sha256(SOURCE)}], "reference_answers":{"path":"data/cache/N05/expected.json","sha256":sha256(CACHE/"expected.json")}, "crosscheck_sources":["data/cache/D02/sweeps.json","data/cache/D02/sweep-manifest.json","data/cache/D02/data.npz"], "data_terms":meta["license"], "terms_url":meta["terms_url"], "redistribution":"Raw file remains in ignored cache; N05 uses relative symlink to D02 without duplication"}
    (REPO / "data/manifests/N05.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return meta

if __name__ == "__main__":
    print(json.dumps(prepare(),indent=2))
