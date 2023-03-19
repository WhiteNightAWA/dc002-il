import json
import asyncio


def checkBotState():
    with open("setting.json", "r") as file:
        return json.load(file)["state"]

def changeBotState():
    with open("setting.json", "r") as file:
        state = json.load(file)
    state["state"] = not state["state"]
    with open("setting.json", "w+") as file:
        file.write(json.dumps(state))
    return state["state"]


async def Close(ctx):
    msg = await ctx.channel.send("The bot has been closed, please ask admin to turn on it. This message will be deleted in 3s.")
    await asyncio.sleep(3)
    await msg.delete()
