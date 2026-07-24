import random
import unittest

from polynomial import generate_random_polynomial


def poly_sum(coeffs, num_points):
    return sum(
        sum(c * x ** k for k, c in enumerate(coeffs))
        for x in range(1, num_points + 1)
    )


class GenerateRandomPolynomialTests(unittest.TestCase):
    def test_scales_sum_to_max_sum_exactly(self):
        random.seed(1)
        coeffs = generate_random_polynomial(degree=2, max_sum=100, num_points=10)
        self.assertAlmostEqual(poly_sum(coeffs, 10), 100)

    def test_scales_up_when_raw_sum_is_below_max_sum(self):
        # coeff_range pinned tight and positive so the raw sum is small and
        # well below max_sum, forcing an upward rather than downward scale.
        random.seed(1)
        coeffs = generate_random_polynomial(
            degree=1, max_sum=1000, coeff_range=(0.01, 0.02), num_points=5
        )
        self.assertAlmostEqual(poly_sum(coeffs, 5), 1000)

    def test_degree_negative_raises(self):
        with self.assertRaises(ValueError):
            generate_random_polynomial(degree=-1, max_sum=10)

    def test_num_points_defaults_to_degree(self):
        random.seed(1)
        coeffs = generate_random_polynomial(degree=3, max_sum=50)
        self.assertAlmostEqual(poly_sum(coeffs, 3), 50)

    def test_resamples_on_zero_sum_draw(self):
        # First draw (a0=1, a1=-1) sums to zero at x=1; the function must
        # discard it and redraw rather than returning an unscaled polynomial.
        scripted = iter([1.0, -1.0, 2.0, 3.0])

        def fake_uniform(_low, _high):
            return next(scripted)

        original_uniform = random.uniform
        random.uniform = fake_uniform
        try:
            coeffs = generate_random_polynomial(degree=1, max_sum=100, num_points=1)
        finally:
            random.uniform = original_uniform

        self.assertAlmostEqual(poly_sum(coeffs, 1), 100)


if __name__ == "__main__":
    unittest.main()
