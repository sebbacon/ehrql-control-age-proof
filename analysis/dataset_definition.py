import datetime

from ehrql import create_dataset, table_from_file
from ehrql.tables.tpp import patients


CONTROLS = "output/ctc_data_ptnl_controls_indexappended.csv.gz"

indexed_controls = table_from_file(
    CONTROLS,
    columns={
        "sex": str,
        "index_date": datetime.date,
    },
)

dataset = create_dataset()
dataset.define_population(indexed_controls.exists_for_patient())

dataset.index_date = indexed_controls.index_date
dataset.age = patients.age_on(indexed_controls.index_date)
dataset.sex = indexed_controls.sex
