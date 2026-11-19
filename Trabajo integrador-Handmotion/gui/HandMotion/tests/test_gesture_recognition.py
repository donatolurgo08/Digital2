"""Pruebas del clasificador de gestos; fixtures sintéticos, no calibración."""

from __future__ import annotations

import unittest

from hand_motion.logic.gesture_recognition import (
    REST,
    X_NEGATIVE,
    X_NEUTRAL,
    X_POSITIVE,
    Y_NEGATIVE,
    Y_POSITIVE,
    Z_NEGATIVE,
    Z_POSITIVE,
    GestureRecognizer,
    TiltBaseline,
    TiltThresholds,
    classify_tilt,
    recognize_gesture,
)


# Estos valores existen solo para comprobar la lógica del clasificador.
SYNTHETIC_NEGATIVE_THRESHOLD_G = -0.25
SYNTHETIC_POSITIVE_THRESHOLD_G = 0.25
SYNTHETIC_BASELINE = TiltBaseline(x_g=0.0, y_g=0.0, z_g=1.0)
SYNTHETIC_THRESHOLDS = TiltThresholds(x_g=0.25, y_g=0.25, z_g=0.25)


class XReferenceClassifierTests(unittest.TestCase):
    def test_synthetic_windows_classify_x_direction(self) -> None:
        fixtures = (
            ([-0.62, -0.55, -0.71, -0.64, -0.59], X_NEGATIVE),
            ([0.04, -0.08, 0.03, 0.00, -0.02], X_NEUTRAL),
            ([0.58, 0.69, 0.61, 0.54, 0.66], X_POSITIVE),
        )
        for samples, expected in fixtures:
            self.assertEqual(
                recognize_gesture(
                    samples,
                    negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
                    positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
                ),
                expected,
            )

    def test_threshold_boundaries_are_inclusive(self) -> None:
        self.assertEqual(
            recognize_gesture(
                [-0.25],
                negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
                positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
            ),
            X_NEGATIVE,
        )
        self.assertEqual(
            recognize_gesture(
                [0.25],
                negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
                positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
            ),
            X_POSITIVE,
        )

    def test_empty_window_returns_none(self) -> None:
        self.assertIsNone(
            recognize_gesture(
                [],
                negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
                positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
            )
        )

    def test_invalid_thresholds_or_nonfinite_samples_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            recognize_gesture(
                [0.0],
                negative_threshold_g=0.2,
                positive_threshold_g=-0.2,
            )
        with self.assertRaises(ValueError):
            recognize_gesture(
                [float("nan")],
                negative_threshold_g=SYNTHETIC_NEGATIVE_THRESHOLD_G,
                positive_threshold_g=SYNTHETIC_POSITIVE_THRESHOLD_G,
            )


class TiltClassifierTests(unittest.TestCase):
    def test_classify_tilt_uses_dominant_axis_and_sign(self) -> None:
        fixtures = (
            ((0.50, 0.00, 1.00), X_POSITIVE),
            ((-0.50, 0.00, 1.00), X_NEGATIVE),
            ((0.00, 0.40, 1.00), Y_POSITIVE),
            ((0.00, -0.40, 1.00), Y_NEGATIVE),
            ((0.00, 0.00, 0.50), Z_NEGATIVE),
            ((0.00, 0.00, 1.50), Z_POSITIVE),
            ((0.10, 0.10, 1.10), REST),
            ((0.30, -0.40, 1.00), Y_NEGATIVE),
        )
        for sample, expected in fixtures:
            with self.subTest(sample=sample):
                self.assertEqual(
                    classify_tilt(
                        *sample,
                        baseline=SYNTHETIC_BASELINE,
                        thresholds=SYNTHETIC_THRESHOLDS,
                    ),
                    expected,
                )

    def test_threshold_is_inclusive_and_z_is_optional(self) -> None:
        self.assertEqual(
            classify_tilt(
                0.25,
                0.0,
                1.0,
                baseline=SYNTHETIC_BASELINE,
                thresholds=SYNTHETIC_THRESHOLDS,
            ),
            X_POSITIVE,
        )
        self.assertEqual(
            classify_tilt(
                0.50,
                0.0,
                None,
                baseline=SYNTHETIC_BASELINE,
                thresholds=SYNTHETIC_THRESHOLDS,
            ),
            X_POSITIVE,
        )

    def test_rejects_invalid_thresholds_and_samples(self) -> None:
        for threshold_values in ((0.0, 0.25, 0.25), (0.25, -0.1, 0.25)):
            with self.subTest(thresholds=threshold_values):
                with self.assertRaises(ValueError):
                    TiltThresholds(*threshold_values)

        for sample in ((float("nan"), 0.0, 1.0), (0.0, float("inf"), 1.0)):
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    classify_tilt(
                        *sample,
                        baseline=SYNTHETIC_BASELINE,
                        thresholds=SYNTHETIC_THRESHOLDS,
                    )

        with self.assertRaises(ValueError):
            TiltBaseline(x_g=float("nan"))


class GestureRecognizerTests(unittest.TestCase):
    def test_requires_baseline_and_confirms_with_hold(self) -> None:
        recognizer = GestureRecognizer(
            thresholds=SYNTHETIC_THRESHOLDS,
            window_samples=3,
            hold_samples=2,
        )
        self.assertFalse(recognizer.calibrated)
        for _ in range(6):
            self.assertIsNone(recognizer.add_sample(0.0, 0.0, 1.0))
        self.assertEqual(recognizer.current_mean(), (0.0, 0.0, 1.0))

        recognizer.set_baseline(SYNTHETIC_BASELINE)
        self.assertTrue(recognizer.calibrated)

        # Tres muestras completan la ventana; la segunda clasificación confirma.
        self.assertIsNone(recognizer.add_sample(0.0, 0.0, 1.0))
        self.assertIsNone(recognizer.add_sample(0.0, 0.0, 1.0))
        self.assertIsNone(recognizer.add_sample(0.0, 0.0, 1.0))
        self.assertEqual(recognizer.add_sample(0.0, 0.0, 1.0), REST)

        # La media tarda en salir del reposo; luego X+ se confirma.
        gesture = None
        for _ in range(5):
            gesture = recognizer.add_sample(0.5, 0.0, 1.0)
        self.assertEqual(gesture, X_POSITIVE)

    def test_reset_clear_baseline_and_window_change(self) -> None:
        recognizer = GestureRecognizer(
            thresholds=SYNTHETIC_THRESHOLDS,
            baseline=SYNTHETIC_BASELINE,
            window_samples=3,
            hold_samples=1,
        )
        for _ in range(3):
            recognizer.add_sample(0.5, 0.0, 1.0)
        self.assertEqual(recognizer.gesture, X_POSITIVE)

        recognizer.reset()
        self.assertIsNone(recognizer.gesture)
        self.assertIsNone(recognizer.current_mean())

        recognizer.set_window_samples(5)
        self.assertEqual(recognizer.window_samples, 5)
        recognizer.clear_baseline()
        self.assertFalse(recognizer.calibrated)
        self.assertIsNone(recognizer.add_sample(0.5, 0.0, 1.0))

        with self.assertRaises(ValueError):
            recognizer.set_window_samples(0)


if __name__ == "__main__":
    unittest.main()
