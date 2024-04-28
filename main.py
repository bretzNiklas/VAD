import webrtcvad
import pyaudio
import wave
import os


def create_audio_file(frames, filename="audio"):
    """Save the recorded frames to a WAV file."""
    output_folder = "recorded_audio"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_path = os.path.join(output_folder, f"{filename}.wav")
    wf = wave.open(file_path, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b"".join(frames))
    wf.close()
    print(f"Audio saved to {file_path}")


def open_mic_stream():
    """Set up and open the microphone stream."""
    audio_format = pyaudio.paInt16
    num_channels = 1
    sample_rate = 16000
    chunk_size = int(sample_rate * 0.02)  # 20ms
    p = pyaudio.PyAudio()
    stream = p.open(
        format=audio_format,
        channels=num_channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size
    )
    return stream, p


def setup_vad(aggressiveness=3):
    """Initialize and return a VAD."""
    vad = webrtcvad.Vad()
    vad.set_mode(aggressiveness)
    return vad


def process_audio_stream(stream, vad, p):
    """Process the audio stream."""
    num_speech_frames = 0
    recording = False
    recorded_frames = []
    i = 0
    try:
        while True:
            frame = stream.read(320)  # Read 20ms frame
            is_speech = vad.is_speech(frame, 16000)  # Check if frame is speech

            if is_speech:
                if not recording:
                    recording = True
                    recorded_frames = []
                    num_speech_frames = 0
                recorded_frames.append(frame)
                num_speech_frames += 1
                print("Recording Speech...")
            elif recording:
                # Stop recording if speech has ended and save the file
                recording = False
                if num_speech_frames > 15:  # Only save if we have a significant amount of speech
                    create_audio_file(recorded_frames, f"audio_{i}")
                    i = i+1
                print("Speech ended.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    stream, p = open_mic_stream()
    vad = setup_vad()
    process_audio_stream(stream, vad, p)
