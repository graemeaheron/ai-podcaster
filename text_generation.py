import time
from utils import compute_word_count


def split_text_into_chunks(text, chunk_size):
    chunk_size = int(chunk_size)
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def convert_text_to_narrative_history(
    topic,
    text,
    chunk_size,
    openai_client,
    model,
    temperature=0.7
):
    system_prompt = """
You are a narrative history writer. Your writing style is clear, detailed and comprehensive.
You will be provided with a detailed notes about history.
Produce a narrative history based on the notes.

You will only be provided with a subset of the complete notes. You only need to write about this subset. Your history will be combined
with histories of the other sections of the notes after you're finished. Therefore DO NOT start with an introduction, get straight
into your narrative history. That is so your history can fit with the others as easily as possible once you're finished.

You should detail events, figures and causes.

Each person or group that plays a role in the plot should be introduced. This introduction should be sized
relative to the person's importance. For example, when introducing Napoleon in the context French revolution his
introduction should be comprehensive. When introducing a finance minister that made only one important decision their
introduction could be shorted (e.g. where they'd come from and how long they'd be in their post).

Events detailed in the notes should not simply just be referred to. An explanation of what happened during the event and what
caused it must be provided.

It is important to detail any important economic factors or conditions that influenced politics and government.
You must also make reference to how life was for middle and lower class people (e.g. peasantry if the topic was the Russian revolution,
workers of Manchester if the topic was the industrial revolution).

The notes may sometimes refer to episodes. These were simply used be the note creator to break the notes up into sections.
You can split your narrative history into sections but DO NOT split it into episodes.

Your target word count is 1500 words. The word count of your narrative must be no more than 150 words more or less than 1500 words.
YOU MUST DO THIS! CHECK YOU ANSWER!

Do not return your resposne as markdown. Just use text.
"""

    chunks = split_text_into_chunks(text, chunk_size)
    
    print(f"Split into {len(chunks)} chunks")

    narrative_history_parts = []
    
    for chunk in chunks:
        user_prompt = f"""
Notes: {chunk}
"""
        request_start_time = time.time()
        print("\nInitiating LLM request")

        completion_response = openai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model=model,
            temperature=temperature
        )

        request_end_time = time.time()
        print(f"Request complete ({(request_end_time - request_start_time):.2f} seconds)")

        narrative_history = completion_response.choices[0].message.content

        print(f"Request input word count: {compute_word_count(chunk)}")
        print(f"Request output word count: {compute_word_count(narrative_history)}")

        narrative_history_parts.append(narrative_history)
    
    narrative_history = "\n".join(narrative_history_parts)
    
    return narrative_history

