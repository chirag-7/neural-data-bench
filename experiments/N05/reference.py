"""Audited deterministic NWB/HDF5 extraction; no model output is used here."""
import h5py
import numpy as np

SWEEPS = [19, 20, 21, 22, 23, 24]

def _text(value):
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)

def extract(nwb_path):
    answer = {"nwb_version": None, "sweeps": {}}
    with h5py.File(nwb_path, "r") as f:
        answer["nwb_version"] = _text(f["nwb_version"][()])
        for number in SWEEPS:
            response = f[f"acquisition/timeseries/Sweep_{number}"]
            stimulus = f[f"stimulus/presentation/Sweep_{number}"]
            rd, sd = response["data"], stimulus["data"]
            rate = float(response["starting_time"].attrs["rate"])
            assert rate == float(stimulus["starting_time"].attrs["rate"])
            v = np.asarray(rd, dtype=np.float64) * float(rd.attrs["conversion"]) * 1000
            current = np.asarray(sd, dtype=np.float64) * float(sd.attrs["conversion"]) * 1e12
            assert _text(rd.attrs["unit"]) == "Volts"
            assert _text(sd.attrs["unit"]) == "Amps"
            assert len(v) == len(current) == int(response["num_samples"][()])
            holding = np.median(current)
            # Main negative pulse is the longest contiguous below-holding run.
            mask = current < holding - 1e-6
            changes = np.diff(np.r_[False, mask, False].astype(np.int8))
            starts, stops = np.flatnonzero(changes == 1), np.flatnonzero(changes == -1)
            idx = int(np.argmax(stops - starts))
            start, stop = int(starts[idx]), int(stops[idx])
            pre = int(round(.05 * rate))
            assert start >= pre
            vrest = float(np.mean(v[start-pre:start]))
            ihold = float(np.mean(current[start-pre:start]))
            answer["sweeps"][str(number)] = {
                "sampling_rate_hz": rate,
                "n_samples": int(len(v)),
                "dt_seconds": 1 / rate,
                "response_stored_unit": _text(rd.attrs["unit"]),
                "stimulus_stored_unit": _text(sd.attrs["unit"]),
                "main_pulse_onset_s": start / rate,
                "main_pulse_duration_s": (stop - start) / rate,
                "main_pulse_amplitude_pa": float(np.mean(current[start:stop]) - ihold),
                "pre_stimulus_voltage_mv": vrest,
                "mean_pulse_voltage_deflection_mv": float(np.mean(v[start:stop]) - vrest)
            }
    return answer
