"""Random polynomial generation constrained by a total-sum budget."""

import random


def generate_random_polynomial(degree, max_sum, coeff_range=(-10.0, 10.0), num_points=None):
    """Generate random coefficients for a degree-`degree` polynomial.

    The polynomial P(x) = a0 + a1*x + ... + a_degree*x^degree is built from
    coefficients drawn uniformly from `coeff_range`. If the sum of P(x) for
    x = 1..num_points would exceed `max_sum`, all coefficients are scaled
    down proportionally so the sum lands exactly at `max_sum` instead.

    Args:
        degree: Non-negative integer degree of the polynomial.
        max_sum: Upper bound that sum(P(x) for x in 1..num_points) must not exceed.
        coeff_range: (low, high) range each coefficient is sampled from before scaling.
        num_points: How many positive integers (1..num_points) to sum P(x) over.
            Defaults to `degree` (or 1, if degree is 0).

    Returns:
        List of coefficients [a0, a1, ..., a_degree].
    """
    if degree < 0:
        raise ValueError("degree must be non-negative")
    if num_points is None:
        num_points = max(degree, 1)
    if num_points < 1:
        raise ValueError("num_points must be >= 1")

    coeffs = [random.uniform(*coeff_range) for _ in range(degree + 1)]

    total = sum(
        sum(c * x ** k for k, c in enumerate(coeffs))
        for x in range(1, num_points + 1)
    )

    if total > max_sum and total != 0:
        scale = max_sum / total
        coeffs = [c * scale for c in coeffs]

    return coeffs
