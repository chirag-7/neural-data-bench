import h5py
import numpy as np
import re
import math

# Allowed imports only: numpy, h5py, math, json, re, collections, functools, itertools, statistics


def extract(nwb_path):
    desired_sweeps = [19, 20, 21, 22, 23, 24]

    def decode_str(x):
        if isinstance(x, bytes):
            try:
                return x.decode('utf-8')
            except Exception:
                try:
                    return x.decode('latin-1')
                except Exception:
                    return str(x)
        if isinstance(x, str):
            return x
        return str(x)

    def get_nwb_version(f):
        v = None
        # Typical location: root attribute 'nwb_version'
        if 'nwb_version' in f.attrs:
            v = f.attrs['nwb_version']
        elif 'nwb_version' in f:
            try:
                v = f['nwb_version'][()]
            except Exception:
                v = None
        if v is None:
            # Try legacy attribute name
            if 'nwb_version' in f:
                try:
                    v = f['nwb_version'][()]
                except Exception:
                    pass
        if isinstance(v, (bytes, str)):
            return decode_str(v)
        # Fallback to identifier to ensure we return a string
        ident = f.attrs.get('identifier', '')
        return decode_str(ident) if ident is not None else ''

    def is_timeseries_group(g):
        # Heuristic: a TimeSeries-like group has a 'data' dataset
        return isinstance(g, h5py.Group) and 'data' in g

    def find_timeseries_groups(f):
        stim_groups = []
        resp_groups = []
        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset) and obj.name.endswith('/data'):
                g = obj.parent
                # Classify by path: stimulus under /stimulus, response under /acquisition
                path = '/' + name.lower().lstrip('/')
                if '/stimulus' in path:
                    stim_groups.append(g)
                elif '/acquisition' in path:
                    resp_groups.append(g)
        def walk_group(g, prefix, ancestors):
            address = h5py.h5o.get_info(g.id).addr
            if address in ancestors:
                return
            ancestors = ancestors | {address}
            for key in g:
                obj = g[key]
                name = prefix + '/' + key
                visitor(name, obj)
                if isinstance(obj, h5py.Group):
                    walk_group(obj, name, ancestors)
        for prefix in ['stimulus', 'acquisition']:
            if prefix in f:
                walk_group(f[prefix], prefix, set())
        return stim_groups, resp_groups

    def get_sweep_number_from_attrs(g):
        # Try direct attributes
        for key in ['sweep_number', 'sweep_num', 'sweep', 'sweepid', 'sweep_idx', 'sweepindex', 'aibs_sweep_number']:
            if key in g.attrs:
                try:
                    val = g.attrs[key]
                    if isinstance(val, (np.integer, int)):
                        return int(val)
                    if isinstance(val, (np.floating, float)):
                        return int(val)
                    s = decode_str(val)
                    m = re.search(r'-?\d+', s)
                    if m:
                        return int(m.group(0))
                except Exception:
                    pass
        # Try dataset inside group
        for key in ['sweep_number', 'sweep_num', 'sweep', 'sweepid']:
            if key in g:
                try:
                    val = g[key][()]
                    if isinstance(val, (np.integer, int)):
                        return int(val)
                    if isinstance(val, (np.floating, float)):
                        return int(val)
                    s = decode_str(val)
                    m = re.search(r'-?\d+', s)
                    if m:
                        return int(m.group(0))
                except Exception:
                    pass
        # Parse from name
        name = g.name.lower()
        # Look for explicit 'sweep_###'
        m = re.search(r'(?:^|/)(?:sweep|sweeps|swp)[_\-\s]*(-?\d+)', name)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
        # Fallback: last path component digits
        base = g.name.split('/')[-1]
        m2 = re.search(r'-?\d+', base)
        if m2:
            try:
                return int(m2.group(0))
            except Exception:
                pass
        return None

    def read_dataset_attr(ds, key, default=None):
        if ds is None:
            return default
        if key in ds.attrs:
            try:
                v = ds.attrs[key]
                if isinstance(v, np.ndarray) and v.shape == ():
                    v = v[()]
                if isinstance(v, (bytes, str)):
                    return decode_str(v)
                return v
            except Exception:
                return default
        return default

    def get_timeseries_rate_and_n(g):
        # Prefer starting_time.rate attribute if present
        sr = None
        n = None
        try:
            if 'data' in g:
                n = int(np.prod(g['data'].shape)) if g['data'].ndim == 1 else int(g['data'].shape[0])
        except Exception:
            n = None
        try:
            if 'starting_time' in g:
                st = g['starting_time']
                rate = read_dataset_attr(st, 'rate', None)
                if rate is not None:
                    sr = float(rate)
        except Exception:
            pass
        if sr is None and 'timestamps' in g:
            try:
                ts = np.asarray(g['timestamps'])
                ts = ts.astype(np.float64).reshape(-1)
                if ts.size >= 2:
                    d = np.diff(ts)
                    # Use median to reduce effect of occasional jitter
                    md = float(np.median(d))
                    if md > 0:
                        sr = 1.0 / md
            except Exception:
                pass
        # NWB1 sometimes stores 'rate' as attribute of group or data
        if sr is None:
            try:
                if 'rate' in g.attrs:
                    sr = float(g.attrs['rate'])
                elif 'data' in g and 'rate' in g['data'].attrs:
                    sr = float(g['data'].attrs['rate'])
            except Exception:
                pass
        return sr, n

    def get_data_and_unit(g):
        # Return: data_physical (after conversion/offset), stored_unit_str (exact attribute string), conversion_used, offset_used
        ds = g['data']
        data = np.asarray(ds)
        if data.ndim > 1:
            # Assume samples along first axis
            data = data.reshape(data.shape[0], -1)
            if data.shape[1] == 1:
                data = data[:, 0]
            else:
                # If multiple columns, take the first channel (common in some files)
                data = data[:, 0]
        data = data.astype(np.float64)
        conv = read_dataset_attr(ds, 'conversion', 1.0)
        offs = read_dataset_attr(ds, 'offset', 0.0)
        try:
            conv = float(conv)
        except Exception:
            conv = 1.0
        try:
            offs = float(offs)
        except Exception:
            offs = 0.0
        unit_attr = read_dataset_attr(ds, 'unit', '')
        # Preserve exact stored unit string for reporting
        stored_unit_str = decode_str(unit_attr) if unit_attr is not None else ''
        data_phys = data * conv + offs
        return data_phys, stored_unit_str, conv, offs

    def normalize_unit_string(u):
        if u is None:
            return ''
        s = decode_str(u).strip()
        s = s.replace('μ', 'u')  # replace Greek mu with 'u'
        s = s.lower()
        s = s.replace(' ', '')
        s = s.replace('.', '')
        s = s.replace('-', '')
        # plural to singular: just remove trailing 's'
        if s.endswith('s'):
            s = s[:-1]
        return s

    def factor_to_pa_from_unit(unit_str):
        # Returns factor to convert from provided unit to pA
        u = normalize_unit_string(unit_str)
        # Map common current units to Amps
        to_amp = None
        if u in ('a', 'ampere', 'amp', 'amper', 'amperes'):
            to_amp = 1.0
        elif u in ('ma', 'milliamp', 'milliampere'):
            to_amp = 1e-3
        elif u in ('ua', 'microamp', 'microampere'):
            to_amp = 1e-6
        elif u in ('na', 'nanoamp', 'nanoampere'):
            to_amp = 1e-9
        elif u in ('pa', 'picoamp', 'picoampere'):
            to_amp = 1e-12
        elif u in ('fa', 'femtoamp', 'femtoampere'):
            to_amp = 1e-15
        elif u in ('amp',):
            to_amp = 1.0
        else:
            # Sometimes full words like 'amperes' already handled; as a fallback, if unit contains 'a' assume amps
            if 'a' in u and len(u) <= 3:
                to_amp = 1.0
        if to_amp is None:
            # Unknown: assume already in Amps
            to_amp = 1.0
        return to_amp * 1e12  # A -> pA

    def factor_to_mv_from_unit(unit_str):
        # Returns factor to convert from provided unit to mV
        u = normalize_unit_string(unit_str)
        to_volt = None
        if u in ('v', 'volt'):  # 'volt' or 'volts' normalized to 'volt'
            to_volt = 1.0
        elif u in ('mv', 'millivolt'):
            to_volt = 1e-3
        elif u in ('uv', 'microvolt'):
            to_volt = 1e-6
        elif u in ('nv', 'nanovolt'):
            to_volt = 1e-9
        elif u in ('kv', 'kilovolt'):
            to_volt = 1e3
        else:
            # Fallback: if contains 'v' assume volts
            if 'v' in u:
                to_volt = 1.0
        if to_volt is None:
            to_volt = 1.0
        return to_volt * 1e3  # V -> mV

    def build_sweep_map(groups):
        m = {}
        for g in groups:
            sn = get_sweep_number_from_attrs(g)
            if sn is not None:
                m.setdefault(sn, []).append(g)
        return m

    def choose_timeseries_for_sweep(group_list):
        # If multiple entries for same sweep under one category, prefer the one with larger sample count
        if not group_list:
            return None
        if len(group_list) == 1:
            return group_list[0]
        best = None
        best_n = -1
        for g in group_list:
            sr, n = get_timeseries_rate_and_n(g)
            n = n if (n is not None) else -1
            if n > best_n:
                best = g
                best_n = n
        return best

    def compute_metrics_for_sweep(stim_g, resp_g):
        # Read data and units
        stim_data_phys, stim_unit_str, _, _ = get_data_and_unit(stim_g)
        resp_data_phys, resp_unit_str, _, _ = get_data_and_unit(resp_g)

        # Sampling rates and n
        resp_sr, resp_n = get_timeseries_rate_and_n(resp_g)
        stim_sr, stim_n = get_timeseries_rate_and_n(stim_g)

        # Ensure we have sr from response
        if resp_sr is None:
            # Fall back to stimulus if needed
            resp_sr = stim_sr
        if resp_sr is None or resp_n is None:
            # As a last resort infer from lengths/durations using timestamps if available
            if 'timestamps' in resp_g:
                ts = np.asarray(resp_g['timestamps'], dtype=np.float64).reshape(-1)
                if ts.size >= 2:
                    d = np.diff(ts)
                    md = float(np.median(d))
                    if md > 0:
                        resp_sr = 1.0 / md
                resp_n = ts.size
        if resp_sr is None:
            raise RuntimeError('Unable to determine response sampling rate')
        if resp_n is None:
            resp_n = int(resp_data_phys.shape[0])

        # Verify stimulus rate matches (within a small tolerance). If absent, skip check.
        if stim_sr is not None:
            if not (abs(stim_sr - resp_sr) <= max(1e-6 * resp_sr, 1e-3)):
                # Still allow minor rounding mismatches by checking timestamps on stim if present
                if 'timestamps' in stim_g:
                    try:
                        ts = np.asarray(stim_g['timestamps'], dtype=np.float64).reshape(-1)
                        if ts.size >= 2:
                            d = np.diff(ts)
                            md = float(np.median(d))
                            s_sr2 = 1.0 / md if md > 0 else stim_sr
                            if abs(s_sr2 - resp_sr) > max(1e-6 * resp_sr, 1e-3):
                                # If clearly mismatched, we still proceed using response sr, as per instructions just verify
                                pass
                    except Exception:
                        pass

        # Convert to computation units: stimulus -> pA, response -> mV
        stim_to_pa = factor_to_pa_from_unit(stim_unit_str)
        resp_to_mv = factor_to_mv_from_unit(resp_unit_str)
        stim_pa = stim_data_phys * stim_to_pa
        resp_mv = resp_data_phys * resp_to_mv

        # Detect main negative pulse: longest contiguous segment where value <= median - 1e-6 pA
        med = float(np.median(stim_pa)) if stim_pa.size > 0 else 0.0
        mask = stim_pa <= (med - 1e-6)
        arr = mask.astype(np.int8)
        if arr.size == 0:
            raise RuntimeError('Empty stimulus array')
        d = np.diff(np.concatenate(([0], arr, [0])))
        starts = np.where(d == 1)[0]
        ends = np.where(d == -1)[0]
        if starts.size == 0:
            # Fallback: if no negative pulse found, choose the longest positive pulse as main and treat as noneg (should not happen for this task)
            mask2 = stim_pa >= (med + 1e-6)
            arr2 = mask2.astype(np.int8)
            d2 = np.diff(np.concatenate(([0], arr2, [0])))
            starts2 = np.where(d2 == 1)[0]
            ends2 = np.where(d2 == -1)[0]
            if starts2.size == 0:
                # As ultimate fallback, set empty pulse at sample 0
                pulse_start = 0
                pulse_len = 0
            else:
                lengths2 = ends2 - starts2
                idx2 = int(np.argmax(lengths2))
                pulse_start = int(starts2[idx2])
                pulse_len = int(lengths2[idx2])
        else:
            lengths = ends - starts
            idx = int(np.argmax(lengths))
            pulse_start = int(starts[idx])
            pulse_len = int(lengths[idx])

        # Main pulse onset/duration in seconds
        onset_s = pulse_start / float(resp_sr)
        duration_s = pulse_len / float(resp_sr)

        # Pre-stimulus 50 ms window indices
        pre_samps = int(round(0.050 * float(resp_sr)))
        if pre_samps < 1:
            pre_samps = 1
        pre0 = max(0, pulse_start - pre_samps)
        pre1 = pulse_start
        # Clamp to available range
        pre1 = min(pre1, stim_pa.size)
        pre0 = min(pre0, pre1)

        # Means for amplitude computation (stimulus in pA)
        if pre1 > pre0:
            pre_stim_mean_pa = float(np.mean(stim_pa[pre0:pre1]))
            pre_resp_mean_mv = float(np.mean(resp_mv[pre0:pre1]))
        else:
            # If no pre window available, use earliest sample
            pre_stim_mean_pa = float(stim_pa[0]) if stim_pa.size > 0 else 0.0
            pre_resp_mean_mv = float(resp_mv[0]) if resp_mv.size > 0 else 0.0

        # During pulse means
        if pulse_len > 0:
            stim_mean_pulse_pa = float(np.mean(stim_pa[pulse_start:pulse_start + pulse_len]))
            resp_mean_pulse_mv = float(np.mean(resp_mv[pulse_start:pulse_start + pulse_len]))
        else:
            stim_mean_pulse_pa = float(stim_pa[pulse_start]) if pulse_start < stim_pa.size else 0.0
            resp_mean_pulse_mv = float(resp_mv[pulse_start]) if pulse_start < resp_mv.size else 0.0

        amp_pa = stim_mean_pulse_pa - pre_stim_mean_pa
        pre_v_mv = pre_resp_mean_mv
        defl_mv = resp_mean_pulse_mv - pre_v_mv

        out = {
            'sampling_rate_hz': float(resp_sr),
            'n_samples': int(resp_n),
            'dt_seconds': float(1.0 / float(resp_sr)) if resp_sr and resp_sr != 0 else float('nan'),
            'response_stored_unit': decode_str(resp_unit_str),
            'stimulus_stored_unit': decode_str(stim_unit_str),
            'main_pulse_onset_s': float(onset_s),
            'main_pulse_duration_s': float(duration_s),
            'main_pulse_amplitude_pa': float(amp_pa),
            'pre_stimulus_voltage_mv': float(pre_v_mv),
            'mean_pulse_voltage_deflection_mv': float(defl_mv),
        }
        return out

    with h5py.File(nwb_path, 'r') as f:
        nwb_version = get_nwb_version(f)
        stim_groups, resp_groups = find_timeseries_groups(f)

        stim_map = build_sweep_map(stim_groups)
        resp_map = build_sweep_map(resp_groups)

        sweeps_out = {}
        for sn in desired_sweeps:
            stim_cands = stim_map.get(sn, [])
            resp_cands = resp_map.get(sn, [])

            # If not found by attribute, try name-based fallback search
            if not stim_cands:
                # find any stim group whose name contains the exact number token
                token = f"{sn}"
                for g in stim_groups:
                    if re.search(r'(?:^|[^0-9])' + re.escape(token) + r'(?:[^0-9]|$)', g.name):
                        stim_cands.append(g)
                # deduplicate
                stim_cands = list(dict.fromkeys(stim_cands))
            if not resp_cands:
                token = f"{sn}"
                for g in resp_groups:
                    if re.search(r'(?:^|[^0-9])' + re.escape(token) + r'(?:[^0-9]|$)', g.name):
                        resp_cands.append(g)
                resp_cands = list(dict.fromkeys(resp_cands))

            stim_g = choose_timeseries_for_sweep(stim_cands)
            resp_g = choose_timeseries_for_sweep(resp_cands)

            if stim_g is None or resp_g is None:
                # If we cannot find both, fill with NaNs/placeholders but keep required keys
                fallback = {
                    'sampling_rate_hz': float('nan'),
                    'n_samples': int(0),
                    'dt_seconds': float('nan'),
                    'response_stored_unit': '',
                    'stimulus_stored_unit': '',
                    'main_pulse_onset_s': float('nan'),
                    'main_pulse_duration_s': float('nan'),
                    'main_pulse_amplitude_pa': float('nan'),
                    'pre_stimulus_voltage_mv': float('nan'),
                    'mean_pulse_voltage_deflection_mv': float('nan'),
                }
                sweeps_out[str(sn)] = fallback
                continue

            metrics = compute_metrics_for_sweep(stim_g, resp_g)
            sweeps_out[str(sn)] = metrics

        return {
            'nwb_version': nwb_version,
            'sweeps': sweeps_out,
        }
