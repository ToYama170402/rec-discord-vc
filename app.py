import discord
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from db import db
from os import environ

load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
DB = db()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


is_joined = False


@client.event
async def on_voice_state_update(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
):
    global is_joined
    if member.bot:
        is_joined = not is_joined
        return
    elif (
        not is_joined
        and before.channel is None
        and after.channel is not None
        and DB.find_user(member.id) is not None
    ):
        vc = await after.channel.connect()
        vc.start_recording(discord.sinks.WaveSink(), finished_callback)
        return
    elif (
        before.channel is not None
        and after.channel is None
        and len(
            list(
                filter(
                    lambda member: DB.find_user(member.id) != None,
                    before.channel.members,
                )
            )
        )
        == 0
        and (vc := before.channel.guild.voice_client)
    ):
        vc.stop_recording()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.content.startswith("!toggle"):
        user_id = message.author.id
        if (user := DB.find_user(user_id)) is None:
            DB.add_user(user_id, True)
            await message.channel.send(
                "Send recording data after recording is now enabled."
            )
            return
        else:
            user.toggle_send_after_rec()
            DB.save()
            await message.channel.send(
                f"Send recording data after recording is now {'enabled' if user.send_after_rec else 'disabled'}."
            )
            return
    elif message.content.startswith("!remove"):
        user_id = message.author.id
        if DB.find_user(user_id) is not None:
            DB.remove_user(user_id)
            await message.channel.send("I will no longer record you.")
            return
        else:
            await message.channel.send("You are not in the database.")
            return


async def finished_callback(sink: discord.sinks.Sink, *args: discord.VoiceState):
    recording_dir = Path("./recordings")
    recording_dir.mkdir(exist_ok=True)
    for user_id, audio in sink.audio_data.items():
        user_dir = Path(str(user_id))
        (save_dir := (recording_dir / user_dir)).mkdir(exist_ok=True)
        save_dir.mkdir(exist_ok=True)
        if (user := DB.find_user(int(user_id))) is not None:
            file = discord.File(
                audio.file,
                f"{save_dir/datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{user_id}.{sink.encoding}",
            )
            if file.filename:
                with open(file.filename, mode="wb") as f:
                    f.write(file.fp.read())
            if user.send_after_rec and (discord_user := client.get_user(int(user_id))):
                await discord_user.send(file=file)
    for vc in client.voice_clients:
        await vc.disconnect(force=True)


client.run(environ.get("DISCORD_BOT_TOKEN"))
