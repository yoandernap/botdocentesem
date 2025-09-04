from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging
import random
import asyncio
import os
from flask import Flask
import threading

# Configurar logging para ver errores
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Crear app Flask para health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot de Telegram funcionando correctamente ✅", 200

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

# Datos de asignaturas actualizados con IDs consistentes
SUBJECTS = {
    "introduccion_biblia": {
        "name": "Introducción a la Biblia",
        "resources": "https://t.me/semholguincentro/11"
    },
    "psicologia": {
        "name": "Psicología",
        "resources": "https://t.me/semholguincentro/9"
    },
    "historia_universal": {
        "name": "Historia Universal",
        "resources": "https://t.me/semholguincentro/17"
    },
    "historia_iglesia": {
        "name": "Historia de la Iglesia",
        "resources": "https://t.me/semholguincentro/18"
    },
    "liderazgo": {
        "name": "Liderazgo",
        "resources": "https://t.me/semholguincentro/23"
    },
    "liturgia": {
        "name": "Liturgia",
        "resources": "https://t.me/semholguincentro/35"
    },
    "metodos_estudio_biblico": {
        "name": "Métodos de Estudio Bíblico",
        "resources": "https://t.me/semholguincentro/25"
    },
    "homiletica": {
        "name": "Homilética",
        "resources": "https://t.me/semholguincentro/13"
    },
    "metodismo_i_historia": {
        "name": "Metodismo I Historia",
        "resources": "https://t.me/semholguincentro/38"
    },
    "metodismo_ii_doctrina": {
        "name": "Metodismo II Doctrina",
        "resources": "https://t.me/semholguincentro/39"
    },
    "introduccion_teologia": {
        "name": "Introducción a la Teología",
        "resources": "https://t.me/semholguincentro/15"
    },
    "tecnicas_estudio": {
        "name": "Técnicas de estudio",
        "resources": "https://t.me/semholguincentro/21"
    },
    "mision_evangelizacion": {
        "name": "Misión y Evangelización",
        "resources": "https://t.me/semholguincentro/20"
    },
    "computacion": {
        "name": "Computación",
        "resources": "https://t.me/semholguincentro/19"
    },
    "ministerio_educativo_i": {
        "name": "Ministerio Educativo de la Iglesia I",
        "resources": "https://t.me/semholguincentro/10"
    },
    "musica_tradicion_cristiana": {
        "name": "Música en la tradición cristiana",
        "resources": "https://t.me/semholguincentro/16"
    },
    "dinamica_estructura": {
        "name": "Dinámica de la estructura",
        "resources": "https://t.me/semholguincentro/24"
    },
    "redaccion_ortografia": {
        "name": "Redacción y Ortografía",
        "resources": "https://t.me/semholguincentro/12"
    }
}

# Mensajes de bienvenida aleatorios
WELCOME_MESSAGES = [
    "¡Bienvenido {name} al Grupo del Seminario Evangélico Metodista Extensión Holguín! 🎓 Esperamos que las clases le sean de provecho para su edificación en Cristo.",
]

class ClassBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    async def set_bot_commands(self):
        """Configurar los comandos del bot"""
        commands = [
            BotCommand("start", "🚀 Iniciar conversación con el Asistente Docente"),
            BotCommand("asignaturas", "📚 Ver lista de asignaturas"),
            BotCommand("bibliografia", "📖 Ver bibliografía"),
            BotCommand("normas", "📋 Ver normas del grupo"),
            BotCommand("help", "❓ Obtener ayuda")
        ]
        await self.application.bot.set_my_commands(commands)

    def setup_handlers(self):
        """Configurar los manejadores de comandos"""
        # Comandos normales
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("asignaturas", self.list_subjects))
        self.application.add_handler(CommandHandler("bibliografia", self.list_bibliografia))
        self.application.add_handler(CommandHandler("normas", self.rules))
        self.application.add_handler(CommandHandler("help", self.help))

        # Handlers para botones interactivos
        self.application.add_handler(CallbackQueryHandler(self.subject_button, pattern="^subject_"))
        self.application.add_handler(CallbackQueryHandler(self.back_button, pattern="^back_to_"))

        # ✅ MANEJADOR PARA NUEVOS MIEMBROS (BIENVENIDA AUTOMÁTICA)
        self.application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self.welcome_new_member
            )
        )

    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """✅ Dar la bienvenida automática a nuevos miembros"""
        print("🔔 Evento de nuevo miembro detectado!")

        if not update.message or not update.message.new_chat_members:
            return

        for new_member in update.message.new_chat_members:
            if new_member.is_bot:
                continue

            print(f"🎓 Saludando nuevo estudiante: {new_member.first_name}")

            welcome_message = random.choice(WELCOME_MESSAGES).format(
                name=new_member.first_name
            )

            full_welcome = f"""
{welcome_message}

📋 Para comenzar:
• /asignaturas - Ver las materias
• /bibliografia - Ver las bibliografías
• /normas - Leer las reglas del grupo
• /help - Obtener ayuda

¡No dudes en preguntar si tienes dudas! 🤗
            """

            try:
                await update.message.reply_text(full_welcome)
                print(f"✅ Bienvenida enviada a {new_member.first_name}")
                
            except Exception as e:
                print(f"❌ Error enviando bienvenida: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mensaje de bienvenida"""
        user = update.effective_user
        chat_type = update.effective_chat.type
        
        if chat_type in ["group", "supergroup"]:
            keyboard = [
                [InlineKeyboardButton("🚀 Iniciar conversación privada", url=f"https://t.me/{context.bot.username}?start=start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = f"""
👋 ¡Hola {user.first_name}! 

Soy el Asistente Docente del Seminario Evangélico Metodista Extensión Holguín.

Para una mejor experiencia, te invito a iniciar una conversación privada conmigo.

¡Allí podré ayudarte con toda la información que necesites! 📚
            """
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        else:
            welcome_text = f"""
👋 ¡Hola {user.first_name}! Bienvenido al Asistente Docente del Seminario Evangélico Metodista Extensión Holguín!

🎓 Esperamos que las clases le sean de provecho para su edificación en Cristo.

Puedo brindar información sobre:
📚 /asignaturas - Ver lista de asignaturas
📖 /bibliografia - Ver lista de bibliografía
📋 /normas - Ver reglas del grupo
❓ /help - Obtener ayuda

¡Espero que te sea útil!
            """
            await update.message.reply_text(welcome_text)
        
        await self.set_bot_commands()

    async def list_subjects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar lista de asignaturas con botones interactivos"""
        if update.effective_chat.type in ["group", "supergroup"]:
            keyboard = [
                [InlineKeyboardButton("🚀 Ver asignaturas en privado", url=f"https://t.me/{context.bot.username}?start=asignaturas")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📚 Para consultar la lista completa de asignaturas, te invito a continuar la conversación en privado:",
                reply_markup=reply_markup
            )
            return
            
        keyboard = []
        for subject_id, subject_info in SUBJECTS.items():
            keyboard.append([InlineKeyboardButton(
                subject_info["name"],
                callback_data=f"subject_{subject_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("◀️ Volver al inicio", callback_data="back_to_start")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📚 Lista de Asignaturas:\n\nSelecciona una asignatura para ver más detalles:",
            reply_markup=reply_markup
        )

    async def list_bibliografia(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar información de bibliografía"""
        if update.effective_chat.type in ["group", "supergroup"]:
            keyboard = [
                [InlineKeyboardButton("🚀 Ver bibliografía en privado", url=f"https://t.me/{context.bot.username}?start=bibliografia")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📖 Para consultar la bibliografía completa, te invito a continuar la conversación en privado:",
                reply_markup=reply_markup
            )
            return
            
        bibliografia_text = """
📚 Bibliografía Recomendada:

🔗 Accede a toda la literatura aquí:
https://t.me/semholguincentro/40
        """
        
        keyboard = [[InlineKeyboardButton("◀️ Volver al inicio", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(bibliografia_text, reply_markup=reply_markup)

    async def subject_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar la selección de una asignatura"""
        query = update.callback_query
        await query.answer()

        subject_id = "_".join(query.data.split("_")[1:])

        if subject_id in SUBJECTS:
            subject = SUBJECTS[subject_id]
            response_text = f"""
📖 **{subject['name']}**

🔗 Recursos: {subject['resources']}
            """
            await query.edit_message_text(
                text=response_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Volver a asignaturas", callback_data="back_to_subjects")]
                ])
            )
        else:
            await query.edit_message_text(
                text="❌ Lo siento, no se pudo encontrar la información de esta asignatura.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Volver a asignaturas", callback_data="back_to_subjects")]
                ])
            )

    async def back_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar botones de volver"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "back_to_start":
            user = query.from_user
            welcome_text = f"""
👋 ¡Hola {user.first_name}! Bienvenido al Asistente Docente del Seminario Evangélico Metodista Extensión Holguín!

🎓 Esperamos que las clases le sean de provecho para su edificación en Cristo.

Puedo brindar información sobre:
📚 /asignaturas - Ver lista de asignaturas
📖 /bibliografia - Ver lista de bibliografía
📋 /normas - Ver reglas del grupo
❓ /help - Obtener ayuda

¡Espero que te sea útil!
            """
            await query.edit_message_text(welcome_text)
            
        else:
            keyboard = []
            for subject_id, subject_info in SUBJECTS.items():
                keyboard.append([InlineKeyboardButton(
                    subject_info["name"],
                    callback_data=f"subject_{subject_id}"
                )])
            
            keyboard.append([InlineKeyboardButton("◀️ Volver al inicio", callback_data="back_to_start")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📚 **Lista de Asignaturas:**\n\nSelecciona una asignatura para ver más detalles:",
                reply_markup=reply_markup
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar mensaje de ayuda"""
        if update.effective_chat.type in ["group", "supergroup"]:
            keyboard = [
                [InlineKeyboardButton("🚀 Obtener ayuda en privado", url=f"https://t.me/{context.bot.username}?start=help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❓ Para obtener ayuda completa, te invito a continuar la conversación en privado:",
                reply_markup=reply_markup
            )
            return
            
        help_text = """
🤖 Bot de Gestión de Asignaturas

Comandos disponibles:
/start - Iniciar el bot
/asignaturas - Ver lista de asignaturas
/bibliografia - Ver bibliografía recomendada
/normas - Ver reglas del grupo
/help - Mostrar esta ayuda

Funcionalidades:
- Consultar información de asignaturas
- Recibir bienvenida automática al unirte
- Acceder a recursos de cada materia
            """
        await update.message.reply_text(help_text)

    async def rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar normas del grupo"""
        if update.effective_chat.type in ["group", "supergroup"]:
            keyboard = [
                [InlineKeyboardButton("🚀 Ver normas en privado", url=f"https://t.me/{context.bot.username}?start=normas")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📋 Para consultar las normas completas, te invito a continuar la conversación en privado:",
                reply_markup=reply_markup
            )
            return
            
        rules_text = """
📋 Normas del Grupo de Clase:

1. 🚫 No spam ni publicidad
2. 👥 Respeto entre hermanos
3. 📚 Mantener el enfoque en temas académicos
4. 🔇 Evitar enlaces externos
5. 🤝 Sólo dudas con respecto al seminario

¡Entre todos mantengamos un buen ambiente de aprendizaje! Dios los bendiga! 🌟
        """
        await update.message.reply_text(rules_text)

def run_flask():
    """Ejecutar servidor Flask para health checks"""
    app.run(host='0.0.0.0', port=5000, debug=False)

async def main():
    """Función principal para Render"""
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN no encontrado en variables de entorno")
        exit(1)

    print("🤖 Iniciando bot en Render...")
    print(f"📚 Total de asignaturas: {len(SUBJECTS)}")
    
    # Iniciar servidor Flask en segundo plano para health checks
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Servidor Flask iniciado para health checks (puerto 5000)")
    
    # Crear y ejecutar el bot
    bot = ClassBot(BOT_TOKEN)
    
    try:
        print("✅ Bot iniciado correctamente")
        
        await bot.application.run_polling()
        
    except Exception as e:
        print(f"❌ Error: {e}")

# 🚀 EJECUCIÓN PARA RENDER
if __name__ == "__main__":
    asyncio.run(main())