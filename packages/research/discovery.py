from dataclasses import dataclass
from itertools import combinations
from math import inf


@dataclass(frozen=True)
class PatternCandidate:
    features: tuple[str, ...]
    occurrences: int
    mean_forward_return: float
    stability: float


def discover_binary_patterns(
    rows: list[dict[str, float | bool]],
    *,
    feature_names: list[str],
    target: str,
    min_features: int = 2,
    max_features: int = 4,
    min_occurrences: int = 30,
) -> list[PatternCandidate]:
    """Generate hypotheses only. Candidates still require temporal OOS validation."""
    if min_features < 1 or max_features < min_features:
        raise ValueError("invalid feature range")
    candidates: list[PatternCandidate] = []
    for size in range(min_features, min(max_features, len(feature_names)) + 1):
        for combo in combinations(feature_names, size):
            matched = [r for r in rows if all(bool(r.get(name, False)) for name in combo)]
            if len(matched) < min_occurrences:
                continue
            values = [float(r[target]) for r in matched if target in r]
            if len(values) < min_occurrences:
                continue
            mean = sum(values) / len(values)
            positive = sum(1 for value in values if value > 0)
            negative = sum(1 for value in values if value < 0)
            directional = max(positive, negative) / len(values) if values else 0.0
            candidates.append(PatternCandidate(combo, len(values), mean, directional))
    return sorted(
        candidates,
        key=lambda x: (abs(x.mean_forward_return) * x.stability, x.occurrences),
        reverse=True,
    )


def family_budget(feature_count: int, max_features: int) -> int:
    """Expose search-space size so multiple-testing risk is visible."""
    if feature_count < 0 or max_features < 1:
        raise ValueError("invalid search-space inputs")
    total = 0
    for size in range(1, min(feature_count, max_features) + 1):
        total += _n_choose_k(feature_count, size)
    return total


def _n_choose_k(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    result = 1
    for i in range(1, k + 1):
        result = result * (n - i + 1) // i
    return result


def bonferroni_alpha(alpha: float, hypotheses: int) -> float:
    if not 0 < alpha < 1 or hypotheses < 1:
        raise ValueError("invalid alpha or hypothesis count")
    return alpha / hypotheses


def safe_score(candidate: PatternCandidate, min_stability: float = 0.55) -> float:
    if candidate.stability < min_stability:
        return -inf
    return abs(candidate.mean_forward_return) * candidate.stability
