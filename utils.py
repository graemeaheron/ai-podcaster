def compute_word_count(text):
    words = text.split()
    return len(words)


def estimate_podcast_minutes_length(text, podcast_words_per_minute = 5_058 / 34.6):
    text_word_count = compute_word_count(text)
    return text_word_count / podcast_words_per_minute

