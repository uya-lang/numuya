from pathlib import Path

import numpy as np


def main() -> None:
    fixture_dir = Path(__file__).resolve().parent
    fixture_dir.mkdir(parents=True, exist_ok=True)

    np.save(
        fixture_dir / "f64_1d.npy",
        np.array([1.0, 2.5, -3.0, 8.25], dtype=np.float64),
    )
    np.save(
        fixture_dir / "f64_2d.npy",
        np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64),
    )
    np.save(
        fixture_dir / "f64_empty.npy",
        np.array([], dtype=np.float64),
    )
    np.save(
        fixture_dir / "i32_1d.npy",
        np.array([1, -2, 7, 42], dtype=np.int32),
    )


if __name__ == "__main__":
    main()
