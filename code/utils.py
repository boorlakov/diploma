import re
from typing import List, Tuple
import pandas as pd
from transformers import PreTrainedTokenizer


def format_dialogue_history(dialogue_history: List[str], game_type: str) -> str:
    """
    Formats the dialogue history into a readable format.

    Parameters
    ----------
    dialogue_history : `List[str]`
        A list containing the dialogue history. Each item is a dialogue string.
    game_type : `str`
        A string representing the type of the game. If 'pst', special formatting is applied.

    Returns
    ----------
    `str`
        The formatted dialogue history. Each turn is on a new line with the format 'Speaker: Dialogue turn'.
    """
    formatted_history = ""
    for turn_index in range(len(dialogue_history)):
        speaker = "Player" if turn_index % 2 == 0 else "NPC"
        dialogue_turn = dialogue_history[turn_index]
        if game_type == "pst" and dialogue_turn != "START DIALOGUE":
            dialogue_turn = dialogue_turn.replace("\\r", "").replace("\\n", "")
            extracted_text = re.findall('"([^"]*)"', dialogue_turn)
            extracted_text = " ".join(extracted_text) if extracted_text else default_text(speaker)
            formatted_history += f"{speaker}: {extracted_text}\n"
        else:
            formatted_history += f"{speaker}: {dialogue_turn}\n"
    return formatted_history


def format_prompt(npc_data: pd.Series, current_history: str, query: str) -> str:
    npc_prompt = f"""Below is the definition of in-game NPC.
NPC Name: {npc_data['name']}
Alignment: {npc_data['alignment']}
Description: {npc_data['description']}
Personality traits: {npc_data['personality']}
Flaws: {npc_data['flaw']}
Motivation: {npc_data['motivation']}

Dialogue history:
{current_history}
Player query: {query}

Respond to player's query based on defined NPC: """
    return npc_prompt


def tokenize_check_overflow(
    tokenizer: PreTrainedTokenizer,
    npc_prompt: str,
    current_history: str,
    dialogue_history: List[str],
    game: str,
) -> Tuple[str, List[str]]:
    """
    Truncates the dialogue history to avoid tokenization overflow.

    Parameters
    ----------
    tokenizer : `PreTrainedTokenizer`
        The tokenizer object used for tokenization.
    npc_prompt : `str`
        The NPC prompt or instruction text.
    current_history : `str`
        The current dialogue history.
    dialogue_history : `List[str]` 
        The list of previous dialogue turns.
    game : `str`
        The game identifier.

    Returns
    ----------
    `Tuple[str, List[str]]`
        A tuple containing the updated current history and dialogue history.
    """

    prompt_tokens = tokenizer.tokenize(npc_prompt)
    history_tokens = tokenizer.tokenize(current_history)
    total_tokens = len(prompt_tokens) + len(history_tokens)
    while total_tokens > 1024:
        dialogue_history = dialogue_history[2:]
        current_history = format_dialogue_history(dialogue_history, game)
        history_tokens = tokenizer.tokenize(current_history)
        total_tokens = len(prompt_tokens) + len(history_tokens)

    return current_history, dialogue_history


def extract_text(dialogue, default_text):
    extracted_text = re.findall('"([^"]*)"', dialogue)
    return " ".join(extracted_text) if extracted_text else default_text


def default_text(speaker):
    return "Ignore." if speaker == "Player" else "That NPC seems to be ignoring you."
