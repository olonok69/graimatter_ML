# GRAIMATTER disclosure-control demo

Two Python demos of the checks in the [GRAIMATTER green paper](GRAIMATTER%20Green%20Paper.pdf): how a trusted research environment (TRE) can decide whether a trained model is safe to export.

Both use the same synthetic cohort of 1,000 rows. The researcher trains on 500. The TRE keeps 500 aside. There are no real patients.

| Script | What it uses | Output |
| --- | --- | --- |
| `demo/run_demo.py` | A small implementation of the paper's checks | `demo/output/demo_report.txt` |
| `demo/run_sacroml_demo.py` | [SACRO-ML](https://github.com/AI-SDC/SACRO-ML) (`sacroml` 2.0.1), the maintained toolkit from the AI-SDC repository named in the paper | `demo/output/sacroml/` |

Release cut-offs in `demo/graimatter_demo/disclosure.py` apply only to the first script. They are a demo policy. The second script uses the rules shipped inside `sacroml`.

## Setup

Python 3.11 or newer. Install [uv](https://docs.astral.sh/uv/) if it is not already on your PATH.

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen the terminal so `uv` is on your PATH. From the repository root:

```powershell
uv venv --python 3.11
uv pip install -r demo/requirements.txt
```

`demo/requirements.txt` installs `numpy`, `scikit-learn`, and `sacroml`. The `sacroml` install also brings in PyTorch.

Activate the environment.

Windows PowerShell (the leading dot keeps the environment in this session):

```powershell
. .\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

macOS and Linux:

```bash
source .venv/bin/activate
```

`.venv/` is listed in `.gitignore`.

## Hand-written demo

With the environment activated:

```powershell
python demo/run_demo.py
```

Or, without activating it:

```powershell
uv run python demo/run_demo.py
```

The write-up is `demo/output/demo_report.txt`. On the seeded run it refuses an unconstrained decision tree (membership AUC 0.708, training accuracy 1.000 against 0.590 on the set-aside) and releases the same data through the safe wrapper (membership AUC 0.528). It also refuses k-nearest neighbours and a standard support-vector classifier because they store training rows, catches a model edited after `fit()`, and blocks a 20-row attribute sweep after one allowed patient query.

Section-by-section notes are in [demo/README.md](demo/README.md). Edit `demo/constraints.json` to change the hyperparameter envelope. The wrapper in this script uses a minimum leaf size of 20.

## Official SACRO-ML demo

```powershell
uv run python demo/run_sacroml_demo.py
```

This calls `SafeDecisionTreeClassifier`, `request_release()`, the worst-case membership attack, the structural attack, and attribute inference. Each attack writes `report.json` and `report.pdf`. A short summary is `demo/output/sacroml/sacroml_report.txt`.

On the seeded run the package rejects `min_samples_leaf=1`, raises it to 5, and records "Proceed to next step of checking". Changing that parameter after `fit()` is caught. The structural attack flags the unconstrained tree (smallest leaf holds 1 row). The wrapped tree still has a generalisation gap of about 0.30, and a leaf of 5 is still marked risky because the package threshold is 10. Worst-case membership AUC stays near 0.5 for both trees: that attack uses predicted probabilities only, and a tree of pure leaves is extreme on training rows and set-aside rows.

The package can also run a likelihood-ratio attack. The upstream example uses 100 shadow models, so this script does not start it. To run that attack, pass a `Target` into `request_release()` as described in the [SACRO-ML examples](https://github.com/AI-SDC/SACRO-ML/tree/main/examples).
