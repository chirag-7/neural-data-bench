import h5py
import numpy as np
import math

def extract(nwb_path):
    def _d(val):
        if isinstance(val, bytes):
            return val.decode(errors='replace')
        return val

    def get_nwb_version(f):
        keys = list(f['/'].attrs)
        candidates = [k for k in keys if ('nwb_version' in _d(k).lower()) or ('nwb_version' in str(k).lower())]
        for k in candidates:
            return _d(f['/'].attrs[k])
        # Try file-level attribute by NWB1 convention
        for k in f['/'].attrs:
            if 'version' in _d(k).lower():
                return _d(f['/'].attrs[k])
        return 'unknown'

    def get_time_series_for_sweep(f, sweep_num):
        sweep_num_str = str(sweep_num)
        # Try NWB2.0 structure: /acquisition/timeseries and /stimulus/presented
        stim_candidates, resp_candidates = [], []
        # (1) Attempt to use /general/sweep_table
        if '/general/sweep_table' in f:
            st = f['/general/sweep_table']
            cols = {str(_d(n)):i for i,n in enumerate(st['colnames'][()])}
            df = st['data'][()]
            if isinstance(df, np.void) and hasattr(st['data'], 'shape'):
                df = st['data'][:]
            sweeps = st['sweep_number'][()] if 'sweep_number' in st else np.arange(len(df))
            try:
                idx = np.where(sweeps == sweep_num)[0][0]
                ts_inds = st['series'][idx]
                tspaths = [st['series/pointer'][i][0] for i in ts_inds if i<len(st['series/pointer'])]
                for path in tspaths:
                    p = _d(path)
                    if '/acquisition/' in p:
                        resp_candidates.append(p)
                    elif '/stimulus/' in p:
                        stim_candidates.append(p)
            except Exception:
                pass
        # (2) Fall back on naming/search convention
        def scan_for_candidates(group, is_resp):
            result = []
            for k in group:
                obj = group[k]
                # Match 'Sweep_{N} ...' or similar
                kstr = _d(k)
                # Look for e.g. /acquisition/Sweep_19 or /stimulus/presented/Sweep_19_stim.
                if (kstr.lower().startswith('sweep_') and kstr[6:].split()[0].startswith(str(sweep_num))):
                    result.append(obj.name)
                # e.g. Sweep_{N}_stim
                if kstr.lower().startswith(f'sweep_{sweep_num}_'):
                    result.append(obj.name)
            return result
        # NWB1 style: /acquisition/timeseries/Sweep_XX
        # Try various plausible groupings
        if '/acquisition/timeseries' in f:
            for k in f['/acquisition/timeseries']:
                kstr = _d(k)
                if f'{sweep_num}' in kstr:
                    resp_candidates.append(f['/acquisition/timeseries'][k].name)
        elif '/acquisition' in f:
            resp_candidates += scan_for_candidates(f['/acquisition'], True)
        if '/stimulus/presented' in f:
            for k in f['/stimulus/presented']:
                kstr = _d(k)
                if f'{sweep_num}' in kstr:
                    stim_candidates.append(f['/stimulus/presented'][k].name)
        elif '/stimulus' in f:
            stim_candidates += scan_for_candidates(f['/stimulus'], False)
        # Remove possible duplicates
        resp_candidates = list(dict.fromkeys(resp_candidates))
        stim_candidates = list(dict.fromkeys(stim_candidates))
        # Try to disambiguate
        def series_type_from_group(obj):
            t = obj.attrs.get('neurodata_type') or obj.attrs.get(b'neurodata_type')
            if t: return _d(t).lower()
            nm = _d(obj.name)
            if 'stim' in nm.lower():
                return 'stimulus'
            if 'resp' in nm.lower() or 'voltage' in nm.lower():
                return 'response'
            return ''
        pick = lambda lst, prefer=None: lst[0] if lst else None
        resp_path = pick(resp_candidates)
        stim_path = pick(stim_candidates)
        return resp_path, stim_path

    def get_data_and_meta(ts_obj):
        # Get data as float64 array
        if 'data' in ts_obj:
            d = ts_obj['data']
        else:
            d = ts_obj
        # Squeeze in case shape (-1,) or (1,N)
        raw = np.asarray(d[()]).squeeze()
        # Get conversion
        conv = ts_obj.attrs.get('conversion', 1.0)
        if isinstance(conv, bytes): conv = float(_d(conv))
        offset = ts_obj.attrs.get('offset', 0.0)
        if isinstance(offset, bytes): offset = float(_d(offset))
        # Get unit
        unit = ts_obj.attrs.get('unit') or ts_obj.attrs.get('units') or ''
        unit = _d(unit)
        # Get starting_time and rate
        sampling_rate = ts_obj.attrs.get('starting_time', None)
        if 'starting_time' in ts_obj.attrs:
            starting_time = ts_obj.attrs['starting_time']
            if isinstance(starting_time, np.ndarray):
                starting_time = float(starting_time[()])
            else:
                starting_time = float(starting_time)
        else:
            starting_time = 0.0
        rate = ts_obj.attrs.get('rate', None)
        if rate is None:
            # Try 'sampling_rate' or shape of timestamps
            if 'sampling_rate' in ts_obj.attrs:
                rate = ts_obj.attrs['sampling_rate']
            elif 'timestamps' in ts_obj:
                ts = ts_obj['timestamps'][()]
                if len(ts) > 1:
                    rate = 1. / np.median(np.diff(ts))
                else:
                    rate = 1.0
            else:
                rate = 1.0
        if isinstance(rate, bytes):
            rate = float(_d(rate))
        else:
            rate = float(rate)
        return {
            'data': raw,
            'conversion': float(conv),
            'offset': float(offset),
            'unit': unit,
            'rate': float(rate),
            'starting_time': float(starting_time)
        }

    def ensure_physical(trace, conversion, offset=0.0):
        return conversion * trace + offset

    output = {}
    with h5py.File(nwb_path, 'r') as f:
        nwb_version = get_nwb_version(f)
        sweeps = {}
        for sweep_num in [19,20,21,22,23,24]:
            sweep_key = str(sweep_num)
            resp_path, stim_path = get_time_series_for_sweep(f, sweep_num)
            # Defensive default structure
            entry = {k: None for k in [
                'sampling_rate_hz', 'n_samples', 'dt_seconds',
                'response_stored_unit', 'stimulus_stored_unit',
                'main_pulse_onset_s', 'main_pulse_duration_s',
                'main_pulse_amplitude_pa', 'pre_stimulus_voltage_mv',
                'mean_pulse_voltage_deflection_mv'
            ]}
            if resp_path is None or stim_path is None:
                sweeps[sweep_key] = entry
                continue
            resp_ts = f[resp_path]
            stim_ts = f[stim_path]
            # Load data
            resp = get_data_and_meta(resp_ts)
            stim = get_data_and_meta(stim_ts)
            # Check sample count
            n_samples = int(min(len(resp['data']), len(stim['data'])))
            sampling_rate_hz = float(resp['rate'])
            dt_seconds = 1.0 / sampling_rate_hz if sampling_rate_hz else 0.0
            # Unit strings as stored
            entry['sampling_rate_hz'] = sampling_rate_hz
            entry['n_samples'] = n_samples
            entry['dt_seconds'] = dt_seconds
            entry['response_stored_unit'] = resp['unit']
            entry['stimulus_stored_unit'] = stim['unit']
            # Physical units for calculations
            stim_phys = ensure_physical(stim['data'][:n_samples], stim['conversion'], stim['offset'])
            resp_phys = ensure_physical(resp['data'][:n_samples], resp['conversion'], resp['offset'])
            # Convert stimulus to pA if needed (allow 'pA', 'pa', or 'amp', etc.)
            stim_unit_lc = stim['unit'].lower()
            stim_scaling = 1.0
            if stim_unit_lc in ['a','amp','amps','ampere','amperes']:
                stim_scaling = 1e12
            elif stim_unit_lc == 'na':
                stim_scaling = 1e3
            elif stim_unit_lc == 'pa' or stim_unit_lc == 'p.a.':
                stim_scaling = 1.0
            # If 'pA', no change
            stim_in_pa = stim_phys * stim_scaling
            # Convert response to mV if needed
            resp_unit_lc = resp['unit'].lower()
            resp_scaling = 1.0
            if resp_unit_lc in ['v','volt','volts','voltages']:
                resp_scaling = 1e3
            elif resp_unit_lc == 'uv' or resp_unit_lc == 'μv':
                resp_scaling = 1e-3
            elif resp_unit_lc == 'mv':
                resp_scaling = 1.0
            resp_in_mv = resp_phys * resp_scaling
            # Detect main pulse
            # Define baseline (median holding current in pA)
            med_stim = float(np.median(stim_in_pa))
            below = (stim_in_pa <= med_stim - 1e-6)
            # Find the longest continuous run
            def find_longest_true_run(arr):
                maxlen = 0
                maxstart = 0
                i=0
                N = len(arr)
                while i<N:
                    if arr[i]:
                        j=i
                        while j+1<N and arr[j+1]:
                            j+=1
                        thislen = j-i+1
                        if thislen>maxlen:
                            maxlen = thislen
                            maxstart = i
                        i=j+1
                    else:
                        i+=1
                return maxstart, maxlen
            onset_idx, main_pulse_len = find_longest_true_run(below)
            main_pulse_onset_s = onset_idx * dt_seconds
            main_pulse_duration_s = main_pulse_len * dt_seconds
            entry['main_pulse_onset_s'] = main_pulse_onset_s
            entry['main_pulse_duration_s'] = main_pulse_duration_s
            # Compute mean physical current during main pulse
            pulse_end = onset_idx + main_pulse_len
            mp = stim_in_pa[onset_idx:pulse_end]
            # Mean current in 50ms before main pulse
            preN = int(round(0.05/dt_seconds))
            pre_start = max(0, onset_idx - preN)
            pre_stim = stim_in_pa[pre_start:onset_idx] if onset_idx > 0 else stim_in_pa[:1]
            main_amp = float(np.mean(mp) - np.mean(pre_stim))
            entry['main_pulse_amplitude_pa'] = main_amp
            # Pre-stimulus voltage: mean in 50ms before main pulse (match sample count logic above)
            pre_resp = resp_in_mv[pre_start:onset_idx] if onset_idx > 0 else resp_in_mv[:1]
            pre_stim_voltage = float(np.mean(pre_resp))
            entry['pre_stimulus_voltage_mv'] = pre_stim_voltage
            # Mean voltage deflection during main pulse: mean(resp main pulse) - mean(pre pulse 50ms)
            mp_resp = resp_in_mv[onset_idx:pulse_end]
            mean_mp_resp = float(np.mean(mp_resp))
            entry['mean_pulse_voltage_deflection_mv'] = mean_mp_resp - pre_stim_voltage
            sweeps[sweep_key] = entry
    return {'nwb_version': nwb_version, 'sweeps': sweeps}
