import spikeinterface.full as si
from pathlib import Path

# %% helper functions
def load_raw_recording(filepath: Path, include_sync: bool=False):
    try:
        return si.read_cbin_ibl(cbin_file_path=filepath, load_sync_channel=include_sync, stream_name='ap')
    except StopIteration:
        # try with bin file if present
        if bin_file := next(filepath.glob('*.ap.bin'), None):
            return si.read_spikeglx(folder_path=bin_file.parent, load_sync_channel=include_sync, stream_id='imec0.ap')
        else:
            print(f'Issues loading raw recording for {filepath}\nSkipping...\n\n')
            return None

def load_recording(filepath: Path=None, folder: Path=None, concatenate: bool = False, include_sync: bool=False):
    if folder is None:
        folder = filepath.parent
    if not concatenate:
        return load_raw_recording(filepath=filepath, include_sync=include_sync)
    else:  # load and concatenate recording segments
        recs = []
        raw_files = list(folder.rglob('*.cbin'))
        for i, raw_file in enumerate(raw_files):
            rec = load_raw_recording(raw_file, include_sync=include_sync)
            if rec is not None:
                recs.append(rec)
        if not recs:
            print(f'No valid recordings found for {folder}\nSkipping...\n\n')
            return None
        return si.concatenate_recordings(recs)


# %% processing functions
def process_recording(rec: si.BaseRecording, probe_num: int):
    # TODO: implement processing pipeline
    pass