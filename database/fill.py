from . import *

def run(cas):
    reference_filler.run(cas)
    date_filler.run(cas)
    average_temperature_filler.run(cas)
    temperature_repro.run(cas)
    tox_table_filler.run(cas)