import discord
import json
import openai


class Bot(discord.Client):
    async def on_ready(self) -> None:
        print("Logged in as {0.user}".format(client))

    async def on_message(self, message) -> None:
        if message.author == client.user:
            return None # don't respond to self, avoids an infinite loop

        print(f"[{message.author}]: {message.content}")

        response = self.get_response(message.content)

        if response is not None:
            await message.channel.send(response)

    def get_response(self, msg: str) -> str:
        msg = msg.lower()

        if msg == "!ping":
            return "pong"

        elif msg == "!help":
            return "Sure, I can help you. Here are the commands I can do: \n\n" \
                "`!ping` - I'll respond with `pong`\n" \
                "`!help` - I'll respond with this message\n" \
                "`!gpt <prompt>` - I'll respond with a GPT-3 response to the prompt"

        elif msg.startswith("!gpt"):
            prompt = self.get_prompt(msg)

            if prompt is None:
                return "Invalid prompt: to give a prompt, type `!gpt <prompt>`"

            # return prompt
            return self.get_chat_gpt_response(prompt)

        else:
            return None

    def get_chat_gpt_response(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ]
        )

        # return the response from chatgpt
        return response["choices"][0]["message"]["content"]

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
        openai.api_key = self.get_credentials()["OPENAI_SECRET_KEY"]

        super().run(self.get_credentials()["DISCORD_SECRET_TOKEN"])


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.typing = False
    intents.presences = False

    client = Bot(intents=intents, command_prefix="!")
    client.run()
