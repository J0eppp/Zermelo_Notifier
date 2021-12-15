from Browser import Browser


class Task():
    def __init__(self, school_name: str, username: str, password: str, single_sign_on: bool, channel_id: int):
        self.school_name = school_name
        self.username = username
        self.password = password
        self.single_sign_on = single_sign_on
        # self.bot: commands.Bot = bot
        self.channel_id = channel_id

    # @tasks.loop(count=1)
    # async def run(self) -> dict:
    #     browser = Browser()
    #     result = {}

    #     token = browser.login_get_token(
    #         self.school_name, self.username, self.password, self.single_sign_on)
    #     browser.close()
    #     if len(token) == 0:
    #         result["error"] = "Error, could not find token"
    #         result["description"] = "Apologies, I was not able to find the token. Please try again or contact the bot administrator."
    #     else:
    #         result["token"] = token
    #     print(token)
    #     channel = await self.bot.fetch_channel(self.channel_id)
    #     await channel.send(token)
