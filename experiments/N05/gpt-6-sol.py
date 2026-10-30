def extract(nwb_path):
    import h5py
    import numpy as np
    import math
    import re

    def scalar(value):
        a = np.asarray(value)
        return a.reshape(-1)[0] if a.ndim else a.item()

    def string(value):
        value = scalar(value)
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return str(value)

    def attr_or_dataset(group, dataset, key, default=None):
        if key in dataset.attrs:
            return scalar(dataset.attrs[key])
        if key in group.attrs:
            return scalar(group.attrs[key])
        if key in group and isinstance(group[key], h5py.Dataset):
            return scalar(group[key][()])
        return default

    def unit_factor(unit, kind):
        u = unit.strip().replace('µ', 'u').replace('μ', 'u')
        units = {
            'current': {'A': 1e12, 'mA': 1e9, 'uA': 1e6,
                        'nA': 1e3, 'pA': 1.0, 'fA': 1e-3},
            'voltage': {'V': 1e3, 'mV': 1.0, 'uV': 1e-3,
                        'nV': 1e-6}
        }[kind]
        if u in units:
            return units[u]
        words = {
            'current': {'amp': 1e12, 'amps': 1e12,
                        'ampere': 1e12, 'amperes': 1e12},
            'voltage': {'volt': 1e3, 'volts': 1e3}
        }[kind]
        if u.lower() in words:
            return words[u.lower()]
        raise ValueError('Unsupported ' + kind + ' unit: ' + unit)

    def sample_rate(group):
        if 'starting_time' in group:
            start = group['starting_time']
            if 'rate' in start.attrs:
                return float(scalar(start.attrs['rate']))
        if 'rate' in group.attrs:
            return float(scalar(group.attrs['rate']))
        if 'rate' in group and isinstance(group['rate'], h5py.Dataset):
            return float(scalar(group['rate'][()]))
        if 'timestamps' in group:
            t = np.asarray(group['timestamps'][:min(1024, len(group['timestamps']))], dtype=float)
            if len(t) >= 2:
                return float(1.0 / np.median(np.diff(t)))
        raise ValueError('Sampling rate missing from ' + group.name)

    with h5py.File(nwb_path, 'r') as f:
        version = None
        for key in ('nwb_version', 'NWB_version'):
            if key in f.attrs:
                version = string(f.attrs[key])
                break
            if key in f and isinstance(f[key], h5py.Dataset):
                version = string(f[key][()])
                break
        if version is None:
            raise ValueError('NWB version metadata not found')

        candidates = None
        def series(number, role):
            nonlocal candidates
            root = 'acquisition/timeseries' if role == 'response' else 'stimulus/presentation'
            for label in ('Sweep_' + str(number), 'sweep_' + str(number)):
                path = root + '/' + label
                if path in f and isinstance(f[path], h5py.Group) and 'data' in f[path]:
                    return f[path]
            if candidates is None:
                candidates = []
                def collect(name, obj):
                    if isinstance(obj, h5py.Group) and 'data' in obj and isinstance(obj['data'], h5py.Dataset):
                        candidates.append((name, obj))
                f.visititems(collect)
            for name, obj in candidates:
                label = name.rsplit('/', 1)[-1]
                match = re.fullmatch(r'(?i)sweep[_ -]?0*(\d+)', label)
                if match and int(match.group(1)) == number:
                    lower = name.lower()
                    if role == 'response' and '/acquisition/' in '/' + lower + '/':
                        return obj
                    if role == 'stimulus' and '/stimulus/' in '/' + lower + '/':
                        return obj
            raise ValueError('Missing ' + role + ' for sweep ' + str(number))

        output = {}
        for number in range(19, 25):
            response_group = series(number, 'response')
            stimulus_group = series(number, 'stimulus')
            response_data = response_group['data']
            stimulus_data = stimulus_group['data']
            response_rate = sample_rate(response_group)
            stimulus_rate = sample_rate(stimulus_group)
            if not math.isclose(response_rate, stimulus_rate, rel_tol=1e-8, abs_tol=1e-5):
                raise ValueError('Response and stimulus rates differ in sweep ' + str(number))
            response_unit = string(attr_or_dataset(response_group, response_data, 'unit'))
            stimulus_unit = string(attr_or_dataset(stimulus_group, stimulus_data, 'unit'))
            response_conversion = float(attr_or_dataset(response_group, response_data, 'conversion', 1.0))
            stimulus_conversion = float(attr_or_dataset(stimulus_group, stimulus_data, 'conversion', 1.0))
            voltage_mv = np.asarray(response_data[()], dtype=np.float64).reshape(-1)
            current_pa = np.asarray(stimulus_data[()], dtype=np.float64).reshape(-1)
            voltage_mv *= response_conversion * unit_factor(response_unit, 'voltage')
            current_pa *= stimulus_conversion * unit_factor(stimulus_unit, 'current')
            if len(voltage_mv) != len(current_pa):
                raise ValueError('Response and stimulus lengths differ in sweep ' + str(number))
            holding = float(np.median(current_pa))
            active = current_pa <= holding - 1e-6
            edges = np.diff(np.concatenate(([False], active, [False])).astype(np.int8))
            starts = np.flatnonzero(edges == 1)
            ends = np.flatnonzero(edges == -1)
            if len(starts) == 0:
                raise ValueError('Main negative pulse not found in sweep ' + str(number))
            longest = int(np.argmax(ends - starts))
            onset = int(starts[longest])
            end = int(ends[longest])
            pre_count = int(round(0.050 * response_rate))
            pre_start = onset - pre_count
            if pre_count < 1 or pre_start < 0:
                raise ValueError('Insufficient pre-pulse samples in sweep ' + str(number))
            pre_voltage = float(np.mean(voltage_mv[pre_start:onset]))
            output[str(number)] = {
                'sampling_rate_hz': float(response_rate),
                'n_samples': int(len(voltage_mv)),
                'dt_seconds': float(1.0 / response_rate),
                'response_stored_unit': response_unit,
                'stimulus_stored_unit': stimulus_unit,
                'main_pulse_onset_s': float(onset / response_rate),
                'main_pulse_duration_s': float((end - onset) / response_rate),
                'main_pulse_amplitude_pa': float(np.mean(current_pa[onset:end]) - np.mean(current_pa[pre_start:onset])),
                'pre_stimulus_voltage_mv': pre_voltage,
                'mean_pulse_voltage_deflection_mv': float(np.mean(voltage_mv[onset:end]) - pre_voltage)
            }
        return {'nwb_version': version, 'sweeps': output}