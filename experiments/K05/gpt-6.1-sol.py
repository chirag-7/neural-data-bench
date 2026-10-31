import numpy as np


def _balanced_weights(donors, blocks):
    w = np.zeros(len(donors), dtype=float)
    unique_donors = np.unique(donors)
    for donor in unique_donors:
        donor_mask = donors == donor
        donor_blocks = np.unique(blocks[donor_mask])
        for block in donor_blocks:
            mask = donor_mask & (blocks == block)
            w[mask] = 1.0 / (len(unique_donors) * len(donor_blocks) * mask.sum())
    return w / w.sum()


def _ridge_path(z, q, centered_y, w, alphas):
    sw = np.sqrt(w)
    a = z * sw[:, None]
    energy = np.einsum('ij,ij->', a, a, optimize=False)
    shape = (len(q), len(alphas), centered_y.shape[1])
    if energy <= 1e-20:
        return np.zeros(shape)
    kernel = np.einsum('ik,jk->ij', a, a, optimize=False) / energy
    eigenvalues, vectors = np.linalg.eigh(kernel)
    eigenvalues = np.maximum(eigenvalues, 0.0)
    cross = np.einsum('ik,jk->ij', q, a, optimize=False) / energy
    cross_vectors = np.einsum('ij,jk->ik', cross, vectors, optimize=False)
    projected_y = np.einsum(
        'ij,it->jt', vectors, centered_y * sw[:, None], optimize=False
    )
    predictions = np.empty(shape)
    for j, alpha in enumerate(alphas):
        coefficients = projected_y / (eigenvalues[:, None] + alpha)
        predictions[:, j, :] = np.einsum(
            'ij,jt->it', cross_vectors, coefficients, optimize=False
        )
    return predictions


def _prediction_bank(x, y, query, donors, blocks, specifications, alphas):
    w = _balanced_weights(donors, blocks)
    finite = np.isfinite(x)
    clean = np.where(finite, x, 0.0)
    denominator = np.einsum('i,ij->j', w, finite, optimize=False)
    numerator = np.einsum('i,ij->j', w, clean, optimize=False)
    imputation = np.divide(
        numerator, denominator, out=np.zeros(x.shape[1]), where=denominator > 0
    )
    clean = np.where(finite, x, imputation[None, :])
    clean_query = np.where(np.isfinite(query), query, imputation[None, :])
    mean_x = np.einsum('i,ij->j', w, clean, optimize=False)
    centered_x = clean - mean_x
    centered_query = clean_query - mean_x
    variance = np.einsum(
        'i,ij,ij->j', w, centered_x, centered_x, optimize=False
    )
    sd = np.sqrt(np.maximum(variance, 0.0))
    positive = sd[sd > 1e-10]
    scale_floor = max(1e-6, 0.05 * np.median(positive)) if positive.size else 1.0
    safe_sd = np.maximum(sd, scale_floor)
    mean_y = np.einsum('i,it->t', w, y, optimize=False)
    centered_y = y - mean_y
    covariance = np.einsum(
        'i,ij,it->jt', w, centered_x, centered_y, optimize=False
    )
    association = np.abs(covariance) / safe_sd[:, None]
    variance_order = np.argsort(-variance, kind='mergesort')
    count = 1 + len(specifications) * len(alphas)
    bank = np.empty((len(query), count, y.shape[1]))
    bank[:, 0, :] = mean_y
    offset = 1
    for method, number, power, prior in specifications:
        number = min(number, x.shape[1])
        if method == 'variance':
            chosen = variance_order[:number]
            scale = safe_sd[chosen] ** power
            z = centered_x[:, chosen] / scale
            q = centered_query[:, chosen] / scale
            path = _ridge_path(z, q, centered_y, w, alphas)
            bank[:, offset:offset + len(alphas), :] = path + mean_y
        else:
            for target in range(y.shape[1]):
                chosen = np.argsort(
                    -association[:, target], kind='mergesort'
                )[:number]
                scale = safe_sd[chosen] ** power
                z = centered_x[:, chosen] / scale
                q = centered_query[:, chosen] / scale
                path = _ridge_path(
                    z, q, centered_y[:, target:target + 1], w, alphas
                )
                bank[:, offset:offset + len(alphas), target] = (
                    path[:, :, 0] + mean_y[target]
                )
        offset += len(alphas)
    return np.clip(bank, 0.0, 1.0)


def _soft_weights(risk, prior, temperature):
    temperature = max(float(temperature), 1e-12)
    log_weights = np.log(prior) - (risk - risk.min()) / temperature
    weights = np.exp(log_weights - log_weights.max())
    return weights / weights.sum()


def fit_predict(train_x, train_y, test_x, train_groups):
    x = np.asarray(train_x, dtype=float)
    y = np.asarray(train_y, dtype=float)
    query = np.asarray(test_x, dtype=float)
    donors = np.asarray(train_groups['group_ids']).astype(str).reshape(-1)
    blocks = np.asarray(train_groups['block_ids']).astype(str).reshape(-1)
    if x.ndim != 2 or y.shape != (len(x), 3):
        raise ValueError('Expected a training matrix and three target columns.')
    if query.ndim != 2 or query.shape[1] != x.shape[1]:
        raise ValueError('Training and test feature dimensions must agree.')
    if len(donors) != len(x) or len(blocks) != len(x):
        raise ValueError('Training grouping vectors must match training rows.')
    if not np.isfinite(y).all():
        raise ValueError('Targets must be observed; missing labels are not imputed.')
    specifications = [
        ('variance', 250, 0.5, 0.12),
        ('variance', 1000, 0.5, 0.18),
        ('variance', 1000, 1.0, 0.24),
        ('variance', 2000, 1.0, 0.20),
        ('supervised', 64, 1.0, 0.10),
        ('supervised', 256, 1.0, 0.16),
    ]
    alphas = np.array([0.0003, 0.003, 0.03, 0.3, 3.0, 30.0])
    prior = [0.05]
    for specification in specifications:
        prior.extend([0.95 * specification[3] / len(alphas)] * len(alphas))
    prior = np.asarray(prior)
    unique_donors = np.unique(donors)
    if len(unique_donors) < 2:
        weights = np.repeat(prior[:, None], 3, axis=1)
    else:
        donor_losses = []
        for donor in unique_donors:
            validation = donors == donor
            training = ~validation
            bank = _prediction_bank(
                x[training], y[training], x[validation],
                donors[training], blocks[training], specifications, alphas
            )
            validation_weights = _balanced_weights(
                donors[validation], blocks[validation]
            )
            error = bank - y[validation, None, :]
            donor_losses.append(np.einsum(
                'i,imt,imt->mt', validation_weights, error, error,
                optimize=False
            ))
        losses = np.stack(donor_losses, axis=1)
        target_risk = np.sqrt(np.maximum(losses.mean(axis=1), 0.0))
        joint_risk = target_risk.mean(axis=1)
        best_joint = int(np.argmin(joint_risk))
        donor_joint = np.sqrt(losses[best_joint]).mean(axis=1)
        joint_se = donor_joint.std(ddof=1) / np.sqrt(len(unique_donors))
        joint_temperature = max(0.04 * joint_risk[0], 0.35 * joint_se, 1e-8)
        joint_weights = _soft_weights(joint_risk, prior, joint_temperature)
        weights = np.empty((len(prior), 3))
        for target in range(3):
            best = int(np.argmin(target_risk[:, target]))
            donor_rmse = np.sqrt(losses[best, :, target])
            se = donor_rmse.std(ddof=1) / np.sqrt(len(unique_donors))
            temperature = max(0.04 * target_risk[0, target], 0.35 * se, 1e-8)
            individual_weights = _soft_weights(
                target_risk[:, target], prior, temperature
            )
            weights[:, target] = (2.0 * joint_weights + individual_weights) / 3.0
    final_bank = _prediction_bank(
        x, y, query, donors, blocks, specifications, alphas
    )
    predictions = np.einsum('imt,mt->it', final_bank, weights, optimize=False)
    training_weights = _balanced_weights(donors, blocks)
    fallback = np.einsum('i,it->t', training_weights, y, optimize=False)
    predictions = np.where(np.isfinite(predictions), predictions, fallback)
    return np.clip(predictions, 0.0, 1.0)
