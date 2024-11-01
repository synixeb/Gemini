import discord
from discord.ext import commands
from scripts.commande import *
from scripts.textGeneration import *

import Error.DiscordExecp as DiscordExecp

TOKEN = os.getenv("TOKEN_DISCORD")
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Connecter en tant que {bot.user}')
    await bot.change_presence(activity=discord.Game(name="aider les étudiant"))
    log("Bot connecté", "Bot", 1)


async def send_note_info(ctx: commands.Context, note_func):
    try:
        url = makeURL(ctx.author.name)
        if url:
            print(url)
            tab, isNote = note_func(url)
            if tab == []:
                await ctx.send("Aucune note n'a été ajoutée")
                log("Aucune note n'a été ajoutée", ctx.author.name)
            else:
                await ctx.send("La dernière note ajoutée est:")
                await ctx.send(f"Titre: {tab[0]}")
                await ctx.send(f"Intitulé: {tab[1]}")
                if isNote:
                    await ctx.send(f"Auteur: {tab[2]}")
                log("Note envoyée", ctx.author.name)
        else:
            raise Exception("Erreur lors de la récupération de l'url")
    except Exception as e:
        print(e)
        log("Erreur lors de la récupération de la note", ctx.author.name, 2)
        await DiscordExecp.DiscordExecp(ctx, e).send_error()


@bot.command()
async def note(ctx: commands.Context):
    await send_note_info(ctx, readXML)


@bot.command()
async def noteV(ctx: commands.Context):
    await send_note_info(ctx, readXMLNote)


@bot.command()
async def talk(ctx: commands.Context, *args):
    try:
        messages = [message async for message in ctx.channel.history(limit=10)]
        context = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
        
        prompt = ' '.join(args)
        full_prompt = f"Context: \n <--//{context}//--> \n\nPrompt:\n >**++{prompt}++--<"
        
        # Generate text based on the full prompt
        text = text_generation(full_prompt)
        await ctx.send(text)
        log(f"Context Prompt: ({prompt}) / V", ctx.author.name, 1)
    except Exception as e:
        print(e)
        log(f"Context Prompt: ({prompt}) / X", ctx.author.name, 2)
        await DiscordExecp.DiscordExecp(ctx, e).send_error()


@bot.command()
async def salle(ctx: commands.Context, *args):
    try:
        filter_salle = []
        if args[0] == "-":
            filter_salle = args[1:]
                
        salles = get_salle_libre(filter_salle)
        if salles == None:
            raise Exception("Erreur lors de la récupération des salles")
        elif salles == []:
            await ctx.send("Aucune salle libre ;(")
        else:
            await ctx.send("Les salles libres sont:")
            for salle in salles:
                await ctx.send(salle + " " + data_salle[salle]["type"])
            await ctx.send("Fin de la liste")
        log("Salle envoyée", ctx.author.name)
    except Exception as e:
        print(e)
        await DiscordExecp.DiscordExecp(ctx, e).send_error()


@bot.command()
async def helpme(ctx: commands.Context):
    await ctx.send("`/helpme` : Renvoie les commandes disponible (fonctionne)\n" +
    "`/note` : Renvoie l'intitude de la dernière note ajoutée sur Tommus (la note n'est pas affichée) (ne fonctionne pas) \n" +
    "`/noteV` : Renvoie la dernière note ajoutée sur le site de Tommus (ne fonctionne pas)\n" +
    "`/talk` : Renvoie une réponse à une question posée avec le contexte de la question (fonctionne)\n" +
    "`/salle` : Renvoie les salles libres à l'heure actuelle (ne fonctionne pas)\n" +
    "vous pouvez filtrez les salles en ajoutant un tiret suivi du filtre (ex: `/salle - S27`)\n" +
    "ou les types de salles (ex: `/salle - TD `) mais aussi les deux (ex: `/salle - TD S27`)")


if __name__ == '__main__':
    bot.run(TOKEN)
