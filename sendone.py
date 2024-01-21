import asyncio
from tools import send_telegram_message

async def sendone():
    await send_telegram_message(
        
        message_text=f"🥊 Node '<b>massa01</b>': Missed blocks on wallet:\n\n<pre>AU1qLrbaC4vWNRLvTaRFY9SBRe7oDcrVqXrjiJmuMFy4eBknBgMV</pre>\n\nBlocks missed in last cycle:\n\n<pre>3</pre>"
        
        )
    
    return


if __name__ == "__main__":
    asyncio.run(sendone())