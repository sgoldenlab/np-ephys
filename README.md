# Neuropixels electrophysiology processing

Collection of scripts used in the Golden Lab to process electrophysiological recordings, from spike sorting to postprocessing and unit curation.


## Getting Started

### Prerequisites & Dependencies

#### Prerequisites
This project uses `uv` as its package manager and virtual environment manager. Please ensure you have `uv` installed. You can find installation instructions [here](https://github.com/astral-sh/uv).

#### Dependencies
The main dependencies with specific version requirements are:
- **SpikeInterface**: `>=0.102.3`
- **Kilosort**: `v4.0.22`
- **PyTorch/Torch**: The project is configured to use a nightly build of PyTorch with CUDA 12.9 support. Adjust as needed!
- **mtscomp**: `>=1.0.2` for compressing recordings.

### Setup
To set up the environment and install all required dependencies, navigate to the project root and run:
```bash
uv sync
```
This command will create a virtual environment (if one doesn't exist) and install all packages specified in the `pyproject.toml` file. A `requirements.txt` file is also included.

## Usage
This repository ***currently*** provides tools for two main purposes: compressing raw ephys data collected with Neuropixels probes, and setting up standardized folder structures for new experiments. The `experiment_setup.ipynb` notebook is provided to guide you through these processes.

### Compressing Raw Recordings
Raw ephys data can be compressed into a more manageable format using the `mtscomp` package. This process is handled entirely within the `experiment_setup.ipynb` notebook.

#### Configuration
Before running the compression, you need to configure your settings:
1.  **`config/run_config.toml`**: This is the main file for run-specific parameters.
    -   `[experiment.dir]`: Set the name of the top-level experiment folder.
    -   `[experiment.recordings]`: Define the recordings to be processed.
2.  **`config/default_config.toml`**: Contains default paths for data structure. If using the folder structure template, these can typically be left as is.
3.  **(Not included) `config/.env`**: For local overrides. For example, you can override the main data drive path by setting `PIPELINE_PATHS__DRIVE="/path/to/your/data"`.

Once configured, the notebook will guide you through compressing a single recording or batch-compressing all defined recordings.

### Setting Up Folder Structures
To ensure consistent data organization, we create standardized folder structures for new recording sessions that have designated locations for both electrophysiological and histological data processing. This can be done in two ways:

1.  **Command-Line Tool**
    You can type `set_up_folders` to use the script directly from the terminal. This is useful for setting up a single session or for more granular control.
    ```bash
    uv run set_up_folders --session MYSESSION_R1 --path /path/to/project
    ```
    Run `uv run set_up_folders --help` for more details on the available arguments.

2.  **Jupyter Notebook (`experiment_setup.ipynb`)**
    The notebook also provides a way to programmatically create folder structures for all recordings listed in your `run_config.toml`. This is ideal for setting up a new project with multiple sessions at once.

## Authors

*   **Kevin N. Schneider**
    *   GitHub: [@kevsch88](https://github.com/kevsch88)
    *   Email: kevsch88@gmail.com