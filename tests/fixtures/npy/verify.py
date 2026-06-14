from pathlib import Path

import numpy as np
from numpy.lib import format as fmt


def verify_fixture(path: Path, expected_shape: tuple[int, ...], expected_values: object) -> None:
    with path.open("rb") as handle:
        version = fmt.read_magic(handle)
        if version == (1, 0):
            shape, fortran_order, dtype = fmt.read_array_header_1_0(handle)
        elif version == (2, 0):
            shape, fortran_order, dtype = fmt.read_array_header_2_0(handle)
        else:
            raise AssertionError(f"{path.name}: unexpected npy version {version}")

    assert version == (1, 0), f"{path.name}: expected version (1, 0), got {version}"
    assert dtype.str == "<f8", f"{path.name}: expected dtype <f8, got {dtype.str}"
    assert not fortran_order, f"{path.name}: expected C-order array"
    assert shape == expected_shape, f"{path.name}: expected shape {expected_shape}, got {shape}"

    values = np.load(path).tolist()
    assert values == expected_values, f"{path.name}: expected values {expected_values}, got {values}"


def verify_dtype_fixture(
    path: Path,
    expected_shape: tuple[int, ...],
    expected_values: object,
    expected_dtype: str,
) -> None:
    with path.open("rb") as handle:
        version = fmt.read_magic(handle)
        if version == (1, 0):
            shape, fortran_order, dtype = fmt.read_array_header_1_0(handle)
        elif version == (2, 0):
            shape, fortran_order, dtype = fmt.read_array_header_2_0(handle)
        else:
            raise AssertionError(f"{path.name}: unexpected npy version {version}")

    assert version == (1, 0), f"{path.name}: expected version (1, 0), got {version}"
    assert dtype.str == expected_dtype, f"{path.name}: expected dtype {expected_dtype}, got {dtype.str}"
    assert not fortran_order, f"{path.name}: expected C-order array"
    assert shape == expected_shape, f"{path.name}: expected shape {expected_shape}, got {shape}"

    values = np.load(path).tolist()
    assert values == expected_values, f"{path.name}: expected values {expected_values}, got {values}"


def main() -> None:
    fixture_dir = Path(__file__).resolve().parent
    verify_fixture(fixture_dir / "f64_1d.npy", (4,), [1.0, 2.5, -3.0, 8.25])
    verify_fixture(fixture_dir / "f64_2d.npy", (2, 3), [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    verify_fixture(fixture_dir / "f64_empty.npy", (0,), [])
    verify_dtype_fixture(fixture_dir / "i32_1d.npy", (4,), [1, -2, 7, 42], "<i4")
    print("verified 4 npy fixtures")


if __name__ == "__main__":
    main()
