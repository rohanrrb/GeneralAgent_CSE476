# CSE 476 - General Agent 

To run this agent use the command structure: 

`python generate_answer_template.py <path to dev/test set> --dev <bool> --classify <bool>`

These flags are **not** robust and so the command should be run directly as given. Below is 
the command to simply generate answers for the test set assuming the file has not been renamed and is in the base dir of this project. 

`python generate_answer_template.py cse_476_final_project_test_data.json --dev False --classify False`

or 

`python generate_answer_template.py`

For verbose run on dev set:

`python generate_answer_template.py cse476_final_project_dev_data.json --dev True --classify True`

Without classification evaluation:

`python generate_answer_template.py cse476_final_project_dev_data.json --dev True --classify False`

### Flags

- `--dev True` indicates the input file has ground-truth output to generate perf metrics
- `--classify True` indicates the input file has ground-truth domain for which the classifications step alone will be run for generating perf metrics


