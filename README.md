Stone-quality recommendation for Glamira
==============================

Project Organization
------------

    ├── README.md          <- The top-level README for developers using this project.
    ├── data               <- Store data from scirpt get_data_from_db.py
    ├── model              <- Store probabilities data use for recommendation
    ├── src                <- Source code in this project.
    │    ├── __init__.py        <- Makes src a Python module.
    │    ├── pathmagic.py       <- Dynamic link between script modules.
    │    ├── run.py             <- Run a full cycle processing.
    │    ├── data
    │    │     └── get_data_from_db.py    <- Get transaction data from 7-nearest day start from a specific day.
    │    ├── model
    │    │     ├── prob.py                <- Calculate relevance probs data.
    │    │     └── predict.py             <- Calculate quality recommendation given product and stone.
    │    ├── util
    │    │     └── path.py                <- Store all path used in this project.

------------
Run

1. Activate virtual envs: source /home/ntq/virtualenv/tf17py3/bin/activate
2. Run 'python {PROJECT_ROOT}/src/run.py --from_date=desire_date (%Y-%m-%d)' or set value to None to select today date.
3. Result file are store in {PROJECT_ROOT}/model/{run-date folder}/{run-date file}.csv.