# Patient-specific age from an appended control index date

This small OpenSAFELY/ehrQL project proves that a date loaded with
`table_from_file()` can be passed directly to `patients.age_on()`. It deliberately
keeps `analysis/dataset_definition.py` close to the original code.

The checked-in proof input contains four controls:

| patient_id | patients row | index date | expected result |
| --- | --- | --- | --- |
| 1 | yes | 2020-03-31 | age 40 |
| 2 | yes | 2021-06-15 | age 20 |
| 3 | no | 2022-01-01 | missing age |
| 4 | yes | missing | missing age |

This demonstrates the two inputs required for a non-missing age: the control ID
must join to the backend `patients` table, and that control must have a non-missing
`index_date`.

## Run the proof

Install the environment if needed:

```sh
uv sync
```

Run the assurance scenarios:

```sh
.venv/bin/ehrql assure analysis/test_dataset_definition.py
```

Generate the proof dataset from aligned dummy tables:

```sh
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py --dummy-tables dummy-tables
```

The output should contain four rows. Patients 1 and 2 have ages; patient 3 has no
matching row in `dummy-tables/patients.csv`, and patient 4 has no index date,
so their ages are intentionally missing.

To save the output explicitly when using the local ehrQL environment instead:

```sh
.venv/bin/ehrql generate-dataset \
  analysis/dataset_definition.py \
  --dummy-tables dummy-tables/ \
  --output output/proof_dataset.csv
```

## Debugging mostly missing ages

The expression below is valid and supports a different index date for every
patient:

```python
dataset.age = patients.age_on(indexed_controls.index_date)
```

Temporarily add these columns to the real extraction:

```python
dataset.has_patient_record = patients.exists_for_patient()
dataset.date_of_birth = patients.date_of_birth
dataset.index_date_is_missing = indexed_controls.index_date.is_null()
dataset.patient_table_sex = patients.sex
```

Then inspect aggregate counts rather than disclosive row-level data:

- If `index_date_is_missing` is true, inspect the upstream script that appends the
  index date. Confirm that the written values use `YYYY-MM-DD` and that the file
  column is really named `index_date`.
- If `has_patient_record` is false while the file's `index_date` and `sex` are
  populated, the external control ID does not join to the current backend's
  `patients` table. The file's own columns can still appear because they come from
  `indexed_controls`, not from the backend.
- If `has_patient_record` and `index_date` are both present, inspect
  `date_of_birth`. In the normal TPP/core patients schema it should be present, and
  `age_on()` should consequently return an integer.
- Do not change the population to
  `indexed_controls.exists_for_patient() & patients.exists_for_patient()` merely to
  remove missing ages. That hides the join failure by silently dropping controls.

### Common reasons IDs do not join

- The controls were produced against a different backend or database snapshot.
- An intermediate Python/R script changed, renumbered, rounded, or regenerated
  `patient_id`.
- The second OpenSAFELY action is not downstream of the matching/index-appending
  action in `project.yaml`.
- A local run used ehrQL's automatically generated dummy data. Its generated IDs
  are not guaranteed to match IDs in a checked-in controls file. Use aligned dummy
  tables, as this proof does.
- The file contains duplicate `patient_id` values. `table_from_file()` represents a
  patient-level table and requires one row per patient.

For a production pipeline, preserve `patient_id` exactly, run the dependent actions
against the same backend, and declare the extraction action as needing the action
that creates `output/ctc_data_ptnl_controls_indexappended.csv.gz`.

## OpenSAFELY action

`project.yaml` contains the production-shaped extraction command. In the real
project, add the upstream action name to its `needs` list. The checked-in proof can
be run locally with the explicit `--dummy-tables` command above.

## Open in GitHub Codespaces

Open the repository's Codespaces link, choose **Create codespace**, and wait for
the development container to finish. The OpenSAFELY command-line tools are already
configured by `.devcontainer/devcontainer.json`.

From the Codespaces terminal, run:

```sh
opensafely exec ehrql:v1 assure analysis/test_dataset_definition.py
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py --dummy-tables dummy-tables
```

The controls file under `output/` is intentionally committed dummy data for this
demonstration. Never commit a real controls extract or other patient-level data.

## Safety notice

This is a technical demonstration using dummy data. It is not a validated study
definition and must not be used to draw clinical, policy, or safety conclusions.
