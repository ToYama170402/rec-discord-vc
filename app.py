import discord
from dotenv import load_dotenv
import os
from datetime import datetime
import pathlib

load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_voice_state_update(member, before, after):
    if (
        member.id == int(os.environ.get("TARGET_USER_ID") or 0)
        and after.channel is not None
        and before.channel != after.channel
    ):
        channel = after.channel
        vc = await channel.connect()
        vc.start_recording(discord.sinks.WaveSink(), finished_callback)
    if (
        member.id == int(os.environ.get("TARGET_USER_ID") or 0)
        and before.channel is not None
        and before.channel != after.channel
    ):
        for vc in client.voice_clients:
            await vc.disconnect(force=True)


async def finished_callback(sink, *args):
    recording_dir = pathlib.Path("./recordings")
    recording_dir.mkdir(exist_ok=True)
    files = [
        discord.File(
            audio.file,
            f"{recording_dir/datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{user_id}.{sink.encoding}",
        )
        for user_id, audio in sink.audio_data.items()
    ]
    for file in files:
        if file.filename:
            with open(file.filename, mode="wb") as f:
                f.write(file.fp.read())


client.run(os.environ.get("DISCORD_BOT_TOKEN"))
