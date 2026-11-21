Gym labs
========

Free-practice exercises for core Python, NumPy, pandas, Matplotlib and seaborn.

* Page types: ``GymHubPage`` (under ``LabsIndexPage``) and ``GymExercisePage``.
* Execution: Pyodide in a Web Worker, one private interpreter per tab. Packages load
  on demand (``labs/gym.py::PACKAGES``); seaborn falls back to micropip.
* Contract: setup (hidden) -> learner code -> check, one shared namespace. A failed
  ``assert`` in the check is the learner's feedback message.
* Infinite loops: the main thread kills the worker after ``GYM_TIMEOUT_SECONDS`` (10)
  and boots a fresh one. No SharedArrayBuffer, so no COOP/COEP headers are needed.
* Persistence: none, deliberately. No localStorage, cookies or network writes.
* Output: stdout/stderr, last-expression repr (DataFrames render as HTML in a
  script-less sandboxed iframe), and Matplotlib/seaborn figures as PNG.
* Gate: ``manage.py check_gym`` runs every solution against its check in a subprocess
  and warns when a starter already passes. ``test_gym.py`` does the same for the seeds.
* Settings (optional): ``GYM_PYODIDE_VERSION``, ``GYM_TIMEOUT_SECONDS``.
