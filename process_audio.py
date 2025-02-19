import os
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from pydub.exceptions import CouldntDecodeError

def reverse_audio(audio):
    return audio.reverse()

def add_echo(audio, delay_ms=250, decay=0.5):
    samples = np.array(audio.get_array_of_samples(), dtype=np.int32)  # Prevent overflow
    sample_rate = audio.frame_rate
    num_channels = audio.channels
    delay_samples = int(sample_rate * (delay_ms / 1000))

    echoed_samples = np.copy(samples)
    for i in range(delay_samples, len(samples)):
        echoed_samples[i] += int(samples[i - delay_samples] * decay)
    
    echoed_samples = np.clip(echoed_samples, -32768, 32767)  # Prevent clipping

    return AudioSegment(
        echoed_samples.astype(np.int16).tobytes(), 
        frame_rate=sample_rate, 
        sample_width=audio.sample_width, 
        channels=num_channels
    )

def add_reverb(audio, decay=0.4, num_reflections=5):
    samples = np.array(audio.get_array_of_samples(), dtype=np.int32)
    sample_rate = audio.frame_rate
    num_channels = audio.channels
    
    reverbed_samples = np.copy(samples)
    for i in range(1, num_reflections + 1):
        delay_samples = int(sample_rate * (i * 0.02))  # 20ms increments
        for j in range(delay_samples, len(samples)):
            reverbed_samples[j] += int(samples[j - delay_samples] * (decay / i))
    
    reverbed_samples = np.clip(reverbed_samples, -32768, 32767)  # Prevent clipping

    return AudioSegment(
        reverbed_samples.astype(np.int16).tobytes(), 
        frame_rate=sample_rate, 
        sample_width=audio.sample_width, 
        channels=num_channels
    )

def process_audio_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for root, _, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".wav"):
                input_path = os.path.join(root, filename)
                rel_path = os.path.relpath(input_path, input_folder)
                output_path = os.path.join(output_folder, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                try:
                    audio = AudioSegment.from_wav(input_path)
                except CouldntDecodeError:
                    print(f"Could not decode {input_path}, skipping.")
                    continue
                
                reversed_audio = reverse_audio(audio)
                echoed_audio = add_echo(reversed_audio)
                reverbed_audio = add_reverb(echoed_audio)
                
                reverbed_audio.export(output_path, format="wav")
                print(f"Processed: {input_path} -> {output_path}")

if __name__ == "__main__":
    input_folder = input("Enter the path to the input folder: ")
    output_folder = input("Enter the path to the output folder: ")
    process_audio_folder(input_folder, output_folder)
    print("Processing complete!")