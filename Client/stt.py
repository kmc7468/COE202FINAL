import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

import io
import openai
import pyaudio
import wave

class STT:
	def __init__(self, apikey: str = OPENAI_API_KEY):
		self.__client = openai.OpenAI(
			api_key=apikey
		)
		self.__pyaudio = pyaudio.PyAudio()

	def __del__(self):
		self.__pyaudio.terminate()

	def record(self, duration: float, channels: int = 1, rate: int = 16000, chunk: int = 1024) -> io.BytesIO:
		stream = self.__pyaudio.open(
			format=pyaudio.paInt16,
			channels=channels,
			rate=rate,
			input=True,
			frames_per_buffer=chunk
		)

		frames = []

		for _ in range(0, int(rate / chunk * duration)):
			frames.append(stream.read(chunk))

		stream.stop_stream()
		stream.close()

		stream = io.BytesIO()
		stream.name = "pyaudio.wav"

		with wave.open(stream, "wb") as wf:
			wf.setnchannels(channels)
			wf.setsampwidth(self.__pyaudio.get_sample_size(pyaudio.paInt16))
			wf.setframerate(rate)
			wf.writeframes(b"".join(frames))

		stream.seek(0)

		return stream

	def stt(self, file, prompt: str = None) -> str:
		transcript = self.__client.audio.transcriptions.create(
			model="whisper-1",
			language="ko",
			file=file,
			prompt=prompt
		)

		return transcript.text