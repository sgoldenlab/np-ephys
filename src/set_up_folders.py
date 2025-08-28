"""set_up_folders.py
Sets up standardized template folder structures for organizing histology data and/or
recording session data for animal subjects. It creates a '0_histology' directory and/or
a session-named directory with predefined subdirectories and placeholder files to
facilitate consistent data organization and downstream processing.
Usage:
    python set_up_folders.py [--histology] [--session SESSION_NAME] [--path START_PATH]
Arguments:
    --histology
        Create only the histology folder structure ('0_histology') in the specified path.
    --session SESSION_NAME
        Create only the recording session folder structure with the given name.
    --path START_PATH
        Base directory to create folders in (default: current directory).
Examples:
    # Create both histology and a default session folder in the current directory
    python set_up_folders.py
    # Create only the histology folder structure in the current directory
    python set_up_folders.py --histology
    # Create only a recording session folder named NP09_R1 in the current directory
    python set_up_folders.py --session NP09_R1
    # Create both structures in a specific path
    python set_up_folders.py --path /path/to/parent
    # Create only a session folder in a specific path
    python set_up_folders.py --session NP09_R1 --path /path/to/parent
The resulting folder structures include:
    - 0_histology/ with subfolders and placeholder files for histology data
    - <SESSION_NAME>/ with subfolders and placeholder files for a recording session
This script is intended to be run from the command line.
"""


from pathlib import Path
import argparse


def create_histology_structure(base_path: Path, debug: bool = False):
    """
    Generates or previews the full folder structure for the '0_histology' subfolder.
    """
    base_folder = base_path / "0_histology"

    if debug:
        print(f"DEBUG: Histology folder structure would be created under '{base_path}'")
        print(f"{base_folder.parent.name}/")
        print(f"└── {base_folder.name}/")
        print("    ├── 0_unregistered_downsampled/")
        print("    ├── 1_registered_napari/")
        print("    ├── 2_transformed_stacks/")
        print("    └── 3_lasagna_tracks/")
        return

    print(f"Creating full folder structure for: {base_folder}")

    # Define the structure as a list of directories to create
    structure = [
        base_folder / "0_unregistered_downsampled",
        base_folder / "1_registered_napari",
        base_folder / "2_transformed_stacks",
        base_folder / "3_lasagna_tracks",
    ]

    for dir_path in structure:
        dir_path.mkdir(parents=True, exist_ok=True)

    print(f"Folder structure created successfully under '{base_path}'")
    print(f"{base_folder.name}/")
    print("├── 0_unregistered_downsampled/")
    print("├── 1_registered_napari/")
    print("├── 2_transformed_stacks/")
    print("└── 3_lasagna_tracks/")
    print("\nYou can find the new folders in:", base_folder)


def create_recording_session_structure(
    session_folder_name, base_path: Path, include_top_level=True, debug: bool = False
):
    """
    Generates or previews a template 'Recording session' subfolder structure.
    """
    if not session_folder_name:
        print("Error: Recording session name cannot be empty.")
        print("Usage: python create_recording_session_full.py <RecordingSessionName>")
        print("Example: python create_recording_session_full.py NP09_R1")
        return

    base = base_path / session_folder_name if include_top_level else base_path

    if debug:
        print(f"DEBUG: Recording session folder structure would be created under '{base}'")
        prefix = "    "
        print(f"{base.parent.name}/")
        if include_top_level:
            print(f"└── {session_folder_name}/")
        else:
            prefix = "└── "
        print(prefix + "├── 0_raw_compressed/")
        print(prefix + "├── 1_histology_alignment/")
        print(prefix + "├── 2_processed/")
        print(prefix + "│   ├── metrics/")
        print(prefix + "│   └── aligned_outputs/")
        print(prefix + "└── 3_datasets/")
        print(prefix + "    ├── sync_data/")
        print(prefix + "    ├── metadata/")
        print(prefix + "    └── plots/")
        return

    print(
        f"Creating folder structure for recording session: {session_folder_name}"
        + ("" if include_top_level else " (no top-level folder)")
    )

    # Only directories, no files
    structure = [
        base / "0_raw_compressed",
        base / "1_histology_alignment",
        base / "2_processed",
        base / "2_processed" / "metrics",
        base / "2_processed" / "aligned_outputs",
        base / "3_datasets",
        base / "3_datasets" / "sync_data",
        base / "3_datasets" / "metadata",
        base / "3_datasets" / "plots",
    ]

    for dir_path in structure:
        dir_path.mkdir(parents=True, exist_ok=True)

    print("Folder structure created successfully for",
          session_folder_name + ":")
    if include_top_level:
        print(f"{session_folder_name}/")
        prefix = ""
    else:
        prefix = ""
    print(prefix + "├── 0_raw_compressed/")
    print(prefix + "├── 1_histology_alignment/")
    print(prefix + "├── 2_processed/")
    print(prefix + "│   ├── kilosort4/")
    print(prefix + "│   ├── metrics/")
    print(prefix + "│   └── aligned_outputs/")
    print(prefix + "└── 3_datasets/")
    print(prefix + "    ├── sync_data/")
    print(prefix + "    ├── metadata/")
    print(prefix + "    └── plots/")
    if include_top_level:
        print("\nYou can find the new session folder in:", base)
    else:
        print("\nYou can find the new folders in the current directory.")

def setup_folders_from_dict(recording_pairs: dict, base_path: Path, debug: bool = False):
    """
    Sets up folder structures for all recordings specified in a dictionary.

    For each session name (key) in the recording_pairs dictionary, this function
    creates both a histology folder and a recording session folder under the
    given base_path.

    Args:
        recording_pairs (dict): A dictionary where keys are session names.
        base_path (Path): The base directory where folders will be created.
        debug (bool, optional): If True, prints what would be created without
                                actually creating any folders. Defaults to False.
    """
    if not isinstance(base_path, Path):
        base_path = Path(base_path)

    print(f"Setting up folder structures under: {base_path}")
    if debug:
        print(f"--- Debug mode: No files or folders will be created. ---\n")

    for session_name in recording_pairs.keys():
        print(f"--- Processing session: {session_name} ---")
        # The project folder for the subject is one level up from the session folder
        project_folder = base_path / session_name.split('_')[0]
        
        create_histology_structure(project_folder, debug=debug)
        print()
        create_recording_session_structure(
            session_name, project_folder, include_top_level=True, debug=debug
        )
        print("-" * (25 + len(session_name)) + "\n")

def main():
    """
    Main function to parse arguments and create folder structures.
    """
    parser = argparse.ArgumentParser(
        description="Set up histology and/or recording session folder structures.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--histology", action="store_true",
        help="Create only the histology folder structure."
    )
    parser.add_argument(
        "--session", metavar="SESSION_NAME", type=str, nargs="?",
        help="Create only the recording session folder structure with the given name."
    )
    parser.add_argument(
        "--path", metavar="START_PATH", type=str, default=".",
        help="Base directory to create folders in (default: current directory)."
    )
    parser.add_argument(
        "--no-top-level", action="store_true",
        help="Do not create a top-level session folder; create subfolders in the current directory."
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Print out the final structure without creating folders."
    )

    args = parser.parse_args()

    base_path = Path(args.path).resolve()

    if args.debug:
        print(f"--- Debug mode: No files or folders will be created. ---\n")

    # Logic for which functions to call
    if args.histology and args.session:
        create_histology_structure(base_path, debug=args.debug)
        print() 
        create_recording_session_structure(
            args.session, base_path, include_top_level=not args.no_top_level, debug=args.debug
        )
    elif args.histology:
        create_histology_structure(base_path, debug=args.debug)
    elif args.session:
        create_recording_session_structure(
            args.session, base_path, include_top_level=not args.no_top_level, debug=args.debug
        )
    else:
        # Default: do both in current or specified directory
        create_histology_structure(base_path, debug=args.debug)
        print()
        #  Use a default session name if not provided
        default_session_name = "RecordingSession"
        create_recording_session_structure(
            default_session_name, base_path, include_top_level=not args.no_top_level, debug=args.debug
        )

if __name__ == "__main__":
    main()