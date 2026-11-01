def extract(nwb_path):
    import h5py
    import numpy as np
    import re
    sweep_ids = (19, 20, 21, 22, 23, 24)

    def text_value(value):
        if isinstance(value, np.ndarray):
            if value.size != 1:
                return str(value.tolist())
            return text_value(value.reshape(-1)[0])
        if isinstance(value, np.generic):
            value = value.item()
        if isinstance(value, (bytes, np.bytes_)):
            return bytes(value).decode('utf-8')
        return str(value)

    def number(value, default=None):
        if value is None:
            return default
        array = np.asarray(value)
        if array.size != 1:
            return default
        try:
            return float(array.reshape(-1)[0])
        except (TypeError, ValueError):
            return default

    def attr_ci(obj, name):
        wanted = name.lower()
        for key in obj.attrs.keys():
            if str(key).lower() == wanted:
                return obj.attrs[key]
        return None

    def file_version(handle):
        for name in ('nwb_version', 'NWB_version'):
            if name in handle and isinstance(handle[name], h5py.Dataset):
                return text_value(handle[name][()])
        for name in ('nwb_version', 'NWB_version'):
            if name in handle.attrs:
                return text_value(handle.attrs[name])
        found = []

        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset) and name.rsplit('/', 1)[-1].lower() == 'nwb_version':
                found.append(obj)
        handle.visititems(visitor)
        if found:
            found.sort(key=lambda obj: (obj.name.count('/'), len(obj.name)))
            return text_value(found[0][()])
        raise ValueError('NWB version metadata was not found')

    def scalar_child(group, child_name):
        for key in group.keys():
            if key.lower() == child_name.lower():
                obj = group.get(key, getlink=False)
                if isinstance(obj, h5py.Dataset) and obj.size == 1:
                    return obj[()]
        return None

    def sweep_number(group):
        current = group
        while isinstance(current, h5py.Group):
            match = re.search('(?:^|[/ _-])sweep[ _-]*0*([0-9]+)(?=$|[/ _-])', current.name, re.I)
            if match:
                return int(match.group(1))
            value = attr_ci(current, 'sweep_number')
            if value is None:
                value = scalar_child(current, 'sweep_number')
            parsed = number(value)
            if parsed is not None and parsed.is_integer():
                return int(parsed)
            if current.name == '/':
                break
            current = current.parent
        return None

    def candidate_score(dataset, role):
        path = dataset.name.lower()
        score = 0
        if role == 'response':
            score += 120 if '/acquisition/' in path else 0
            score += 25 if '/timeseries/' in path else 0
            score -= 180 if '/stimulus/' in path else 0
            score -= 50 if '/analysis/' in path else 0
        else:
            score += 140 if '/stimulus/' in path else 0
            score += 30 if '/presentation/' in path else 0
            score -= 180 if '/acquisition/' in path else 0
        score += 10 if dataset.name.rsplit('/', 1)[-1].lower() == 'data' else 0
        score += 3 if attr_ci(dataset, 'unit') is not None else 0
        return score

    def find_series(handle):
        candidates = {s: [] for s in sweep_ids}

        def visitor(name, obj):
            if not isinstance(obj, h5py.Dataset) or not obj.shape:
                return
            if name.rsplit('/', 1)[-1].lower() != 'data':
                return
            sn = sweep_number(obj.parent)
            if sn in candidates:
                candidates[sn].append(obj)

        def visit_paths(group, ancestors):
            address = h5py.h5o.get_info(group.id).addr
            if address in ancestors:
                return
            active = ancestors | {address}
            for name in group:
                link = group.get(name, getlink=True)
                if isinstance(link, h5py.ExternalLink):
                    continue
                try:
                    obj = group[name]
                except (KeyError, OSError):
                    continue
                visitor(obj.name.lstrip('/'), obj)
                if isinstance(obj, h5py.Group):
                    visit_paths(obj, active)
        visit_paths(handle, set())
        result = {}
        for sn in sweep_ids:
            items = candidates[sn]
            if not items:
                raise ValueError('No data series found for sweep %d' % sn)
            responses = sorted(items, key=lambda x: candidate_score(x, 'response'), reverse=True)
            stimuli = sorted(items, key=lambda x: candidate_score(x, 'stimulus'), reverse=True)
            response = responses[0]
            stimulus = stimuli[0]
            if response.name == stimulus.name:
                stimulus = next((x for x in stimuli if x.name != response.name), None)
            if stimulus is None:
                raise ValueError('Could not distinguish sweep %d stimulus' % sn)
            result[sn] = (response, stimulus)
        return result

    def series_rate(dataset):
        group = dataset.parent
        for obj in (dataset, group):
            for key in ('rate', 'sampling_rate', 'sampling_rate_hz'):
                value = number(attr_ci(obj, key))
                if value is not None and value > 0:
                    return value
        for key in group.keys():
            obj = group.get(key, getlink=False)
            if not isinstance(obj, h5py.Dataset):
                continue
            if key.lower() == 'starting_time':
                value = number(attr_ci(obj, 'rate'))
                if value is not None and value > 0:
                    return value
            if key.lower() == 'timestamps' and obj.size >= 2:
                count = min(int(obj.shape[0]), 10001)
                times = np.asarray(obj[:count], dtype=np.float64).reshape(-1)
                differences = np.diff(times)
                differences = differences[np.isfinite(differences) & (differences > 0)]
                if differences.size:
                    return float(1.0 / np.median(differences))
        raise ValueError('Sampling rate missing for ' + dataset.name)

    def stored_unit(dataset):
        value = attr_ci(dataset, 'unit')
        if value is None:
            value = attr_ci(dataset.parent, 'unit')
        if value is None:
            raise ValueError('Unit missing for ' + dataset.name)
        return text_value(value)

    def unit_multiplier(unit, quantity):
        normalized = unit.replace('µ', 'u').replace('μ', 'u')
        normalized = re.sub('[\\s_.-]+', '', normalized).lower()
        if quantity == 'current':
            scales = {'a': 1000000000000.0, 'amp': 1000000000000.0, 'amps': 1000000000000.0, 'ampere': 1000000000000.0, 'amperes': 1000000000000.0, 'ma': 1000000000.0, 'milliamp': 1000000000.0, 'milliamps': 1000000000.0, 'milliampere': 1000000000.0, 'milliamperes': 1000000000.0, 'ua': 1000000.0, 'microamp': 1000000.0, 'microamps': 1000000.0, 'microampere': 1000000.0, 'microamperes': 1000000.0, 'na': 1000.0, 'nanoamp': 1000.0, 'nanoamps': 1000.0, 'nanoampere': 1000.0, 'nanoamperes': 1000.0, 'pa': 1.0, 'picoamp': 1.0, 'picoamps': 1.0, 'picoampere': 1.0, 'picoamperes': 1.0, 'fa': 0.001, 'femtoamp': 0.001, 'femtoampere': 0.001}
        else:
            scales = {'v': 1000.0, 'volt': 1000.0, 'volts': 1000.0, 'mv': 1.0, 'millivolt': 1.0, 'millivolts': 1.0, 'uv': 0.001, 'microvolt': 0.001, 'microvolts': 0.001, 'nv': 1e-06, 'nanovolt': 1e-06, 'nanovolts': 1e-06}
        if normalized not in scales:
            raise ValueError('Unsupported physical unit: ' + unit)
        return scales[normalized]

    def physical_vector(dataset, unit, quantity):
        raw = np.asarray(dataset[...], dtype=np.float64).reshape(-1)
        conversion = number(attr_ci(dataset, 'conversion'), 1.0)
        offset = number(attr_ci(dataset, 'offset'), 0.0)
        return (raw * conversion + offset) * unit_multiplier(unit, quantity)

    def longest_true_run(mask):
        padded = np.concatenate((np.array([False]), mask, np.array([False])))
        changes = np.diff(padded.astype(np.int8))
        starts = np.flatnonzero(changes == 1)
        ends = np.flatnonzero(changes == -1)
        if starts.size == 0:
            raise ValueError('No negative stimulus pulse found')
        lengths = ends - starts
        index = int(np.argmax(lengths))
        return (int(starts[index]), int(ends[index]))
    with h5py.File(nwb_path, 'r') as handle:
        version = file_version(handle)
        series = find_series(handle)
        output = {}
        for sn in sweep_ids:
            response_ds, stimulus_ds = series[sn]
            response_rate = float(series_rate(response_ds))
            stimulus_rate = float(series_rate(stimulus_ds))
            tolerance = max(1e-09, abs(response_rate) * 1e-09)
            if abs(response_rate - stimulus_rate) > tolerance:
                raise ValueError('Response/stimulus rate mismatch in sweep %d' % sn)
            response_unit = stored_unit(response_ds)
            stimulus_unit = stored_unit(stimulus_ds)
            voltage_mv = physical_vector(response_ds, response_unit, 'voltage')
            current_pa = physical_vector(stimulus_ds, stimulus_unit, 'current')
            n_samples = int(response_ds.shape[0])
            if voltage_mv.size != n_samples or current_pa.size < 1:
                raise ValueError('Unsupported multidimensional sweep data')
            holding = float(np.median(current_pa))
            onset, pulse_end = longest_true_run(current_pa <= holding - 1e-06)
            if pulse_end > voltage_mv.size:
                raise ValueError('Stimulus pulse extends beyond response')
            baseline_count = int(round(0.05 * response_rate))
            baseline_start = onset - baseline_count
            if baseline_count < 1 or baseline_start < 0:
                raise ValueError('Insufficient 50 ms pre-pulse baseline')
            current_baseline = float(np.mean(current_pa[baseline_start:onset]))
            current_pulse = float(np.mean(current_pa[onset:pulse_end]))
            voltage_baseline = float(np.mean(voltage_mv[baseline_start:onset]))
            voltage_pulse = float(np.mean(voltage_mv[onset:pulse_end]))
            pulse_length = pulse_end - onset
            output[str(sn)] = {'sampling_rate_hz': response_rate, 'n_samples': n_samples, 'dt_seconds': float(1.0 / response_rate), 'response_stored_unit': response_unit, 'stimulus_stored_unit': stimulus_unit, 'main_pulse_onset_s': float(onset / response_rate), 'main_pulse_duration_s': float(pulse_length / response_rate), 'main_pulse_amplitude_pa': float(current_pulse - current_baseline), 'pre_stimulus_voltage_mv': voltage_baseline, 'mean_pulse_voltage_deflection_mv': float(voltage_pulse - voltage_baseline)}
        return {'nwb_version': version, 'sweeps': output}
