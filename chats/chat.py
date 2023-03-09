import time
import openai


# one day in seconds
DAY = 60 * 60 * 24


class Chat:
    def __init__(self, server: int, channel: int, timeout: int = DAY) -> None:
        self.server = server
        self.channel = channel
        self.__prompts = []
        self.__expires = time.time() + timeout

    def get_gpt_response(self, prompt: str) -> str:
        self.__add_prompt(prompt)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "\n".join(self.__prompts)},
                ]
            )

            # return the response from chatgpt
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(e)
            return "Something went wrong. Please try again later."
        
    def __add_prompt(self, prompt: str) -> None:
        self.__prompts.append(prompt)

    @property
    def expired(self) -> bool:
        return time.time() > self.__expires

