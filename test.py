from pydub import AudioSegment
import os

# Construct the correct path to the audio file
input_file = os.path.join(os.getcwd(), "static", "office-ambience.mp3")
output_file = os.path.join(os.getcwd(), "static", "office-ambience_24000.mp3")

# Load the audio file
audio = AudioSegment.from_file(input_file)

# Convert the sample rate to 24000 Hz
audio = audio.set_frame_rate(24000)

# Export the resampled audio file
audio.export(output_file, format="mp3")

print("Audio file converted successfully!")
