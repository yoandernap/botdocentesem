from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import logging
import random
import asyncio
import os
from datetime import time, datetime, timedelta
import pytz
from flask import Flask
import threading

# Configurar logging para ver errores
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Crear app Flask para health checks de Render
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

# Base de datos de promesas bíblicas
BIBLE_PROMISES = [
     {"text": "Reconoce, pues, que el Señor tu Dios es Dios, el Dios fiel, que cumple su pacto y muestra su fiel amor por mil generaciones a quienes lo aman y obedecen sus mandamientos.", "reference": "Deuteronomio 7:9"},
     {"text": "Mi arco he puesto en las nubes, el cual será por señal del pacto entre mí y la tierra.", "reference": "Génesis 9:13"},
     {"text": "Y haré mi pacto contigo, y te multiplicaré en gran manera.", "reference": "Génesis 17:2"},
     {"text": "El Señor mismo va delante de ti y estará contigo; no te dejará ni te desamparará. No temas ni te intimides.", "reference": "Deuteronomio 31:8"},
     {"text": "Pero el amor leal del Señor es desde la eternidad y hasta la eternidad para los que le temen, y su justicia para los hijos de sus hijos; para los que guardan su pacto y se acuerdan de sus preceptos para ponerlos por obra.", "reference": "Salmos 103:17-18"},
     {"text": "Por eso, Cristo es mediador de un nuevo pacto, para que los llamados reciban la herencia eterna prometida, ahora que él ha muerto para liberarlos de los pecados cometidos bajo el primer pacto.", "reference": "Hebreos 9:15"},
     {"text": "Ahora, pues, si en verdad escuchan mi voz y guardan mi pacto, serán mi especial tesoro entre todos los pueblos, porque toda la tierra es mía.", "reference": "Éxodo 19:5"},
     {"text": "Y el Señor dijo a Moisés: Escribe tú estas palabras, porque conforme a estas palabras he hecho pacto contigo y con Israel.", "reference": "Éxodo 34:27"},
     {"text": "Porque aunque los montes se corran y las colinas se tambaleen, mi amor leal no se apartará de ti, ni mi pacto de paz será quebrantado —dice el Señor, que tiene compasión de ti—.", "reference": "Isaías 54:10"},
     {"text": "Pero ahora, a Jesús se le ha confiado un ministerio muy superior, pues él es el mediador que nos garantiza un pacto mejor, basado en mejores promesas.", "reference": "Hebreos 8:6"}
]

# Mensajes de bienvenida aleatorios
WELCOME_MESSAGES = [
    "¡Bienvenido {name} al Grupo del Seminario Evangélico Metodista Extensión Holguín! 🎓 Esperamos que las clases le sean de provecho para su edificación en Cristo.",
]

# Almacenamiento simple de usuarios suscritos (en producción usarías una base de datos)
subscribed_users = set()
# Almacenar la hora preferida de cada usuario
user_preferred_time = {}

class ClassBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.has_job_queue = hasattr(self.application, 'job_queue') and self.application.job_queue is not None
        self.setup_handlers()

    async def set_bot_commands(self):
        """Configurar los comandos del bot"""
        commands = [
            BotCommand("start", "🚀 Iniciar conversación con el Asistente Docente"),
            BotCommand("asignaturas", "📚 Ver lista de asignaturas"),
            BotCommand("bibliografia", "📖 Ver bibliografía"),
            BotCommand("normas", "📋 Ver normas del grupo"),
            BotCommand("promesa", "📖 Suscribirse a la promesa bíblica diaria"),
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
        self.application.add_handler(CommandHandler("promesa", self.promesa_diaria))
        self.application.add_handler(CommandHandler("help", self.help))

        # Handlers para botones interactivos
        self.application.add_handler(CallbackQueryHandler(self.subject_button, pattern="^subject_"))
        self.application.add_handler(CallbackQueryHandler(self.back_button, pattern="^back_to_"))
        self.application.add_handler(CallbackQueryHandler(self.promesa_button, pattern="^promesa_"))
        self.application.add_handler(CallbackQueryHandler(self.time_selection, pattern="^time_"))

        # ✅ MANEJADOR PARA NUEVOS MIEMBROS (BIENVENIDA AUTOMÁTICA)
        self.application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self.welcome_new_member
            )
        )
        
        # Programar la tarea diaria de enviar promesas bíblicas solo si JobQueue está disponible
        if self.has_job_queue:
            try:
                # Programar para cada hora del día para verificar las horas preferidas de los usuarios
                for hour in range(24):
                    self.application.job_queue.run_daily(
                        self.enviar_promesas_diarias,
                        time=time(hour=hour, minute=0, tzinfo=pytz.timezone('America/Havana')),
                        name=f"enviar_promesas_diarias_{hour}am"
                    )
                print("✅ JobQueue configurado correctamente para promesas diarias (cada hora)")
            except Exception as e:
                print(f"❌ Error configurando JobQueue: {e}")
                self.has_job_queue = False
        else:
            print("⚠️ JobQueue no disponible. Las promesas diarias no se enviarán automáticamente.")

    async def enviar_promesas_diarias(self, context: ContextTypes.DEFAULT_TYPE):
        """Enviar promesas bíblicas a todos los usuarios suscritos a la hora actual"""
        if not subscribed_users:
            print("⏰ No hay usuarios suscritos para enviar promesas bíblicas")
            return
            
        current_time = datetime.now(pytz.timezone('America/Havana'))
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        promesa = random.choice(BIBLE_PROMISES)
        mensaje = f"📖 Promesa Bíblica del Día:\n\n\"{promesa['text']}\"\n- {promesa['reference']}"
        
        for user_id in list(subscribed_users):
            try:
                # Verificar si es la hora preferida del usuario
                user_time = user_preferred_time.get(user_id, time(8, 0))  # Por defecto 8:00 AM
                
                # Solo enviar si es la hora programada por el usuario
                if user_time.hour == current_hour and user_time.minute == current_minute:
                    await context.bot.send_message(chat_id=user_id, text=mensaje)
                    print(f"✅ Promesa enviada a usuario {user_id} a las {user_time}")
            except Exception as e:
                print(f"❌ Error enviando promesa a usuario {user_id}: {e}")
                # Si el usuario ha bloqueado el bot, eliminarlo de la lista
                if "bot was blocked" in str(e).lower():
                    subscribed_users.discard(user_id)
                    print(f"⚠️ Usuario {user_id} eliminado de suscripciones (bloqueó el bot)")

    async def send_promise_now(self, user_id):
        """Enviar una promesa bíblica inmediatamente al usuario"""
        promesa = random.choice(BIBLE_PROMISES)
        mensaje = f"📖 Tu promesa bíblica de hoy:\n\n\"{promesa['text']}\"\n- {promesa['reference']}"
        
        try:
            await self.application.bot.send_message(chat_id=user_id, text=mensaje)
            print(f"✅ Promesa inmediata enviada a usuario {user_id}")
        except Exception as e:
            print(f"❌ Error enviando promesa inmediata a usuario {user_id}: {e}")

    async def promesa_diaria(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar el comando para suscribirse/desuscribirse a las promesas diarias"""
        user_id = update.effective_user.id
        
        # Si JobQueue no está disponible, informar al usuario
        if not self.has_job_queue:
            await update.message.reply_text(
                "⚠️ La función de promesas diarias automáticas no está disponible en este momento. "
                "Puedes usar /promesa para recibir una promesa bíblica inmediata."
            )
            return
        
        # Si el usuario ya está suscrito
        if user_id in subscribed_users:
            keyboard = [
                [InlineKeyboardButton("✅ Sí, mantener suscripción", callback_data="promesa_keep")],
                [InlineKeyboardButton("🕐 Cambiar hora de envío", callback_data="promesa_time")],
                [InlineKeyboardButton("❌ No, cancelar suscripción", callback_data="promesa_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            user_time = user_preferred_time.get(user_id, time(8, 0))
            await update.message.reply_text(
                f"📖 Ya estás suscrito a la Promesa Bíblica Diaria.\n\nActualmente recibes las promesas a las {user_time.strftime('%H:%M')}.\n\n¿Qué deseas hacer?",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("✅ Sí, suscribirme", callback_data="promesa_subscribe")],
                [InlineKeyboardButton("❌ No, gracias", callback_data="promesa_decline")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📖 ¿Te gustaría recibir una promesa bíblica cada día para fortalecer tu fe?\n\nPuedes cancelar en cualquier momento con /promesa",
                reply_markup=reply_markup
            )

    async def promesa_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar los botones de suscripción a promesas bíblicas"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        action = query.data.split("_")[1]
        
        if action == "subscribe":
            subscribed_users.add(user_id)
            # Establecer hora predeterminada si no existe
            if user_id not in user_preferred_time:
                user_preferred_time[user_id] = time(8, 0)  # 8:00 AM por defecto
            
            # Enviar promesa inmediata
            await self.send_promise_now(user_id)
            
            # Mostrar opciones para programar hora
            keyboard = [
                [InlineKeyboardButton("🕐 Programar hora de envío", callback_data="promesa_time")],
                [InlineKeyboardButton("✅ Mantener hora predeterminada (8:00 AM)", callback_data="promesa_keep")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "✅ ¡Te has suscrito a la Promesa Bíblica Diaria!\n\nCada día recibirás una promesa de la Palabra de Dios para fortalecer tu fe.\n\n¿Deseas programar una hora específica para recibir las promesas?",
                reply_markup=reply_markup
            )
            
        elif action == "decline":
            await query.edit_message_text("❌ No te preocupes. Si cambias de opinión, siempre puedes suscribirte después con el comando /promesa.")
            
        elif action == "keep":
            user_time = user_preferred_time.get(user_id, time(8, 0))
            await query.edit_message_text(f"✅ Perfecto, seguirás recibiendo la Promesa Bíblica Diaria a las {user_time.strftime('%H:%M')}. ¡Dios bendiga tu día!")
            
        elif action == "cancel":
            if user_id in subscribed_users:
                subscribed_users.remove(user_id)
            await query.edit_message_text("❌ Has cancelado tu suscripción a la Promesa Bíblica Diaria.\n\nSi cambias de opinión, siempre puedes volver a suscribirte con /promesa.")
            
        elif action == "time":
            # Mostrar opciones de hora
            keyboard = [
                [InlineKeyboardButton("6:00 AM", callback_data="time_6_0")],
                [InlineKeyboardButton("7:00 AM", callback_data="time_7_0")],
                [InlineKeyboardButton("8:00 AM", callback_data="time_8_0")],
                [InlineKeyboardButton("9:00 AM", callback_data="time_9_0")],
                [InlineKeyboardButton("10:00 AM", callback_data="time_10_0")],
                [InlineKeyboardButton("5:00 PM", callback_data="time_17_0")],
                [InlineKeyboardButton("6:00 PM", callback_data="time_18_0")],
                [InlineKeyboardButton("7:00 PM", callback_data="time_19_0")],
                [InlineKeyboardButton("8:00 PM", callback_data="time_20_0")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🕐 Selecciona la hora a la que prefieres recibir tu promesa bíblica diaria:",
                reply_markup=reply_markup
            )

    async def time_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar la selección de hora para las promesas bíblicas"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        # Extraer hora y minutos del callback_data (formato: time_H_M)
        _, hour_str, minute_str = query.data.split("_")
        hour = int(hour_str)
        minute = int(minute_str)
        
        # Guardar la preferencia del usuario
        user_preferred_time[user_id] = time(hour, minute)
        
        # Asegurarse de que el usuario está suscrito
        subscribed_users.add(user_id)
        
        await query.edit_message_text(
            f"✅ ¡Hora programada correctamente!\n\nA partir de ahora recibirás tu promesa bíblica diaria a las {hour:02d}:{minute:02d}.\n\n¡Dios bendiga tu día! 📖"
        )

    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """✅ Dar la bienvenida automática a nuevos miembros"""
        print("🔔 Evento de nuevo miembro detectado!")

        # Verificar que hay nuevos miembros
        if not update.message or not update.message.new_chat_members:
            return

        for new_member in update.message.new_chat_members:
            # ⚠️ Evitar saludar al propio bot u otros bots
            if new_member.is_bot:
                print(f"⚠️  Ignorando bot: {new_member.first_name}")
                continue

            print(f"🎓 Saludando nuevo estudiante: {new_member.first_name}")

            # Seleccionar mensaje de bienvenida aleatorio
            welcome_message = random.choice(WELCOME_MESSAGES).format(
                name=new_member.first_name
            )

            # Mensaje de bienvenida completo
            full_welcome = f"""
{welcome_message}

📋 Para comenzar:
• /asignaturas - Ver las materias
• /bibliografia - Ver las bibliografías
• /normas - Leer las reglas del grupo
• /promesa - Recibir promesas bíblicas diarias
• /help - Obtener ayuda

¡No dudes en preguntar si tienes dudas! 🤗
            """

            try:
                # Enviar mensaje de bienvenida al grupo
                await update.message.reply_text(full_welcome)
                print(f"✅ Bienvenida enviada a {new_member.first_name} en el grupo")
                
                # Enviar mensaje privado al nuevo miembro
                try:
                    # Crear botón para iniciar conversación privada
                    keyboard = [
                        [InlineKeyboardButton("🚀 Iniciar conversación privada", url=f"https://t.me/{context.bot.username}?start=start")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await context.bot.send_message(
                        chat_id=new_member.id,
                        text=f"👋 ¡Hola {new_member.first_name}! Soy el asistente del Seminario. Haz clic en el botón para iniciar una conversación privada conmigo donde podré ayudarte con información sobre las asignaturas, bibliografías y más.",
                        reply_markup=reply_markup
                    )
                    print(f"✅ Invitación a chat privado enviada a {new_member.first_name}")
                except Exception as e:
                    print(f"⚠️ No se pudo enviar mensaje privado a {new_member.first_name}: {e}")

            except Exception as e:
                print(f"❌ Error enviando bienvenida al grupo: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mensaje de bienvenida"""
        user = update.effective_user
        chat_type = update.effective_chat.type
        
        # Si el comando se ejecuta en un grupo (no en privado)
        if chat_type in ["group", "supergroup"]:
            # Crear botón para iniciar conversación privada
            keyboard = [
                [InlineKeyboardButton("🚀 Iniciar conversación privada", url=f"https://t.me/{context.bot.username}?start=start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = f"""
👋 ¡Hola {user.first_name}! 

Soy el Asistente Docente del Seminario Evangélico Metodista Extensión Holguín.

Para una mejor experiencia, te invito a iniciar una conversación privada conmigo haciendo clic en el botón de abajo.

¡Allí podré ayudarte con toda la información que necesites! 📚
            """
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        else:
            # Conversación privada
            welcome_text = f"""
👋 ¡Hola {user.first_name}! Bienvenido al Asistente Docente del Seminario Evangélico Metodista Extensión Holguín!

🎓 Esperamos que las clases le sean de provecho para su edificación en Cristo.

Puedo brindar información sobre:
📚 /asignaturas - Ver lista de asignaturas
📖 /bibliografia - Ver lista de bibliografía
📋 /normas - Ver reglas del grupo
📖 /promesa - Recibir promesas bíblicas diarias
❓ /help - Obtener ayuda

¡Espero que te sea útil!
            """
            await update.message.reply_text(welcome_text)
        
        # Configurar comandos después del start
        await self.set_bot_commands()

    async def list_subjects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar lista de asignaturas con botones interactivos"""
        # Si el comando se ejecuta en un grupo, sugerir conversación privada
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
            
        # Conversación privada - mostrar la lista completa
        keyboard = []
        for subject_id, subject_info in SUBJECTS.items():
            keyboard.append([InlineKeyboardButton(
                subject_info["name"],
                callback_data=f"subject_{subject_id}"
            )])
        
        # Agregar botón "Volver al inicio" al final
        keyboard.append([InlineKeyboardButton(
            "◀️ Volver al inicio", 
            callback_data="back_to_start"
        )])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📚 Lista de Asignaturas:\n\nSelecciona una asignatura para ver más detalles:",
            reply_markup=reply_markup
        )

    async def list_bibliografia(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar información de bibliografía con enlace directo y botón de regreso"""
        # Si el comando se ejecuta en un grupo, sugerir conversación privada
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
            
        # Conversación privada - mostrar la bibliografía completa
        print("📖 Comando /bibliografia ejecutado")
        bibliografia_text = """
📚 Bibliografía Recomendada:

🔗 Accede a toda la literatura aquí:
https://t.me/semholguincentro/40
        """
        
        # Crear teclado con botón de regreso al inicio
        keyboard = [
            [InlineKeyboardButton("◀️ Volver al inicio", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            bibliografia_text,
            reply_markup=reply_markup
        )

    async def subject_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar la selección de una asignatura"""
        query = update.callback_query
        await query.answer()

        # CORRECCIÓN: Unir todas las partes después de "subject_"
        subject_id = "_".join(query.data.split("_")[1:])

        print(f"🔍 Botón presionado: {query.data}")
        print(f"🔍 ID de asignatura extraído: {subject_id}")

        if subject_id in SUBJECTS:
            subject = SUBJECTS[subject_id]
            response_text = f"""
📖 **{subject['name']}**

🔗 Recursos: {subject['resources']}
            """
            print(f"✅ Asignatura encontrada: {subject['name']}")
            await query.edit_message_text(
                text=response_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Volver a asignaturas", callback_data="back_to_subjects")]
                ])
            )
        else:
            print(f"❌ Asignatura no encontrada: {subject_id}")
            print(f"📋 Asignaturas disponibles: {list(SUBJECTS.keys())}")
            await query.edit_message_text(
                text="❌ Lo siento, no se pudo encontrar la información de esta asignatura.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Volver a asignaturas", callback_data="back_to_subjects")]
                ])
            )

    async def back_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar botones de volver (tanto a asignaturas como al inicio)"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "back_to_start":
            # Volver al mensaje de inicio
            user = query.from_user
            welcome_text = f"""
👋 ¡Hola {user.first_name}! Bienvenido al Asistente Docente del Seminario Evangélico Metodista Extensión Holguín!

🎓 Esperamos que las clases le sean de provecho para su edificación en Cristo.

Puedo brindar información sobre:
📚 /asignaturas - Ver lista de asignaturas
📖 /bibliografia - Ver lista de bibliografía
📋 /normas - Ver reglas del grupo
📖 /promesa - Recibir promesas bíblicas diarias
❓ /help - Obtener ayuda

¡Espero que te sea útil!
            """
            await query.edit_message_text(welcome_text)
            
        else:  # back_to_subjects
            # Volver a la lista de asignaturas
            keyboard = []
            for subject_id, subject_info in SUBJECTS.items():
                keyboard.append([InlineKeyboardButton(
                    subject_info["name"],
                    callback_data=f"subject_{subject_id}"
                )])
            
            # Agregar botón "Volver al inicio" al final
            keyboard.append([InlineKeyboardButton(
                "◀️ Volver al inicio", 
                callback_data="back_to_start"
            )])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📚 **Lista de Asignaturas:**\n\nSelecciona una asignatura para ver más detalles:",
                reply_markup=reply_markup
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar mensaje de ayuda"""
        # Si el comando se ejecuta en un grupo, sugerir conversación privada
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
            
        # Conversación privada - mostrar la ayuda completa
        help_text = """
🤖 Bot de Gestión de Asignaturas

Comandos disponibles:
/start - Iniciar el bot
/asignaturas - Ver lista de asignaturas
/bibliografia - Ver bibliografía recomendada
/normas - Ver reglas del grupo
/promesa - Suscribirse a promesas bíblicas diarias
/help - Mostrar esta ayuda

Funcionalidades:
- Consultar información de asignaturas
- Recibir bienvenida automática al unirte
- Acceder a recursos de cada materia
- Recibir promesas bíblicas diarias
        """
        await update.message.reply_text(help_text)

    async def rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar normas del grupo"""
        # Si el comando se ejecuta en un grupo, sugerir conversación privada
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
            
        # Conversación privada - mostrar las normas completas
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

def main():
    """Función principal para Render"""
    # Obtener token de variable de entorno (para Render)
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN no encontrado en variables de entorno")
        print("💡 Asegúrate de configurar la variable BOT_TOKEN en Render")
        exit(1)

    print("🤖 Iniciando bot en Render...")
    print(f"📚 Total de asignaturas: {len(SUBJECTS)}")
    print(f"📖 Total de promesas bíblicas: {len(BIBLE_PROMISES)}")
    
    # Iniciar servidor Flask en segundo plano para health checks
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Servidor Flask iniciado para health checks (puerto 5000)")
    
    # Crear y ejecutar el bot
    bot = ClassBot(BOT_TOKEN)
    
    try:
        print("✅ Bot iniciado correctamente")
        print("📖 Comando /bibliografia incluye: https://t.me/semholguincentro/40")
        if bot.has_job_queue:
            print("📖 JobQueue disponible: Promesas bíblicas diarias activadas")
        else:
            print("⚠️ JobQueue no disponible: Promesas diarias desactivadas")
        
        bot.application.run_polling()
        
    except Exception as e:
        print(f"❌ Error: {e}")

# 🚀 EJECUCIÓN PARA RENDER
if __name__ == "__main__":

    main()
