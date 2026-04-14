import os
from tqdm import tqdm
from TTS.api import TTS
from pydub import AudioSegment

def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text, max_length=500):
    # Split the text into roughly sentence-sized chunks
    sentences = text.replace('\n', ' ').split('. ')
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def text_to_speech(model_name, speaker, input_path, output_path):
    print(f"Loading model: {model_name}")
    tts = TTS(model_name=model_name, progress_bar=False, gpu=False)

    text = read_text_file(input_path)
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")

    os.makedirs("temp_audio", exist_ok=True)
    audio_files = []

    for i, chunk in enumerate(tqdm(chunks, desc="Converting chunks")):
        temp_file = f"temp_audio/chunk_{i}.wav"
        tts.tts_to_file(text=chunk, speaker=speaker, file_path=temp_file)
        audio_files.append(temp_file)

    # Combine all chunks into one audio file
    print("Combining audio files...")
    combined = AudioSegment.empty()
    for file in tqdm(audio_files, desc="Merging audio"):
        combined += AudioSegment.from_wav(file)

    combined.export(output_path, format="wav")
    print(f"Conversion complete. Output saved to: {output_path}")

    # Clean up temporary files
    for f in audio_files:
        os.remove(f)
    os.rmdir("temp_audio")

if __name__ == "__main__":
    model_name = "tts_models/en/vctk/vits"
    speaker = input("Enter speaker ID (e.g., p260, p263): ").strip()
    input_path = input("Enter input text file path: ").strip()
    output_path = input("Enter output audio file path (e.g., output.wav): ").strip()

    text_to_speech(model_name, speaker, input_path, output_path)
