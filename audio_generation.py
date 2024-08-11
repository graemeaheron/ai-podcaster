import time
from pydub import AudioSegment
import os

def split_text(text, max_char_length=4096):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 > max_char_length:
            chunks.append(current_chunk)
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def convert_seconds_to_minutes_and_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return minutes, remaining_seconds


def convert_text_to_audio_files(
    text,
    openai_client,
    output_directory_path,
    concatenated_output_filename
):
    text_chunks = split_text(text)
    
    print(f"Text chunks: {len(text_chunks)}")

    audio_filepaths_in_sequential_order = []

    for index in range(0, len(text_chunks)):
        output_filename = f"{index}.mp3"
        output_filepath = os.path.join(output_directory_path, output_filename)
        audio_filepaths_in_sequential_order.append(output_filepath)

        request_start_time = time.time()
        print("\nInitiating text to speech request")

        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="fable",
            input=text_chunks[index]
        )
        
        request_end_time = time.time()
        print(f"Request complete ({(request_end_time - request_start_time):.2f} seconds)")

        response.stream_to_file(output_filepath)
    
    combined = AudioSegment.empty()

    for filepath in audio_filepaths_in_sequential_order:
        audio = AudioSegment.from_mp3(filepath)
        combined += audio
    
    combined_output_filename = f"{concatenated_output_filename}.mp3"
    combined_output_filepath = os.path.join(output_directory_path, combined_output_filename)

    combined.export(combined_output_filepath, format="mp3")
    print(f"\nAudio file saved as {combined_output_filename}")

    duration_ms = len(combined)
    duration_s = duration_ms / 1000
    minutes, seconds = convert_seconds_to_minutes_and_seconds(duration_s)
    print(f"Audio length: {minutes} mins, {int(seconds)} secs")
