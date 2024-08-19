import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados del ConversationHandler
ASKING_FOR_IMAGE = 1

# Token del bot y ID del canal
BOT_TOKEN = "7369622624:AAFofO9gKPuChXn0-XVZpV3wv1US_CEQMuI"
CHANNEL_ID = "@donpolloscrapper_refes"

# Contador para las referencias
ref_counter = 1

# Inicia el comando /refe
async def start_refe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, envía una imagen y un mensaje que deseas enviar al canal.")
    return ASKING_FOR_IMAGE

# Maneja la recepción de la imagen y el mensaje
async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ref_counter

    user = update.message.from_user
    message_text = update.message.caption if update.message.caption else "Sin mensaje"
    
    if not update.message.photo:
        await update.message.reply_text("Por favor, envía una imagen junto con un mensaje.")
        return ASKING_FOR_IMAGE

    file_id = update.message.photo[-1].file_id

    template = f"""
━━━━━━━━━━━━━━━━
Message: {message_text}
[⽷] ID: {user.id}
[⽷] Username: @{user.username if user.username else "N/A"}
[⽷] Nombre: {user.first_name}
━━━━━━━━━━━━━━━━

#REFE{str(ref_counter).zfill(2)} 
    """

    try:
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=template)
        await update.message.reply_text("Tu mensaje ha sido enviado al canal exitosamente.")
        ref_counter += 1
    except TelegramError as e:
        logger.error(f"Error al enviar el mensaje al canal: {e}")
        await update.message.reply_text("Hubo un error al enviar tu mensaje. Por favor, inténtalo de nuevo más tarde.")

    return ConversationHandler.END

# Maneja la cancelación de la conversación
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

# Maneja mensajes inesperados
async def handle_invalid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Por favor, envía una imagen con un mensaje o usa /cancel para cancelar la operación.")
    return ASKING_FOR_IMAGE

def main() -> None:
    try:
        # Crear la aplicación
        application = Application.builder().token(BOT_TOKEN).build()

        # Maneja el flujo de la conversación
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('refe', start_refe)],
            states={
                ASKING_FOR_IMAGE: [
                    MessageHandler(filters.PHOTO, receive_image),
                    MessageHandler(filters.ALL & ~filters.COMMAND, handle_invalid_input)
                ],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        application.add_handler(conv_handler)

        # Iniciar el bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error en la aplicación principal: {e}")

if __name__ == '__main__':
    main()
