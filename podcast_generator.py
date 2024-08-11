from text_generation import convert_text_to_narrative_history
from audio_generation import convert_text_to_audio_files
from utils import compute_word_count, estimate_podcast_minutes_length
from dotenv import load_dotenv
from openai import OpenAI
import os
import glob
import time
import argparse

script_start_time = time.time()

OPENAI_LLM_MODEL = "gpt-4o"
OUTPUT_NOTES_DIRECTORY = "./data/outputs/text/narrative_histories"
OUTPUT_AUDIO_DIRECTORY = "./data/outputs/audio/narrative_histories"

argparser = argparse.ArgumentParser()
argparser.add_argument("input_filepath", type=str, help="Filepath to read input text from")
argparser.add_argument("--skip-steps", nargs="+", help="Steps to skip", choices=[
    "text-generation",
    "audio-generation"
])

args = argparser.parse_args()

input_filepath = args.input_filepath
skip_steps = args.skip_steps if args.skip_steps else []

with open(input_filepath, 'r', encoding='utf-8') as file:
    input_text = file.read()

input_filename = os.path.basename(input_filepath)
topic = input_filename.removesuffix(".txt")

input_word_count = compute_word_count(input_text)
input_audio_length_minutes = estimate_podcast_minutes_length(input_text)

print(f"\nTopic: {topic}")
print(f"Input word count: {input_word_count}")

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)

narrative_history_text_output_filename = f"{topic}.txt"
narrative_history_tect_output_path = os.path.join(OUTPUT_NOTES_DIRECTORY, narrative_history_text_output_filename)


if "text-generation" not in skip_steps:
    print(f"Estimated podcast minutes length: {input_audio_length_minutes:.2f}")

    desired_podcast_length_minutes = input("How many minutes would you like your podcast to approximately be? ")

    try:
        desired_podcast_length_minutes = float(desired_podcast_length_minutes)
    except:
        raise Exception("You must enter a number!")

    target_word_length = input_word_count * desired_podcast_length_minutes / input_audio_length_minutes

    print("\nGenerating text")
    step_start_time = time.time()

    # Assuming 1500 output per LLM call
    desired_chunks = target_word_length / 1_500
    chunk_size = input_word_count / desired_chunks

    narrative_history_text = convert_text_to_narrative_history(
        topic,
        input_text,
        chunk_size,
        openai_client,
        OPENAI_LLM_MODEL
    )

    step_end_time = time.time()
    print(f"\nText generation complete ({int(step_end_time - step_start_time)} seconds)")
    print(f"Narrative history output word count: {compute_word_count(narrative_history_text)}")
    print(f"Estimated audio minutes length: {estimate_podcast_minutes_length(narrative_history_text):1f}")

    with open(narrative_history_tect_output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(narrative_history_text)
else:
    with open(narrative_history_tect_output_path, 'r') as file:
        narrative_history_text = file.read()



if "audio-generation" not in skip_steps:
    print("\nGenerating audio")
    step_start_time = time.time()

    audio_output_directory = os.path.join(OUTPUT_AUDIO_DIRECTORY, topic)

    if not os.path.exists(audio_output_directory):
        os.makedirs(audio_output_directory)

    existing_files_in_output_directory = glob.glob(os.path.join(audio_output_directory, '*'))
    for file in existing_files_in_output_directory:
        os.remove(file)

    convert_text_to_audio_files(
        narrative_history_text,
        openai_client,
        audio_output_directory,
        topic
    )

    step_end_time = time.time()
    print(f"\nAudio generation complete ({int(step_end_time - step_start_time)} seconds)")

script_end_time = time.time()
print(f"\nTotal run time: {int(script_end_time - script_start_time)} seconds")
