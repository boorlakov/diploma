import argparse


def create_arg_parser():
    parser = argparse.ArgumentParser(
        description="Process subsets of DNDD (Dungeon & Dragons Dialogues) dataset"
    )
    parser.add_argument(
        "--subsets",
        nargs="+",
        required=False,
        default="all",
        help="Subsets of the dataset to process (bg1, bg2, id1, pst, all). DEFAULT: all",
    )
    parser.add_argument(
        "--generate_descriptions",
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Generates a description to NPCs using Alpaca-LoRA-13B in format Name/Alignment/Description/Flaw/Motivation/Personality",  # noqa: E501
    )
    parser.add_argument(
        "--description_file",
        required=False,
        default=False,
        help="Adds NPCs' description to dataset in format Name/Alignment/Description/Flaw/Motivation/Personality",
    )
    parser.add_argument(
        "--limit_dialogues",
        required=False,
        default=None,
        type=int,
        help="Limits the number of dialogues that NPC can have.",
    )
    parser.add_argument(
        "--llama_base_model",
        default="decapoda-research/llama-13b-hf",
        help="The name of the base model to use.",
    )
    parser.add_argument(
        "--model_server_url",
        default="http://127.0.0.1:7860",
        help="The URL of the model server.",
    )
    parser.add_argument(
        "--generate_descriptions", action="store_true", help="Whether to generate descriptions."
    )
    parser.add_argument(
        "--build-final",
        action="store_false",
        help="Builds the final training dataset.",
    )

    return parser
