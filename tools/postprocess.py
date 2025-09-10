import warnings
from pathlib import Path

import spikeinterface.full as si

# Ignore specific warnings from SpikeInterface
warnings.filterwarnings("ignore", message="The `ipywidgets` package is not installed.")
warnings.filterwarnings("ignore", message="`sortingview` is not installed.")

def postprocess_session(session_folder: Path, paths_config, skip_existing: bool = True):
    """
    Postprocesses a single recording session by extracting waveforms and computing quality metrics.

    Args:
        session_folder (Path): The path to the session folder.
        paths_config: The 'paths' section of the project settings.
        skip_existing (bool, optional): If True, skip sessions that already have a
                                        postprocessed folder. Defaults to True.
    """
    session_name = session_folder.name
    print(f"--- Processing session: {session_name} ---")

    # Define paths for sorter output and postprocessing results
    sorter_output_folder = session_folder / paths_config.processed_dir / "kilosort4"
    postprocessed_folder = session_folder / paths_config.processed_dir / "postprocessed"

    # Check if the session should be skipped
    if skip_existing and postprocessed_folder.exists():
        print(f"Skipping {session_name}: Postprocessed folder already exists.\n")
        return

    if not sorter_output_folder.exists():
        print(f"Skipping {session_name}: Sorter output not found at {sorter_output_folder}.\n")
        return

    # Load the sorted data
    try:
        sorting = si.load_sorting_output(sorter_output_folder)
        print(f"Loaded sorting output from: {sorter_output_folder}")
    except Exception as e:
        print(f"Could not load sorting output for {session_name}. Error: {e}\n")
        return

    # Load the preprocessed recording
    try:
        rec_path = session_folder / paths_config.raw_dir
        rec = si.load_extractor(rec_path)
        print(f"Loaded recording from: {rec_path}")
    except Exception as e:
        print(f"Could not load recording for {session_name}. Error: {e}\n")
        return

    # Extract waveforms
    print("Extracting waveforms...")
    we = si.extract_waveforms(
        rec,
        sorting,
        folder=postprocessed_folder,
        overwrite=True,
        ms_before=1.0,
        ms_after=2.0,
        max_spikes_per_unit=500,
        n_jobs=-1,
        chunk_size=30000,
    )

    # Define and compute quality metrics
    metrics_list = [
        "amplitude_cutoff", "amplitude_median", "sliding_rp_violation",
        "presence_ratio", "snr", "isi_violation", "num_spikes",
        "peak_sign", "halfwidth", "peak_to_trough", "repolarization_slope",
        "recovery_slope",
    ]
    print("Computing quality metrics...")
    si.compute_quality_metrics(we, metric_names=metrics_list, load_if_exists=True)
    print("Done.")

    print(f"--- Finished processing {session_name} ---\n")
