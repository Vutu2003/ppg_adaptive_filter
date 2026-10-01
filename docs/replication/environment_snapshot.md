# CPC replication environment snapshot

- Installation and verification: 2026-09-30 23:53:41 +07:00 (Asia/Ho_Chi_Minh)
- OS: Ubuntu 26.04.1 LTS; Linux 7.0.0-34-generic x86_64
- Project root: `/home/vutu/Desktop/XLTHNC`
- Virtual environment: `/home/vutu/Desktop/XLTHNC/.venv`
- Python executable: `/home/vutu/Desktop/XLTHNC/.venv/bin/python`
- Python: 3.12.10
- pip: 26.2.1
- setuptools: 84.0.0
- wheel: 0.48.0

## Direct project dependencies

| Package | Version |
| --- | --- |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| pandas | 3.0.6 |
| matplotlib | 3.11.2 |
| h5py | 3.16.0 |
| PyYAML | 6.0.3 |
| pytest | 9.1.1 |
| pytest-cov | 7.1.0 |
| tqdm | 4.70.1 |
| psutil | 7.2.2 |

This environment serves the CPC PPG heart-rate replication project. The virtual environment was created with Python 3.12.10 after confirming that this project did not already have one. `requirements.txt` pins the direct dependencies above; pip installs their required transitive dependencies automatically.

Verification: all listed packages and `cpc_ppg` imported; the requested SciPy functions imported; `pip check` found no broken requirements. `pytest --collect-only` found 0 tests, as expected before implementation.
