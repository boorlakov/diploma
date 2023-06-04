import requests
from typing import Dict, Tuple, List
from tqdm import tqdm
from datasets import Dataset
from transformers import LlamaTokenizer, PreTrainedTokenizer
import pandas as pd


from utils import (
    format_dialogue_history,
    format_prompt,
    tokenize_check_overflow,
    extract_text,
    default_text,
)


def generate_descriptions(
    dnd_dataset: Dataset,
    tokenizer: LlamaTokenizer,
    execution_timestamp: str,
    model_server_url: str,
) -> None:
    """
    Generate descriptions for NPCs based on their dialogues in the given dataset.

    Parameters
    ----------
    dnd_dataset : `Dataset`
        The dataset containing NPC dialogues.
    tokenizer : `LlamaTokenizer`
        The tokenizer for text encoding.
    execution_timestamp : `str`
        The timestamp for execution.
    model_server_url : `str`
        The URL of the model server for generating descriptions.
    """

    grouped_by_filename: pd.DataFrame = (
        dnd_dataset.to_pandas().groupby("filename").agg(({"npc_turns": list, "player_turns": list}))
    )

    # Instruction text for the model
    instruction_text = "Create the personality of a single NPC in DnD style, based on the provided example dialogue in JSON format. Answer in format Name/Alignment/Description/Flaw/Motivation/Personality in a list format written in third person."  # noqa: E501
    header_text = '"NPC-turns": '

    instruction_len = len(tokenizer.tokenize(instruction_text))
    header_len = len(tokenizer.tokenize(header_text))

    for filename, dialogues in tqdm(grouped_by_filename["npc_turns"].items(), "Generating data"):
        dialogue_turns = process_dialogues(dialogues, tokenizer, instruction_len, header_len)

        input_text = header_text + str(dialogue_turns)
        response = make_prediction(
            model_server_url,
            instruction_text=instruction_text,
            input_text=input_text,
        )

        generated_description = response["data"][0]
        # Replacing newline characters with "þ" to avoid corrupting CSV file
        generated_description = generated_description.replace("\n", "þ")
        description_filename = f"descriptions-{execution_timestamp}.csv"
        with open(description_filename, mode="a", encoding="utf-8") as file:
            file.write(f"{filename},{generated_description}\n")


def make_prediction(
    model_server_url: str,
    instruction_text: str,
    input_text: str,
    temperature: float = 0.1,
    top_p: float = 0.2,
    top_k: int = 100,
    num_beams: int = 1,
    max_new_tokens: int = 512,
    streaming_opt: bool = False,
) -> dict:
    """
    Make a prediction using the API endpoint.

    Parameters
    ----------
    model_server_url : `str`
        The URL of the model server.
    instruction_text : `str`
        Instruction text to LLM.
    input_text : `str`
        Input text containing example NPC dialogues.
    temperature : `float`, default=0.1
        Sampling temperature.
    top_p : `float`, default=0.2
        Top p sampling value.
    top_k : `int`, default=100
        Top k sampling value.
    num_beams : `int`, default=1
        Number of beams for beam search.
    max_new_tokens : `int`, default=512
        Maximum number of new tokens for the output.
    streaming_opt : `bool`, default=False
        Option for streaming LLM output.

    Returns
    ----------
    dict
        The prediction response.
    """
    
    params = [
        instruction_text,
        input_text,
        temperature,
        top_p,
        top_k,
        num_beams,
        max_new_tokens,
        streaming_opt,
    ]

    response = requests.post(
        f"{model_server_url}/run/predict",
        json={"data": params},
    ).json()

    return response


def build_dataset(dndd_df: pd.DataFrame, tokenizer: PreTrainedTokenizer) -> Dataset:
    """
    Builds a training dataset from the provided DNDD dataset.

    Parameters
    ----------
    dndd_df : `pd.DataFrame`
        The DNDD dataset DataFrame.
    tokenizer : `PreTrainedTokenizer`
        The tokenizer used for tokenization.

    Returns
    ----------
    dict
        A dictionary containing the 'source' and 'target' lists representing the training dataset.
    """

    dataset_dict = {"source": [], "target": []}

    for npc_data in tqdm(dndd_df.itertuples(), "Processing dataset"):
        dialogue_history = []
        query = "START DIALOGUE"

        total_turns = len(npc_data.player_turns) + len(npc_data.npc_turns)
        for turn_index in range(total_turns):
            if turn_index % 2 == 0:
                target = npc_data.npc_turns[turn_index // 2]

                formatted_history = (
                    format_dialogue_history(dialogue_history, npc_data.game)
                    if dialogue_history
                    else "EMPTY"
                )
                npc_prompt = format_prompt(npc_data, formatted_history, query)
                formatted_history, dialogue_history = tokenize_check_overflow(
                    tokenizer,
                    npc_prompt,
                    formatted_history,
                    dialogue_history,
                    npc_data.game,
                )

                if npc_data.game == "pst":
                    if query != "START DIALOGUE":
                        query = extract_text(query, default_text("Player"))
                    target = extract_text(target, default_text("NPC"))

                npc_prompt = format_prompt(npc_data, formatted_history, query)
                dataset_dict["source"].append(npc_prompt)
                dataset_dict["target"].append(target)
            else:
                dialogue_history.append(query)
                dialogue_history.append(target)
                query = npc_data.player_turns[turn_index // 2]

    return Dataset.from_dict(dataset_dict)


def process_dialogues(
    dialogues: List[List[str]],
    tokenizer: LlamaTokenizer,
    instruction_len: int,
    header_len: int,
) -> List[str]:
    """
    Process dialogues by removing duplicates and ensuring the length of tokenized text is within limit.

    Parameters
    ----------
    dialogues : `List[List[str]]`
        List of dialogues, each dialogue is a list of turns.
    tokenizer : `LlamaTokenizer`
        Tokenizer to be used.
    instruction_len : `int`
        Length of instruction text.
    header_len : `int`
        Length of header text.

    Returns
    ----------
    `List[str]`
        Processed dialogue turns.
    """

    dialogue_turns: List[str] = []
    for dialogue in dialogues:
        for turn in dialogue:
            dialogue_turns.append(turn)
            # Removing any duplicate turns from the dialogue
            dialogue_turns = list(set(dialogue_turns))

            # Checking if the length of the tokenized dialogue_turns and instruction texts are within the limit
            prompt_len = len(tokenizer.tokenize(str(dialogue_turns))) + instruction_len + header_len
            if prompt_len > 500:
                print(prompt_len)
                dialogue_turns = dialogue_turns[:-1]
                break
        else:
            continue
        break
    return dialogue_turns


def generate_file_paths(
    execution_timestamp: str, limit_dialogues: int
) -> Dict[str, Tuple[str, str]]:
    """
    Generates file paths for subsets of a dataset based on the execution timestamp and limit of dialogues.

    Parameters
    ----------
    execution_timestamp : `str`
        The timestamp of the execution.
    limit_dialogues : `int`
        The maximum number of dialogues allowed in the subsets.

    Returns
    ----------
    `dict`
        A dictionary mapping subset names to their corresponding file paths.
    """
    
    file_prefix = "data/dndd_subset_"
    file_suffix = f"_{execution_timestamp}_max-d_{limit_dialogues}.parquet"
    subset_map = {
        "all": ("", f"{file_prefix}all{file_suffix}"),
        "bg1": ("bg1", f"{file_prefix}bg1{file_suffix}"),
        "bg2": ("bg2", f"{file_prefix}bg2{file_suffix}"),
        "id1": ("id1", f"{file_prefix}id1{file_suffix}"),
        "pst": ("pst", f"{file_prefix}pst{file_suffix}"),
    }
    return subset_map


def save_dataset_subsets(
    dnd_dataset: Dataset, subsets: List[str], subset_map: Dict[str, Tuple[str, str]]
) -> None:
    """
    Saves subsets of a dataset based on specified subsets and their corresponding paths.

    Parameters
    ----------
    dnd_dataset : `Dataset`
        The dataset to save subsets from.
    subsets : `List[str]`
        A list of subset names to save.
    subset_map : `Dict[str, Tuple[str, str]]`
        A dictionary mapping subset names to their corresponding paths.
    """

    for subset in subsets:
        subset_prefix, subset_file_path = subset_map[subset]
        subset_dndd = dnd_dataset.filter(lambda example: example["game"].startswith(subset_prefix))
        subset_dndd.to_parquet(subset_file_path)
        print(f"Saved to {subset_file_path}")


def add_descriptions_to_dataset(dnd_dataset: Dataset, description_file: str) -> Dataset:
    """
    Adds descriptions to a dataset by merging it with a description file.

    Parameters
    ----------
    dnd_dataset : `Dataset`
        The dataset to which descriptions will be added.
    description_file : `str`
        The path to the description file.

    Returns
    ----------
    `Dataset`
        The updated dataset with descriptions.
    """

    dndd_df = dnd_dataset.to_pandas()
    desc_df = pd.read_csv(description_file, sep="|")
    dndd_df_merged = pd.merge(dndd_df, desc_df, on="filename")
    dnd_dataset = Dataset.from_pandas(dndd_df_merged)
    return dnd_dataset
