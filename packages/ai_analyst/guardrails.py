def probability_label(probability: float | None) -> str:
    if probability is None:
        return "NÃO CALIBRADA"
    if not 0 <= probability <= 1:
        raise ValueError("probability must be within [0,1]")
    return f"{probability:.1%}"
