"""
This script processes a dataset of Dungeons & Dragons (D&D) dialogues.

Example:
    $ python prepare.py --subsets all --generate_descriptions --description_file descriptions.csv --limit_dialogues 25
"""
from datetime import datetime
import random
import requests
from transformers import LlamaTokenizer, AutoTokenizer

from dialogue_data import (
    collect_and_prepare_dialogue_data,
)
from descriptions import (
    generate_descriptions,
    build_dataset,
    generate_file_paths,
    save_dataset_subsets,
    add_descriptions_to_dataset,
)
from arg_parser import create_arg_parser


def main(args):
    data_directory = "DNDD_ver0.5"
    execution_timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M%S")
    dnd_dataset = collect_and_prepare_dialogue_data(data_directory, args.limit_dialogues)

    if args.generate_descriptions:
        generate_descriptions(dnd_dataset, tokenizer, execution_timestamp, args.model_server_url)

    if args.description_file:
        dnd_dataset = add_descriptions_to_dataset(dnd_dataset, args.description_file)

    if args.build_final:
        t5_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-xl")
        final_dataset = build_dataset(dnd_dataset.to_pandas(), t5_tokenizer)
        save_filepath = f"dndd-max_d{args.limit_dialogues}-{execution_timestamp}.parquet"
        final_dataset.to_parquet(save_filepath)
        print(f"Saved to {save_filepath}")

    subset_map = generate_file_paths(execution_timestamp, args.limit_dialogues)
    save_dataset_subsets(dnd_dataset, args.subsets, subset_map)


if __name__ == "__main__":
    random.seed(42)
    parser = create_arg_parser()
    args = parser.parse_args()

    if isinstance(args.subsets, str):
        subsets = [args.subsets]
        args.subsets = subsets

    if args.generate_descriptions:
        tokenizer = LlamaTokenizer.from_pretrained(args.llama_base_model)
        try:
            status_code = requests.get(args.model_server_url).status_code
            if status_code != 200:
                raise Exception(f"Model server returned status code {status_code}")
        except requests.exceptions.RequestException as ex:
            print(f"Could not connect to the model server: {ex}")
            raise ex

    main(args)
