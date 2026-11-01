import numpy as np
import scipy.signal

def fit_predict(train_x, train_y, test_x, train_groups):
    # train_x, test_x: (nrec, 90, 132)  count rasters  (nrec=4), time (90), depth bins (132)
    # train_y: (nrec, 90), true per-bin displacement, micrometers
    # test_x: predict (nrec, 90), micrometers, unknown constant offset per row allowed
    # train_groups is always None (unused)
    nrec, nbin, ndepth = test_x.shape
    rel_pred = np.zeros((nrec, nbin), dtype=float)

    # Peak depth grid (in um, for reference; not used for training)
    # depth_grid = np.linspace(-20, 640, ndepth) # spacing is 5um

    rng = np.random.RandomState(1337)  # for any subsampling, deterministic
    max_shift_bins = 12  # allows up to ±60um=12*5um
    shifts = np.arange(-max_shift_bins, max_shift_bins+1)  # in bins

    # For each heldout simulation (row)
    for r in range(nrec):
        # data: (90, 132)
        x = test_x[r].astype(float)
        # Robust per-depth normalization: each depth subtract median and scale
        x -= np.median(x, axis=0, keepdims=True)
        x /= (np.std(x, axis=0, ddof=1, keepdims=True) + 1e-8)
        # For per-time profiles, recenter over depths
        y_bin = np.zeros(nbin, dtype=float)
        # Use mean activity profile as a registration template
        template = np.median(x, axis=0)  # Shape: (132,)
        template -= np.mean(template)    # Center
        template /= (np.std(template, ddof=1) + 1e-8)
        # For each second
        for t in range(nbin):
            prof = x[t].copy()
            prof -= np.mean(prof)
            prof /= (np.std(prof, ddof=1) + 1e-8)
            # Cross-correlate this profile to mean template over allowed shifts
            ccs = []
            for sh in shifts:
                if sh < 0:
                    a, b = prof[-sh:], template[:sh] if sh != 0 else template
                elif sh > 0:
                    a, b = prof[:-sh], template[sh:]
                else:
                    a, b = prof, template
                if len(a)==0 or len(b)==0:
                    ccs.append(-np.inf)
                else:
                    n1 = np.linalg.norm(a)
                    n2 = np.linalg.norm(b)
                    cc = np.dot(a,b)/(n1*n2+1e-8)
                    ccs.append(cc)
            ccs = np.array(ccs)
            # Parabolic sub-bin refinement near the peak
            sh0 = np.argmax(ccs)
            if 0 < sh0 < len(shifts)-1:
                y0, y1, y2 = ccs[sh0-1], ccs[sh0], ccs[sh0+1]
                denom = 2*(y0 - 2*y1 + y2)
                if denom != 0:
                    delta = (y0 - y2)/denom
                else:
                    delta = 0.0
            else:
                delta = 0.0
            sh_est = shifts[sh0] + delta
            # Shift in bins, map to micrometers (5um per bin)
            y_bin[t] = sh_est * 5.0
        # Remove temporal mean: relative displacement only
        y_bin -= np.mean(y_bin)
        rel_pred[r] = y_bin
    return rel_pred
