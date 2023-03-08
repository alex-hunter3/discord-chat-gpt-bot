import time
import openai


class Chat:
    def __init__(self, server, channel, timeout=86400):
        self.server = server
        self.channel = channel
        self.__prompts = []
        self.__expires = time.time() + timeout

    def get_gpt_response(self, prompt):
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
        
    def __add_prompt(self, prompt):
        self.__prompts.append(prompt)

    @property
    def expired(self):
        return time.time() > self.__expires
        
