# %% Imports
import os
from mtscomp import compress
from pathlib import Path

from spikeinterface.extractors import read_spikeglx
from shutil import copyfile
from pprint import pprint

# # %% setup
# set default parallel processing parameters
num_cores = os.cpu_count()
job_kwargs=dict(
    n_threads=round(num_cores*0.8),
    chunk_duration=5,
)
print("\nParallel Job parameters:")
pprint(job_kwargs, indent=4)

def compress_recording(recording_name: str, rec_folder: Path | list | str, target_folder: Path, job_kwargs=job_kwargs):
    if isinstance(rec_folder, str):
        rec_folder = Path(rec_folder)
    elif isinstance(rec_folder, list):
        rec_folder = Path(rec_folder[0])  # take the first folder in the list
    
    recording_name = rec_folder.name
    raw_list = list(rec_folder.glob('*imec*'))  # length > 1 multiple probes
    for probe_num, _ in enumerate(raw_list):
        raw_folder = next(rec_folder.glob(f'*imec{probe_num}*'))

        rec = read_spikeglx(raw_folder, load_sync_channel=True, stream_id=f'imec{probe_num}.ap')
        raw_file = next(raw_folder.glob(f'*imec{probe_num}*ap.bin'))
        meta_file = next(raw_folder.glob(f'*imec{probe_num}*ap.meta'))

        target_cbin = target_folder / f'{raw_file.with_suffix(".cbin").name}'
        target_cmeta = target_folder / f'{raw_file.with_suffix(".ch").name}'
        target_meta = target_folder / f'{meta_file.name}'
        print(target_cbin, target_cmeta, target_meta, sep='\n')

        # # get ephys metadata
        fs = rec.get_sampling_frequency()
        n_channels = rec.get_num_channels()
        dtype = rec.get_dtype()

        # compress bin file to '.cbin' and corresponding cmeta '.ch' json file
        print(f'\ncompressing {raw_file.name} to {target_folder / f"{recording_name}.cbin"}')
        _ = compress(
            raw_file,
            out=target_cbin,
            outmeta=target_cmeta,
            sample_rate=fs,
            n_channels=n_channels,
            dtype=dtype,
            **job_kwargs
        )
        print('...compression done.')
        copyfile(meta_file, target_meta)  # copy the spikeglx meta file
        print(f'...copied {meta_file.name} to {target_meta.name}.')
        print(f'---finished processing {recording_name}---\n')

def compress_recordings(recording_pairs, batch_folder, target_folder: Path, project_base_path: Path | None=None, job_kwargs=job_kwargs):
    for session, properties in recording_pairs.items():
        animal = session.split('_')[0]
        recording_name = session
        concatenate = properties['concatenate']
        print(f'---processing  {recording_name}{", multiple recordings..." if concatenate else ""}')

        if not concatenate:
            try:
                rec_folder = next(batch_folder.glob(f"{recording_name}_g*"))
            except StopIteration:
                print(f'No recordings found for {recording_name}!\nSkipping...\n\n')
                continue
        else:
            rec_names = [f.name for f in batch_folder.glob(f"{recording_name}_g*")]
            rec_folders = [f for f in batch_folder.glob(f'{recording_name}*_g*')]
            print(*rec_folders, sep='\n')

        print(f'recording top folder:  {rec_folder}')

        if not concatenate:
            rec_folders = [rec_folder]
            rec_name = rec_folder.name

        if project_base_path is not None:
            target_folder = (project_base_path / animal / recording_name / target_folder).resolve()
        assert target_folder.exists(), f"Target folder does not exist: {target_folder}"
        
        for rec_folder in rec_folders:
            compress_recording(rec_name, rec_folder, target_folder, job_kwargs)

    print('\nAll recordings processed successfully.')
