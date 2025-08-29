from spikeinterface.extractors import read_cbin_ibl, read_spikeglx
from spikeinterface.core import load_extractor, load_waveforms
from dynaconf import Dynaconf

import os
import shutil
from pathlib import Path, PurePath

from misc_funcs import dated, print_date
from re import sub as regexsub


# %% general file / folder
def get_relative_path(originpath, rel_to):
    "may not work depending on pathlib version"
    assert isinstance(originpath, Path)
    assert isinstance(rel_to, Path)
    return originpath.relative_to(rel_to, walk_up=True)


def make_dir(folder_path: Path, overwrite=False, debug=False):
    if folder_path.is_dir():
        match overwrite:
            case False:
                print('...folder path already exists.')
                return None
            case True:
                print('...folder path exists, removing and replacing.')
                remove_dir(folder_path)
    print(f'...making new dir at {folder_path}')
    os.mkdir(folder_path)


def remove_dir(folder_path, debug=False):
    try:
        shutil.rmtree(folder_path)
    except PermissionError as err:
        # chmod(folder_path, S_IWOTH)
        shutil.rmtree(folder_path)
    finally:
        print(f'...deleted {folder_path}')


def remove_recording(rec, rec_folder: Path,
                     debug=False
                     ):
    """To remove recording, typically once done with local copy of processed rec.
    NOTE: clean wf and new sorting objects should be linked to recording in drive
    before deleting local one. See: load and register
    """
    del rec
    remove_dir(rec_folder)


# %% spikeinterface file/folder management


# %% getting information
def get_recs_with_raw(batch_folder, animal, debug=False):
    "Look in animal folder for rec folders. Default path would be {batch_folder}/{animal}/{Rec1_g0}"
    assert batch_folder.is_dir(
    ), f'---{batch_folder} was not found to be a directory'
    assert (animal_folder := (batch_folder / animal)
            ).is_dir(), f'---{animal_folder} was not found to be a directory'

    rec_folders = [Path(d) for d in list(animal_folder.glob('*_g0'))]
    print('Recording folders:')
    # print(*(d for d in rec_folders), sep='\n')
    # print('\n')

    raw_folders = list()
    for d in rec_folders:
        if not (raw_fold := (d / f'{d.name}_imec0')).is_dir():
            # f = 'no "_imec0" subfolder'
            continue
        # if any(['ap.bin' in f for f in os.listdir(d)] +
        #         ['lf.bin' in f for f in os.listdir(d)] +
        #         ['ap.cbin' in f for f in os.listdir(d)]):
        #     rec_folders.append(d)
        if any([raw_fold.glob('*ap.bin') != [], raw_fold.glob('*ap.cbin') != []]):
            print(f'{d} ... raw bin file found.')
            raw_folders.append(raw_fold)
    return raw_folders


def get_recs(batch_folder, anim_folder: Path, recs: list = [], debug=False):
    assert batch_folder.is_dir(
    ), f'---{batch_folder} was not found to be a directory'
    assert anim_folder.is_dir(
    ), f'---{anim_folder} was not found within {batch_folder}'
    assert list(anim_folder.glob('*R*')
                ) != [], f'---no rec folders found in {anim_folder}'
    assert recs != [], f'---list passed to param `recs` is empty.'
    # find recs with numbers listed in recs within animal folder
    #   f string separates possible numbers with "|" to yield OR regex statement
    recs = list(anim_folder.glob(f'*R[{"|".join(str(x) for x in recs)}]*'))
    recs = [r for r in recs if r.is_dir()]
    if recs != []:
        return recs
    else:
        return None


def get_rec_info(rec_folder: Path, full=False):
    """if full, returns recname, animal, recnum, otherwise just recname"""
    rec_name = regexsub(r'_g.*$', '', rec_folder.name)
    animal, recnum = rec_name.split('_')
    if full:
        return rec_name, animal, recnum
    else:
        return rec_name


def get_folder_info(rec_folder: Path):
    "returns rec_name and base_folder"
    rec_name, animal, recnum = get_rec_info(rec_folder, full=True)

    base_folder = rec_folder
    raw_fold = find_raw_fold(rec_folder)
    print(f'\nbase folder: {base_folder}\n',
          f'raw folder: {raw_fold}\n',
          f'rec name: {rec_name}')
    return rec_name, base_folder  # , animal, recnum


def get_single_rec(batch_folder, animal, recnum):
    assert batch_folder.is_dir(
    ), f'---{batch_folder} was not found to be a directory'
    assert (animal_folder := (batch_folder /
            f'{animal}')).is_dir(), f'---{animal_folder} was not found to be a directory'
    assert list(animal_folder.glob(
        f'*R{recnum}*')) != [], f'---R{recnum} was not found for {animal}'
    return list(animal_folder.glob(f'*R{recnum}*'))[0]


def find_raw_fold(rec_folder):
    raw_fold = rec_folder / f'{rec_folder.name}_imec0'  # old format
    if not raw_fold.is_dir():
        raw_fold = next(rec_folder.rglob('*imec0*')).parent
    assert raw_fold.is_dir(), f'---no raw folder found in {rec_folder}'
    assert any([raw_fold.glob('*ap.bin') != [],
               raw_fold.glob('*ap.cbin') != []])
    return raw_fold


# %% loading


def check_rec(base_folder, label='preprocessed', debug=False):
    "checks if labeled folder exists to load recording folder"
    # assert (check_test := base_folder / label).is_dir(), f'{label} is not a folder in {base_folder}'
    check_test = (base_folder / label).is_dir()
    # check_text = "exists" if check_test else "doesn't exist"
    if debug:
        if check_test:
            print(f'\nFound "{label}" folder under "{base_folder.name}"...')
        else:
            print(
                f'\nDid not find "{label}" folder under "{base_folder.name}"...')
        return check_test
    else:
        return load_extractor(base_folder / label, base_folder=base_folder)


def load_raw(rec_folder, type='cbin', stream='imec0.ap', sync=False):
    "load raw recording, set cbin or ap.bin depending on file format"
    assert rec_folder.is_dir(
    ), f'---{rec_folder} was not found to be a directory'
    raw_fold = rec_folder / f'{rec_folder.name}_imec0'
    match type:
        case 'cbin':
            try:
                raw_rec = read_cbin_ibl(raw_fold, load_sync_channel=sync)
                return raw_rec
            except:
                print(f'problems loading cbin file in {raw_fold}...\n')
                return None
        case _:  # stream_id could also be imec0.lf for lfp data or None for both
            raw_rec = read_spikeglx(
                raw_fold, stream_id=stream, load_sync_channel=sync)
            return raw_rec
