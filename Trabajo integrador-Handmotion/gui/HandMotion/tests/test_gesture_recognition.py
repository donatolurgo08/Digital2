"""Fixtures sintéticos; sus amplitudes/umbrales no son calibración física."""

from hand_motion.logic.gesture_recognition import (
    X_NEGATIVE,
    X_NEUTRAL,
    X_POSITIVE,
    recognize_gesture,
)


# Estos valores existen solo para comprobar la lógica del clasificador.
SYNTHETIC_NEGATIVE_THRESHOLD_G = -0.25
SYNTHETIC_POSITIVE_THRESHOLD_G = 0.25


def test_synthetic_windows_classify_x_direction() -> None:
    fixtures = (
        ([-0.62, -0.55, -0.71, -0.64, -0.59], X_NEGATIVE),
        ([0.04, -0.08, 0.03, 0.00, -0.02], X_NEUTRAL),
        ([0.58, 0.69, 0.61, 0.54, 0.66], X_POSITIVE),
    )
    for samples, expected in fixtures:
        assert recognize_gesture(
            samples,
            negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
            positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
        ) == expected


def test_threshold_boundaries_are_inclusive() -> None:
    assert recognize_gesture(
        [-0.25],
        negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
        positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
    ) == X_NEGATIVE
    assert recognize_gesture(
        [0.25],
        negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
        positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
    ) == X_POSITIVE


def test_empty_window_returns_none() -> None:
    assert recognize_gesture(
        [],
        negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
        positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
    ) is None


def test_invalid_thresholds_or_nonfinite_samples_are_rejected() -> None:
    invalid_cases = (
        ([0.0], 0.2, -0.2),
        ([float("nan")], -0.2, 0.2),
    )
    for samples, negative, positive in invalid_cases:
        try:
            recognize_gesture(
                samples,
                negative_threshold_g=negative,
                positive_threshold_g=positive,
            )
        except ValueError:
            continue
        raise AssertionError("Se aceptó una ventana o umbrales inválidos")
