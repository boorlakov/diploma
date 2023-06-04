import json
import os
import random
from typing import Union
from datasets import Dataset
from tqdm import tqdm


def identify_game(dir: str) -> Union[str, None]:
    """
    Identify the game based on the directory name.

    Parameters
    ----------
    dir : `str`
        The directory name.

    Returns
    ----------
    `Union[str, None]`
        The game identifier.
    """
    game_identifiers = ["pst", "id1", "bg1", "bg2"]

    for game in game_identifiers:
        if game in dir:
            return game

    return None


def load_dialogues_from_file(path: str, limit: Union[int, None] = None) -> list:
    """
    Load dialogues from a file.

    Parameters
    ----------
    path : `str`
        The path of the file.
    limit : `Union[int, None]`, default=None
        The maximum number of dialogues to load.

    Returns
    ----------
    content:
        The list of dialogues.
    """

    with open(path) as file:
        content = json.load(file)
    if limit:
        content = random.sample(content, limit)
    return content


def collect_and_prepare_dialogue_data(data_directory: str, limit: Union[int, None]) -> Dataset:
    """
    Collects and prepares dialogue data from multiple files within a directory.
    The collected data is converted into a Hugging Face Dataset object.

    Parameters
    ----------
    data_directory : `str`
        The base directory containing the files to read data from.
    limit : `Union[int, None]`
        The maximum number of dialogues to load, or None for no limit.

    Returns
    ----------
    `Dataset`
        A Hugging Face Dataset object containing the collected dialogue data.
    """

    dialogue_data = []
    for directory in os.listdir(data_directory):
        files = os.listdir(os.path.join(data_directory, directory))
        game = identify_game(directory)
        for filename in tqdm(files, f"Processing files in {directory}"):
            dialogues = load_dialogues_from_file(
                os.path.join(data_directory, directory, filename), limit
            )
            for dialogue in dialogues:
                dialogue["filename"] = filename
                dialogue["game"] = game
                dialogue_data.append(dialogue)

    dnd_dataset = Dataset.from_list(dialogue_data)
    dnd_dataset = dnd_dataset.rename_columns(
        {"HeroSpeech": "player_turns", "CharacterSpeech": "npc_turns"}
    )
    dnd_dataset = dnd_dataset.remove_columns("Id")
    return dnd_dataset
