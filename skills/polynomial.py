"""Random polynomial generation constrained by a total-sum budget."""

import random


def generate_random_polynomial(degree, max_sum, coeff_range=(-10.0, 10.0), num_points=None):
    """Generate random coefficients for a degree-`degree` polynomial.

    The polynomial P(x) = a0 + a1*x + ... + a_degree*x^degree is built from
    coefficients drawn uniformly from `coeff_range`, then all coefficients
    are scaled proportionally (up or down) so that the sum of P(x) for
    x = 1..num_points lands exactly at `max_sum`. On the rare draw whose sum
    is exactly zero (so it can't be scaled to anything nonzero), the
    coefficients are redrawn until the sum is nonzero.

    Args:
        degree: Non-negative integer degree of the polynomial.
        max_sum: Target that sum(P(x) for x in 1..num_points) is scaled to hit exactly.
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

    def draw():
        return [random.uniform(*coeff_range) for _ in range(degree + 1)]

    def total_over_range(coeffs):
        return sum(
            sum(c * x ** k for k, c in enumerate(coeffs))
            for x in range(1, num_points + 1)
        )

    coeffs = draw()
    total = total_over_range(coeffs)
    while total == 0:
        coeffs = draw()
        total = total_over_range(coeffs)

    scale = max_sum / total
    return [c * scale for c in coeffs]
