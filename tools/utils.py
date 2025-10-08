import spikeinterface.full as si
from pathlib import Path

# %% helper functions
def find_raw_files(raw_folder: Path, recording_name: str, concatenate: bool=False):
    raw_folders = list(raw_folder.glob(f'{recording_name}*'))
    if concatenate:  # if multiple raw folders, raw_files will be list of lists
            assert len(raw_folders) > 1, f"(!) No multiple raw data folders found for recording: {recording_name}\nExpected in: {raw_folder}\nSkipping...\n\n"
            print(f'Found multiple raw folders for {recording_name}: {x}')
            raw_files = []
            for folder in raw_folders:
                segment_raw_files = list(folder.rglob(f'{recording_name}*.cbin'))
                if segment_raw_files:
                    raw_files.append(segment_raw_files)
            print(f'Found:\n\t{raw_files}')
    elif len(raw_folders) > 0:  # single raw folder
        # if multiple files, likely multiple probes
        match raw_files := list(raw_folder.rglob(f'{recording_name}*imec*.cbin')):
            case x if len(x) > 1:
                print(f'Found multiple raw files for {recording_name}: {x}')
            case _:
                print(f'Found single raw file for {recording_name}: {raw_files}')
    else:
        return None
    return raw_files


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

def load_recording(filepath: Path|list|None=None, folder: Path|None=None, concatenate: bool = False, include_sync: bool=False):
    if filepath and (folder is None):
        folder = filepath.parent
    else:
        assert folder is not None, 'Either filepath or folder must be provided'
    
    if not concatenate:
        return load_raw_recording(filepath=filepath, include_sync=include_sync)
    else:
        if isinstance(filepath, list):  # list of files to concatenate
            recs = []
            raw_files = filepath
        else:
            raise ValueError('For concatenation, filepath must be a list of file paths')
        for raw_file in raw_files:
            rec = load_raw_recording(raw_file, include_sync=include_sync)
            if rec is not None:
                recs.append(rec)
        if not recs:
            print(f'No valid recordings found for {folder}\nSkipping...\n\n')
            return None
        return si.concatenate_recordings(recs)