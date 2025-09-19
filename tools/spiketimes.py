import polars as pl
import numpy as np
from pathlib import Path
from spikeinterface.core import BaseRecording, ChunkRecordingExecutor

# %% Helpers
def load_alignment_data(filename: Path, ):
    "load alignment table with unit->channelid->brain region info"
    pass

def get_rec_spikes():
    'get spikes for duration of recording, start stop ideally from sync signal'
    pass

def get_spike_times():
    'get spike times for each unit; sample time to rec time, in secs'
    pass

def merge_unit_data():
    pass


# def spikes_to_rates():
#     pass

# - iterate over alignment units
# - get spike vector, transform as needed and merge
#   - transform:
#     - get spikes from rec duration, 
#     - convert spike times to seconds, from rec start 
#     - need: start stop, fs, sync (maybe)
#   - merge with alignment data
#   - save per recording: alignmenta data + now spike times in secs, drop index if too large
# - separately, aggregate by animal and then by project
# ---> analysis scripts