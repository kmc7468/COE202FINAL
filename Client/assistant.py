import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

import openai
import time

class Assistant:
	def __init__(self, apikey: str = OPENAI_API_KEY, assid: str = OPENAI_ASSISTANT_ID):
		self.__client = openai.OpenAI(
			api_key=apikey
		)
		self.__assistantid = assid

	def send(self, content: str, retrivetries: int = 10) -> str:
		thread = self.__client.beta.threads.create()
		self.__client.beta.threads.messages.create(
			thread_id=thread.id,
			role="user",
			content=content
		)
		run = self.__client.beta.threads.runs.create(
			thread_id=thread.id,
			assistant_id=self.__assistantid
		)

		for _ in range(retrivetries):
			retrive = self.__client.beta.threads.runs.retrieve(
				thread_id=thread.id,
				run_id=run.id
			)
			if retrive.status == "completed":
				msgs = self.__client.beta.threads.messages.list(
					thread_id=thread.id
				)

				return msgs.data[0].content[0].text.value
			elif retrive.status == "failed":
				raise Exception("Run failed")
			else:
				time.sleep(3)
		else:
			self.__client.beta.threads.runs.cancel(
				thread_id=thread.id,
				run_id=run.id
			)
			raise Exception("Time out")