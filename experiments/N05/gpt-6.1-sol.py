import numpy as np
import h5py
import re


def extract(nwb_path):
    def scalar(value):
        a = np.asarray(value)
        if a.size != 1:
            raise ValueError('Expected scalar metadata')
        return a.reshape(-1)[0].item()

    def decode(value):
        value = scalar(value)
        return value.decode('utf-8') if isinstance(value, bytes) else str(value)

    def unit_scale(unit, kind):
        u = unit.strip().replace('μ', 'u').replace('µ', 'u').lower()
        u = u.replace(' ', '')
        bases = ('a', 'amp', 'amps', 'ampere', 'amperes') if kind == 'stimulus' else ('v', 'volt', 'volts')
        target = 1e12 if kind == 'stimulus' else 1e3
        prefixes = {'': 1.0, 'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12}
        for prefix, multiplier in prefixes.items():
            if any(u == prefix + base for base in bases):
                return target * multiplier
        raise ValueError('Unsupported physical unit: ' + unit)

    def metadata(g, key, default=None):
        d = g['data']
        if key in d.attrs:
            return scalar(d.attrs[key])
        if key in g.attrs:
            return scalar(g.attrs[key])
        if key in g and isinstance(g[key], h5py.Dataset):
            return scalar(g[key][()])
        return default

    def stored_unit(g):
        return decode(g['data'].attrs['unit'])

    def physical(g, kind):
        values = np.asarray(g['data'][()], dtype=np.float64).squeeze()
        if values.ndim != 1:
            raise ValueError('Expected a single-channel time series')
        conversion = float(metadata(g, 'conversion', 1.0))
        offset = float(metadata(g, 'offset', 0.0))
        return (values * conversion + offset) * unit_scale(stored_unit(g), kind)

    def clock(g):
        start = 0.0
        rate = None
        if 'starting_time' in g:
            d = g['starting_time']
            start = float(scalar(d[()]))
            if 'rate' in d.attrs:
                rate = float(scalar(d.attrs['rate']))
        if rate is None:
            for owner in (g, g['data']):
                for key in ('rate', 'sampling_rate', 'sampling_rate_hz'):
                    if key in owner.attrs:
                        rate = float(scalar(owner.attrs[key]))
                        break
                if rate is not None:
                    break
        if 'timestamps' in g:
            t = g['timestamps']
            if t.size:
                start = float(scalar(t[0]))
            if rate is None and t.size > 1:
                rate = (t.shape[0] - 1) / (float(scalar(t[-1])) - start)
        if rate is None:
            for key in ('rate', 'sampling_rate'):
                if key in g and isinstance(g[key], h5py.Dataset):
                    rate = float(scalar(g[key][()]))
                    break
        if rate is None or not np.isfinite(rate) or rate <= 0:
            raise ValueError('Missing or invalid sampling rate')
        return rate, start

    def sweep_number(g):
        for key in ('sweep_number', 'sweep_num'):
            if key in g.attrs:
                return int(scalar(g.attrs[key]))
            if key in g and isinstance(g[key], h5py.Dataset):
                return int(scalar(g[key][()]))
        matches = re.findall(r'sweep[_\s-]*(\d+)', g.name, flags=re.I)
        return int(matches[-1]) if matches else None

    targets = set(range(19, 25))
    with h5py.File(nwb_path, 'r') as f:
        if 'nwb_version' in f and isinstance(f['nwb_version'], h5py.Dataset):
            version = decode(f['nwb_version'][()])
        elif 'nwb_version' in f.attrs:
            version = decode(f.attrs['nwb_version'])
        else:
            versions = []
            def find_version(name, obj):
                if name.rsplit('/', 1)[-1] == 'nwb_version' and isinstance(obj, h5py.Dataset):
                    versions.append(obj)
            f.visititems(find_version)
            if not versions:
                raise ValueError('Missing NWB version')
            version = decode(versions[0][()])

        candidates = []
        def add(g, number=None, role=None):
            if isinstance(g, h5py.Group) and 'data' in g and isinstance(g['data'], h5py.Dataset):
                number = sweep_number(g) if number is None else number
                if number in targets:
                    candidates.append((g, number, role))

        def resolve(obj):
            if isinstance(obj, h5py.Group):
                return obj
            if isinstance(obj, h5py.Dataset) and obj.size == 1:
                value = scalar(obj[()])
                if isinstance(value, h5py.Reference):
                    return f[value] if value else None
                if isinstance(value, (str, bytes)):
                    path = value.decode('utf-8') if isinstance(value, bytes) else value
                    return f[path] if path in f else None
            return None

        def inspect(name, obj):
            if not isinstance(obj, h5py.Group):
                return
            add(obj)
            number = sweep_number(obj)
            if number not in targets:
                return
            for role in ('response', 'stimulus'):
                for relative in (role + '/timeseries', role):
                    if relative in obj:
                        linked = resolve(obj[relative])
                        if linked is not None:
                            add(linked, number, role)
        f.visititems(inspect)

        def choose(number, role):
            ranked = []
            for g, n, hint in candidates:
                if n != number:
                    continue
                try:
                    unit_scale(stored_unit(g), role)
                except (KeyError, ValueError, TypeError):
                    continue
                path = g.name.lower()
                score = 100 if hint == role else 0
                if role == 'response':
                    score += 30 if '/acquisition/' in path else 0
                    score += 10 if '/response/' in path else 0
                    score -= 40 if '/stimulus/' in path else 0
                else:
                    score += 30 if '/stimulus/' in path else 0
                    score += 10 if '/presentation/' in path else 0
                    score -= 40 if '/acquisition/' in path else 0
                ranked.append((score, g.name, g))
            if not ranked:
                raise ValueError('Cannot locate %s for sweep %s' % (role, number))
            ranked.sort(key=lambda item: (-item[0], item[1]))
            return ranked[0][2]

        sweeps = {}
        for number in sorted(targets):
            response = choose(number, 'response')
            stimulus = choose(number, 'stimulus')
            rate, response_start = clock(response)
            stimulus_rate, stimulus_start = clock(stimulus)
            if not np.isclose(rate, stimulus_rate, rtol=1e-10, atol=1e-8):
                raise ValueError('Stimulus and response rates differ')
            voltage = physical(response, 'response')
            current = physical(stimulus, 'stimulus')
            holding = float(np.median(current))
            negative = current <= holding - 1e-6
            edges = np.diff(np.concatenate(([False], negative, [False])).astype(np.int8))
            starts = np.flatnonzero(edges == 1)
            stops = np.flatnonzero(edges == -1)
            if not starts.size:
                raise ValueError('No negative stimulus pulse')
            longest = int(np.argmax(stops - starts))
            begin, end = int(starts[longest]), int(stops[longest])
            baseline_count = int(round(0.05 * rate))
            time_offset = stimulus_start - response_start
            response_begin = begin + int(round(time_offset * rate))
            response_end = response_begin + end - begin
            if baseline_count < 1 or begin < baseline_count or response_begin < baseline_count or response_end > voltage.size:
                raise ValueError('Incomplete pulse or baseline window')
            pre_voltage = float(np.mean(voltage[response_begin-baseline_count:response_begin]))
            amplitude = float(np.mean(current[begin:end]) - np.mean(current[begin-baseline_count:begin]))
            deflection = float(np.mean(voltage[response_begin:response_end]) - pre_voltage)
            sweeps[str(number)] = {
                'sampling_rate_hz': float(rate),
                'n_samples': int(voltage.size),
                'dt_seconds': float(1.0 / rate),
                'response_stored_unit': stored_unit(response),
                'stimulus_stored_unit': stored_unit(stimulus),
                'main_pulse_onset_s': float(time_offset + begin / rate),
                'main_pulse_duration_s': float((end - begin) / rate),
                'main_pulse_amplitude_pa': amplitude,
                'pre_stimulus_voltage_mv': pre_voltage,
                'mean_pulse_voltage_deflection_mv': deflection
            }
        return {'nwb_version': version, 'sweeps': sweeps}
