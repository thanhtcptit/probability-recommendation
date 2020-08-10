Recommendation by Probability
==============================

Project Organization
------------

    ├── README.md          <- The top-level README for developers using this project.
    ├── data               <- Store data from scirpt get_data_from_db.py
    ├── model              <- Store probabilities data use for recommendation
    ├── src                <- Source code in this project.
    │    ├── __init__.py        <- Makes src a Python module.
    │    ├── config.json        <- Store configs.
    │    ├── run.py             <- Run a full cycle processing.
    │    ├── data
    │    │     └── get_data_from_db.py    <- Get transaction data from 7-nearest day start from a specific day.
    │    ├── model
    │    │     ├── prob.py                <- Calculate relevance probs data.
    │    │     └── predict.py             <- Calculate recommendation given product and stone.
    │    ├── util
    │    │     └── path.py                <- Store all path used in this project.

------------

Run
------------

1. Activate virtual envs
2. Run 'python {PROJECT_ROOT}/src/run.py --from_date=desire_date (%Y-%m-%d)' or set value to None to select today date.
------------