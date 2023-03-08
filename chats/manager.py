import discord
import time
import threading
import chats.chat


class ChatManager:
    def __init__(self):
        self.chats = []

        remove_expired_chats_thread = threading.Thread(target=self.remove_expired_chats)
        remove_expired_chats_thread.start()

    def get_chat_response(self, msg: discord.message.Message, prompt: str) -> str:
        chat = self.find_chat(msg)

        if chat is None:
            chat = self.add_chat(msg)

        return chat.get_gpt_response(prompt)

    def add_chat(self, chat: discord.message.Message) -> chats.chat.Chat:
        new_chat = chats.chat.Chat(
            server=chat.guild.id, 
            channel=chat.channel.id
        )

        self.chats.append(new_chat)

        return new_chat

    def find_chat(self, msg: discord.message.Message) -> chats.chat.Chat | None:
        for chat in self.chats:
            if chat.server == msg.guild.id and chat.channel == msg.channel.id:
                return chat

        return None

    def remove_expired_chats(self) -> None:
        while True:
            for chat in self.chats:
                if chat.expired:
                    self.remove_chat(chat)

            time.sleep(10)

    def remove_chat(self, chat: chats.chat.Chat) -> None:
        try:
            self.chats.remove(chat)
        except ValueError:
            pass
        except Exception as e:
            print(e)