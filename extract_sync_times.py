import numpy as np
from pprint import pprint
from pathlib import Path
from tools.settings import settings
from scipy.signal import find_peaks
from tools.spikesorting import load_recording
from spikeinterface.core import BaseRecording, ChunkRecordingExecutor

# %% functions
def get_sync_timestamps(
        recording: BaseRecording,
        threshold=None,
        verbose: bool = False,
        **job_kwargs
):
    
    # executor
    func = _get_sync_times_chunk
    init_func = _init_sync_times_chunk
    init_args = (recording,threshold)
    executor = ChunkRecordingExecutor(
        recording,
        func,
        init_func,
        init_args,
        job_name='get_sync_times',
        verbose=verbose,
        handle_returns=True,
        **job_kwargs
    )
    results = executor.run()

    if results is None:
        return [], []

    ping_samples = []
    ping_times = []

    for res in results:
        samples, times = res
        ping_samples.extend(np.atleast_1d(samples))
        ping_times.extend(np.atleast_1d(times))

    return np.array(ping_samples), np.array(ping_times)

def _init_sync_times_chunk(recording: BaseRecording, threshold=None):
    # create local dict for each worker
    worker_ctx = {}
    worker_ctx["recording"] = recording
    worker_ctx["times"] = recording.get_times()
    worker_ctx["threshold"] = threshold
    return worker_ctx

def _get_sync_times_chunk(
        segment_index, start_frame, end_frame, worker_ctx):
    """
    A function that will be executed on each chunk.
    `chunk` is a numpy array (n_samples, n_channels).
    `start_frame` is the starting sample index of the chunk.
    `worker_index` is the parallel worker index.
    `job_kwargs` contains the chunking parameters.
    """
    recording = worker_ctx["recording"]
    times = worker_ctx["times"]
    threshold = worker_ctx["threshold"]

    traces = recording.get_traces(start_frame=start_frame, end_frame=end_frame, segment_index=segment_index, return_scaled=True)
    # --- Detection Logic ---
    if threshold is not None:
        # Find where the signal crosses the threshold from below
        crossings = np.where((traces[:-1] < threshold) & (traces[1:] >= threshold))[0]
        local_peaks = crossings
    else:
        # Alternative: Using np.diff and find_peaks
        diffs = np.diff(traces.squeeze())
        # Define findpeaks_kwargs inside or pass them as an argument
        findpeaks_kwargs = dict(height=0.5, prominence=0.5) # Use a sensible height for diffs
        local_peaks, _ = find_peaks(diffs, **findpeaks_kwargs)

    # Convert local chunk indices to global recording indices
    # the offset is the start of the *current* chunk
    ping_samples = local_peaks + start_frame
    ping_times = times[ping_samples]
    return ping_samples, ping_times

def get_recording_sync(
        raw_file: Path,
        rec_folder: Path,
        probe_num: int,
        overwrite: bool = False,
        threshold=None,
        verbose: bool = False,
        sync_job_kwargs: dict = dict(n_jobs=8, chunk_duration='10s', progress_bar=True)
):
        global settings
        output_dir = settings.paths.output_dir
        ## get sync times
        # load recording sync channel
        assert f'imec{probe_num}' in raw_file.name, f"(!) Expected imec{probe_num} in {raw_file.name}\nSkipping...\n\n"
        raw_sync = load_recording(raw_file, include_sync=True)
        raw_sync = raw_sync.channel_slice(channel_ids=[raw_sync.channel_ids[-1]]) # type: ignore

        # get ping times - get sample indices
        data_output = rec_folder / output_dir
        if not overwrite and len(list(data_output.glob(f'ping*probe{probe_num}.npy'))) > 1:
            try:
                ping_samples = np.load(data_output / f'ping_samples_probe{probe_num}.npy')
                ping_times = np.load(data_output / f'ping_times_probe{probe_num}.npy')
                print(f'Loaded existing sync timestamps to {data_output}')
                print(f'Found {len(ping_samples)} sync timestamps for probe {probe_num} in {raw_file.stem}')
            except Exception as e:
                print(f'(!) Error loading existing sync timestamps for probe {probe_num} in {raw_file.stem}: {e}\nSkipping...\n\n')
                return None, None
        else:
            ping_samples, ping_times = get_sync_timestamps(raw_sync, threshold=threshold, verbose=verbose, **sync_job_kwargs)
            if ping_samples.size==0: # type: ignore
                print(f'(!) No sync timestamps found for probe {probe_num} in {raw_file.stem}\nSkipping...\n\n')
                return None, None
            
            # save to simple npy
            np.save(data_output / f'ping_samples_probe{probe_num}.npy', ping_samples)
            np.save(data_output / f'ping_times_probe{probe_num}.npy', ping_times)
            print(f'Found {len(ping_samples)} sync timestamps for probe {probe_num} in {raw_file.stem}')
            print(f'Saved sync timestamps to {data_output}')
        return ping_samples, ping_times

# %% main processing loop
def get_all_sync():
    for session, properties in recording_sessions.items():
        animal = session.split('_')[0]
        recording_name = session
        concatenate = properties['concatenate']
        print(f'---processing  {recording_name}{", multiple recordings..." if concatenate else ""}')

        # find session folder
        rec_folder = batch_folder / animal / recording_name
        if rec_folder.exists():
            print(f'recording session folder:  {rec_folder}')  # top-level
        else:
            print(f'(!) No recording session folder found for:  {rec_folder}\nSkipping...\n\n')
            continue

        # check for multiple probes, essentially are there multiple .cbin/.bin files?
        raw_folder = rec_folder / raw_dir
        assert raw_folder.exists(), f"(!) No raw data folder found for recording: {rec_folder}\nExpected in: {raw_folder}\nSkipping...\n\n"
        match raw_files := list(raw_folder.rglob(f'{recording_name}*imec*.cbin')):
            case x if len(x) > 1:
                print(f'Found multiple raw files for {recording_name}: {x}')
            case _:
                print(f'Found single raw file for {recording_name}: {raw_files}')

        # loop over probes
        for probe_num, raw_file in enumerate(raw_files):
            print(f'---processing probe {probe_num} from file: {raw_file.name}')

            ## get sync times
            ping_samples, ping_times = get_recording_sync(
                raw_file,
                rec_folder,
                probe_num,
                overwrite=overwrite,
                threshold=None,
                verbose=True,
                sync_job_kwargs=dict(n_jobs=8, chunk_duration='10s', progress_bar=True)
            )
            if ping_samples is None: # type: ignore
                print(f'(!) No ping samples found in existing npy files for probe {probe_num}\nSkipping...\n\n')
                continue

    print('\nFinished processing all recordings.'.upper())

if __name__ == "__main__":
    from spikeinterface import __version__ as si_vers
    print(f'spikeinterface version:  {si_vers}')

    # % setup
    # load config settings
    paths = settings.paths
    experiment = settings.experiment

    # define project paths
    raw_drive = paths.drive
    experiment_name = experiment.dir
    batch_folder = raw_drive / experiment_name / paths.data_dir
    metadata_folder = raw_drive / experiment_name / paths.meta_dir
    datasets_folder = raw_drive / experiment_name / paths.dataset_dir
    print(f'Looking for recordings in:\n\t{batch_folder}')

    # define session paths
    raw_dir = paths.raw_dir
    alignment_dir = paths.alignment_dir
    processed_dir = paths.processed_dir
    output_dir = paths.output_dir

    # set recording sessions to process
    recording_sessions = experiment.recordings
    print("Processing the following recordings:")
    pprint(recording_sessions, indent=4)

    # % parameters
    overwrite = False
    get_all_sync()