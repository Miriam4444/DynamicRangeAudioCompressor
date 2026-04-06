from pydub import AudioSegment

audio = AudioSegment.from_mp3("Mississippi-John-Hurt_Nobodys-Dirty-Business.mp3")

# slice it (milliseconds)
trimmed = audio[5000:10000]  # first 10 seconds

trimmed.export("trimmed.wav", format="wav")