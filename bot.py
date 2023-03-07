import asyncio
import discord
import json
import openai
import threading
import time


class ChatManager:
    def __init__(self):
        self.chats = []

    def get_chat_response(self, msg: discord.message.Message, prompt: str) -> str:
        chat = self.find_chat(msg)

        if chat is None:
            self.add_chat(msg)
            chat = self.find_chat(msg)

        chat["prompts"].append(prompt)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "\n".join(chat["prompts"])},
                ]
            )

            # return the response from chatgpt
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(e)
            return "Something went wrong. Please try again later."

    def add_chat(self, chat: discord.message.Message) -> None:
        return self.chats.append({
            "expires": self.timeout,
            "server": chat.guild.id,
            "channel": chat.channel.id,
            "prompts": []
        })

    def find_chat(self, msg: discord.message.Message) -> dict:
        self.remove_expired_chats()

        for chat in self.chats:
            if chat["server"] == msg.guild.id and chat["channel"] == msg.channel.id:
                return chat

        return None

    def remove_expired_chats(self) -> None:
        for chat in self.chats:
            if self.is_timed_out(chat):
                self.remove_chat(chat)
                return None # stop because we found the chat to remove

    def remove_chat(self, chat: dict) -> None:
        try:
            self.chats.remove(chat)
        except ValueError:
            pass
        except Exception as e:
            print(e)

    def is_timed_out(self, chat: dict) -> bool:
        return time.time() > chat["expires"]

    @property
    def timeout(self) -> int:
        return time.time() + 86400


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        credentials = self.get_credentials()

        self.OPEN_AI_KEY = credentials["OPENAI_SECRET_KEY"]
        self.DISCORD_SECRET_TOKEN = credentials["DISCORD_SECRET_TOKEN"]

        # event loop so that we can get multiple responses from the GPT-3 API at the same time
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # set up the ChatManager to handle chat responses
        self.chat_manager = ChatManager()

        super().__init__(*args, **kwargs)

    async def on_ready(self) -> None:
        print("Logged in as {0.user}".format(client))

        # set the activity
        await self.change_presence(activity=discord.Game(name="Answering queries..."))

    async def on_message(self, message: discord.message.Message) -> None:
        if message.author == client.user:
            return None # don't respond to self, avoids an infinite loop

        print(f"[{message.author}]: {message.content}")

        thread = threading.Thread(target=self.handle_message, args=(message,))
        thread.start()

    async def send_message(self, message: discord.message.Message, response: str):
        await message.channel.send(response)

    def handle_message(self, message: discord.message.Message):
        response = self.get_response(message)

        if response is not None:
            self.loop.create_task(self.send_message(message, response))

    def get_response(self, message) -> str:
        msg = message.content.lower()

        if msg == "!ping":
            return "pong"

        elif msg == "!help":
            return "Sure, I can help you. Here are the commands I can do: \n\n" \
                "`!ping` - I'll respond with `pong`\n" \
                "`!help` - I'll respond with this message\n" \
                "`!clear` - I'll clear all prompts from this channel\n" \
                "`!gpt <prompt>` - I'll respond with a GPT-3 response to the prompt"

        elif msg == "!clear":
            self.chat_manager.remove_chat(self.chat_manager.find_chat(message))
            return "All prompts cleared from this channel."

        elif msg.startswith("!gpt"):
            prompt = self.get_prompt(msg)

            if prompt is None:
                return "Invalid prompt: to give a prompt, type `!gpt <prompt>`"

            # return prompt
            return self.get_chat_gpt_response(message, prompt)

        else:
            return None

    def get_chat_gpt_response(self, message, prompt: str) -> str:
        try:
            return self.chat_manager.get_chat_response(message, prompt)
        except Exception as e:
            print(e)
            return "Something went wrong. Please try again later."

    def get_prompt(self, msg: str) -> str:
        prompt = msg.split(" ")

        if len(prompt) == 1:
            return None

        # remove the command from the prompt
        return " ".join(msg.split(" ")[1:]) 

    def get_credentials(self) -> dict:
        with open("credentials.json", "r") as f:
            return json.load(f)

    def run(self):
        openai.api_key = self.OPEN_AI_KEY

        super().run(self.DISCORD_SECRET_TOKEN)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.typing = False
    intents.presences = False

    client = Bot(intents=intents, command_prefix="!")
    client.run()
