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
  {"text": "Por eso, Cristo es mediador de un nuevo pacto, para que los llamados reciban la herencia eterna prometida, ahora que él ha muerto para liberarlos de los pecados cometidos bajo el primer pacto.", "reference": "Hebreos 9:15"},
  {"text": "Ahora, pues, si en verdad escuchan mi voz y guardan mi pacto, serán mi especial tesoro entre todos los pueblos, porque toda la tierra es mía.", "reference": "Éxodo 19:5"},
  {"text": "Y el Señor dijo a Moisés: Escribe tú estas palabras, porque conforme a estas palabras he hecho pacto contigo y con Israel.", "reference": "Éxodo 34:27"},
  {"text": "Porque aunque los montes se corran y las colinas se tambaleen, mi amor leal no se apartará de ti, ni mi pacto de paz será quebrantado —dice el Señor, que tiene compasión de ti—.", "reference": "Isaías 54:10"},
  {"text": "Pero ahora, a Jesús se le ha confiado un ministerio muy superior, pues él es el mediador que nos garantiza un pacto mejor, basado en mejores promesas.", "reference": "Hebreos 8:6"},
  {"text": "Por tanto, guarden los términos de este pacto y cúmplanlos, para que prosperen en todo lo que hagan.", "reference": "Deuteronomio 29:9"},
  {"text": "Ama al Señor tu Dios, obedece su voz, aférrate a él, porque él es tu vida y te dará muchos años en la tierra que juró dar a tus padres Abraham, Isaac y Jacob.", "reference": "Deuteronomio 30:20"},
  {"text": "De la misma manera, después de cenar, tomó la copa, diciendo: Esta copa es el nuevo pacto en mi sangre, que es derramada por ustedes.", "reference": "Lucas 22:20"},
  {"text": "Ese mismo día, Josué hizo un pacto con el pueblo y estableció para ellos decretos y leyes en Siquem.", "reference": "Josué 24:25"},
  {"text": "Y él les declaró su pacto, los Diez Mandamientos, que les mandó poner por obra, y los escribió en dos tablas de piedra.", "reference": "Deuteronomio 4:13"},
  {"text": "Ciertamente no es así con mi casa delante de Dios; sin embargo, él ha hecho conmigo un pacto eterno, ordenado en todo y seguro. Él es toda mi salvación y todo mi deseo, aunque todavía no haga que brote.", "reference": "2 Samuel 23:5"},
  {"text": "Yo establezco mi pacto con ustedes: Nunca más será exterminada toda carne por las aguas de un diluvio, ni habrá otro diluvio que destruya la tierra.", "reference": "Génesis 9:11"},
  {"text": "Y él estuvo allí con el Señor cuarenta días y cuarenta noches; no comió pan ni bebió agua. Y escribió en las tablas las palabras del pacto: los Diez Mandamientos.", "reference": "Éxodo 34:28"},
  {"text": "Del pacto que hizo con Abraham, y del juramento que hizo a Isaac.", "reference": "1 Crónicas 16:16"},
  {"text": "No violaré mi pacto, ni modificaré lo que ha salido de mis labios.", "reference": "Salmos 89:34"},
  {"text": "Y tomando la copa, y habiendo dado gracias, se la dio, diciendo: Beban de ella todos; porque esto es mi sangre del nuevo pacto, que es derramada por muchos para el perdón de los pecados.", "reference": "Mateo 26:27-28"},
  {"text": "Vienen días —declara el Señor— en que haré un nuevo pacto con la casa de Israel y con la casa de Judá.", "reference": "Jeremías 31:31"},
  {"text": "Se acordó para siempre de su pacto, de la palabra que ordenó para mil generaciones, del pacto que hizo con Abraham, y del juramento que hizo a Isaac.", "reference": "Salmos 105:8-9"},
  {"text": "Da alimento a los que le temen; se acuerda para siempre de su pacto.", "reference": "Salmos 111:5"},
  {"text": "En aquel tiempo haré un pacto para ellos con las bestias del campo, con las aves del cielo y con los reptiles de la tierra. Y quitaré de la tierra el arco, la espada y la guerra, y los haré dormir seguros.", "reference": "Oseas 2:18"},
  {"text": "Él da a conocer su palabra a Jacob, sus estatutos y sus juicios a Israel. No ha hecho así con ninguna otra nación; ellas no conocen sus juicios. ¡Aleluya!", "reference": "Salmos 147:19-20"},
  {"text": "Para hacer misericordia con nuestros padres, y acordarse de su santo pacto; del juramento que hizo a Abraham nuestro padre.", "reference": "Lucas 1:72-73"},
  {"text": "Pero yo me acordaré de mi pacto que hice contigo en los días de tu juventud, y estableceré contigo un pacto eterno.", "reference": "Ezequiel 16:60"},
  {"text": "Os haré pasar bajo la vara y os haré entrar en el vínculo del pacto.", "reference": "Ezequiel 20:37"},
  {"text": "Inclinen su oído y vengan a mí; escuchen, y vivirá su alma. Y haré con ustedes un pacto eterno, según las fieles misericordias mostradas a David.", "reference": "Isaías 55:3"},
  {"text": "Yo, el Señor, te he llamado en justicia, te sostendré por la mano, te guardaré y te pondré por pacto para el pueblo, por luz de las naciones.", "reference": "Isaías 42:6"},
  {"text": "Y haré con ellos un pacto de paz; será un pacto perpetuo con ellos. Los estableceré, los multiplicaré y pondré mi santuario entre ellos para siempre.", "reference": "Ezequiel 37:26"},
  {"text": "Mi pacto con él fue de vida y de paz, las cuales cosas yo le di para que me temiera; y tuvo temor de mí, y delante de mi nombre estuvo humillado.", "reference": "Malaquías 2:5"},
  {"text": "Por tanto, Jesús ha llegado a ser fiador de un mejor pacto.", "reference": "Hebreos 7:22"},
  {"text": "Entonces Moisés tomó la sangre y roció sobre el pueblo, y dijo: He aquí la sangre del pacto que el Señor ha hecho con ustedes conforme a todas estas palabras.", "reference": "Éxodo 24:8"},
  {"text": "Porque esto es mi sangre del nuevo pacto, que es derramada por muchos para el perdón de los pecados.", "reference": "Mateo 26:28"},
  {"text": "Y les dijo: Esto es mi sangre del nuevo pacto, que es derramada por muchos.", "reference": "Marcos 14:24"},
  {"text": "Ustedes son hijos de los profetas y del pacto que Dios hizo con nuestros padres, al decirle a Abraham: 'En tu simiente serán benditas todas las familias de la tierra'.", "reference": "Hechos 3:25"},
  {"text": "Y este será mi pacto con ellos, cuando yo quite sus pecados.", "reference": "Romanos 11:27"},
  {"text": "Asimismo tomó también la copa, después de haber cenado, diciendo: Esta copa es el nuevo pacto en mi sangre; hagan esto todas las veces que la beban, en memoria de mí.", "reference": "1 Corintios 11:25"},
  {"text": "Este es el pacto que haré con ellos después de aquellos días, dice el Señor: Pondré mis leyes en sus corazones, y en sus mentes las escribiré.", "reference": "Hebreos 10:16"},
  {"text": "En aquel día el Señor hizo un pacto con Abram, diciendo: A tu descendencia he dado esta tierra, desde el río de Egipto hasta el río grande, el río Éufrates.", "reference": "Génesis 15:18"},
  {"text": "Y estableceré mi pacto entre mí y ti, y tu descendencia después de ti, por sus generaciones, como pacto perpetuo, para ser tu Dios y el de tu descendencia después de ti.", "reference": "Génesis 17:7"},
  {"text": "Por tanto, los hijos de Israel guardarán el día de reposo, celebrándolo por sus generaciones como pacto perpetuo.", "reference": "Éxodo 31:16"},
  {"text": "Porque me volveré a ustedes, los haré fecundos y los multiplicaré, y afirmaré mi pacto con ustedes.", "reference": "Levítico 26:9"},
  {"text": "El Señor nuestro Dios hizo un pacto con nosotros en Horeb. No con nuestros padres hizo el Señor este pacto, sino con nosotros, todos los que estamos aquí hoy vivos.", "reference": "Deuteronomio 5:2-3"},
  {"text": "Junten ante mí a mis fieles, que hicieron pacto conmigo mediante sacrificio.", "reference": "Salmos 50:5"},
  {"text": "Para siempre le conservaré mi misericordia, y mi pacto será firme con él.", "reference": "Salmos 89:28"},
  {"text": "Lo estableció a Jacob por decreto, a Israel como pacto eterno.", "reference": "Salmos 105:10"},
  {"text": "La tierra fue profanada por sus habitantes, porque traspasaron las leyes, violaron los estatutos, quebrantaron el pacto eterno.", "reference": "Isaías 24:5"},
  {"text": "Este habitará en las alturas; fortaleza de rocas será su lugar de refugio; se le dará su pan, y sus aguas serán seguras.", "reference": "Isaías 33:16"},
  {"text": "Preguntarán por el camino a Sion, hacia donde volverán sus rostros, diciendo: Vengan, unámonos al Señor en pacto eterno que jamás será olvidado.", "reference": "Jeremías 50:5"},
  {"text": "Y estableceré con ellos un pacto de paz y eliminaré de la tierra las bestias feroces; y habitarán en el desierto con seguridad y dormirán en los bosques.", "reference": "Ezequiel 34:25"},
  {"text": "Y sabrán que yo les envié este mandamiento, para que mi pacto con Leví permaneciera —dice el Señor de los ejércitos—.", "reference": "Malaquías 2:4"},
  {"text": "Yo soy el pan vivo que descendió del cielo; si alguno come de este pan, vivirá para siempre; y el pan que yo daré es mi carne, la cual yo daré por la vida del mundo.", "reference": "Juan 6:51"},
  {"text": "Porque en el evangelio la justicia de Dios se revela por fe y para fe, como está escrito: Mas el justo por la fe vivirá.", "reference": "Romanos 1:17"},
  {"text": "que son israelitas, de los cuales son la adopción, la gloria, los pactos, la promulgación de la ley, el culto y las promesas.", "reference": "Romanos 9:4"},
  {"text": "porque el fin de la ley es Cristo, para justicia a todo aquel que cree.", "reference": "Romanos 10:4"},
  {"text": "Digo, pues: ¿Ha desechado Dios a su pueblo? ¡De ninguna manera!... Dios no ha desechado a su pueblo, al cual desde antes conoció.", "reference": "Romanos 11:1-2"},
  {"text": "Porque todas las promesas de Dios son 'sí' en él; y por medio de él, 'amén', para gloria de Dios por nosotros.", "reference": "2 Corintios 1:20"},
  {"text": "el cual asimismo nos hizo ministros competentes de un nuevo pacto, no de la letra, sino del Espíritu; porque la letra mata, mas el Espíritu vivifica.", "reference": "2 Corintios 3:6"},
  {"text": "Lo cual es una alegoría, pues estas mujeres son los dos pactos; el uno proviene del monte Sinaí, el cual da hijos para esclavitud; este es Agar.", "reference": "Gálatas 4:24"},
  {"text": "y por medio de él reconciliar consigo todas las cosas, así las que están en la tierra como las que están en los cielos, haciendo la paz mediante la sangre de su cruz.", "reference": "Colosenses 1:20"},
  {"text": "Porque donde hay testamento, es necesario que intervenga la muerte del testador. Porque el testamento con la muerte se confirma; pues no es válido entre tanto que el testador vive.", "reference": "Hebreos 9:16-17"},
  {"text": "Estará el arco en las nubes, y lo veré, y me acordaré del pacto perpetuo entre Dios y todo ser viviente, con toda carne que hay sobre la tierra.", "reference": "Génesis 9:16"},
  {"text": "Y te daré a ti, y a tu descendencia después de ti, la tierra en que moras, toda la tierra de Canaán en heredad perpetua; y seré el Dios de ellos.", "reference": "Génesis 17:8"},
  {"text": "Guardarán esto como estatuto para ustedes y para sus hijos para siempre.", "reference": "Éxodo 12:24"},
  {"text": "Y todo el pueblo respondió a una voz, y dijo: Todo lo que el Señor ha dicho, haremos. Y Moisés refirió al Señor las palabras del pueblo.", "reference": "Éxodo 19:8"},
  {"text": "Y aun con todo esto, estando ellos en tierra de sus enemigos, yo no los desecharé, ni los abominaré para consumirlos, invalidando mi pacto con ellos; porque yo soy el Señor su Dios.", "reference": "Levítico 26:44"},
  {"text": "Cuídense, no se olviden del pacto del Señor su Dios, que él estableció con ustedes, y no se hagan ídolo o imagen de ninguna cosa que el Señor tu Dios te ha prohibido. Porque el Señor tu Dios es fuego consumidor, Dios celoso.", "reference": "Deuteronomio 4:23-24"},
  {"text": "No por tu justicia, ni por la rectitud de tu corazón entras a poseer la tierra de ellos, sino por la impiedad de estas naciones el Señor tu Dios las arroja de delante de ti, y para confirmar la palabra que el Señor juró a tus padres Abraham, Isaac y Jacob.", "reference": "Deuteronomio 9:5"},
  {"text": "Si tus hijos guardaren mi pacto y mi testimonio que yo les enseñaré, sus hijos también se sentarán sobre tu trono para siempre.", "reference": "Salmos 132:12"},
  {"text": "Pero este es el pacto que haré con la casa de Israel después de aquellos días, dice el Señor: Pondré mi ley en su mente, y la escribiré en su corazón; y yo seré a ellos por Dios, y ellos me serán por pueblo.", "reference": "Jeremías 31:33"},
  {"text": "Y tú también por la sangre de tu pacto serás salva; yo he sacado tus presos de la cisterna en que no hay agua.", "reference": "Zacarías 9:11"},
  {"text": "Libro de la genealogía de Jesucristo, hijo de David, hijo de Abraham.", "reference": "Mateo 1:1"},
  {"text": "Y les digo que desde ahora no beberé más de este fruto de la vid, hasta aquel día en que lo beba nuevo con ustedes en el reino de mi Padre.", "reference": "Mateo 26:29"},
  {"text": "Para hacer misericordia con nuestros padres, y acordarse de su santo pacto.", "reference": "Lucas 1:72"},
  {"text": "Porque para ustedes es la promesa, y para sus hijos, y para todos los que están lejos; para cuantos el Señor nuestro Dios llame.", "reference": "Hechos 2:39"},
  {"text": "Justificados, pues, por la fe, tenemos paz para con Dios por medio de nuestro Señor Jesucristo.", "reference": "Romanos 5:1"},
  {"text": "Ahora bien, aun el primer pacto tenía ordenanzas de culto y un santuario terrenal.", "reference": "Hebreos 9:1"},
  {"text": "Y haré de ti una nación grande, te bendeciré y engrandeceré tu nombre, y serás bendición. Bendeciré a los que te bendijeren y a los que te maldijeren maldeciré; y serán benditas en ti todas las familias de la tierra.", "reference": "Génesis 12:2-3"},
  {"text": "Y tomó el libro del pacto y lo leyó a oídos del pueblo, el cual dijo: Haremos todas las cosas que el Señor ha dicho, y obedeceremos.", "reference": "Éxodo 24:7"},
  {"text": "Ustedes todos están hoy en presencia del Señor su Dios... para que entres en el pacto del Señor tu Dios, y en su juramento, que el Señor tu Dios concierta hoy contigo, a fin de confirmarte hoy como su pueblo, para que él te sea a ti por Dios... Y no solamente con ustedes hago yo este pacto y este juramento, sino con los que están aquí presentes hoy con nosotros delante del Señor nuestro Dios, y con los que no están aquí hoy con nosotros.", "reference": "Deuteronomio 29:10-15"},
  {"text": "Esfuérzate y sé valiente, porque tú repartirás a este pueblo por heredad la tierra que juré a sus padres que les daría. Solamente esfuérzate y sé muy valiente, para cuidar de hacer conforme a toda la ley que mi siervo Moisés te mandó... Nunca se apartará de tu boca este libro de la ley... porque entonces harás prosperar tu camino y todo te saldrá bien. Mira que te mando que te esfuerces y seas valiente; no temas ni desmayes, porque el Señor tu Dios estará contigo dondequiera que vayas.", "reference": "Josué 1:6-9"},
  {"text": "Pues sus corazones no eran rectos con él, ni estuvieron firmes en su pacto.", "reference": "Salmos 78:37"},
  {"text": "Redención ha enviado a su pueblo; para siempre ha ordenado su pacto; santo y temible es su nombre.", "reference": "Salmos 111:9"},
  {"text": "Judá vino a ser su santuario, e Israel su señorío.", "reference": "Salmos 114:2"},
  {"text": "Y este será mi pacto con ellos, dijo el Señor: Mi Espíritu que está sobre ti, y mis palabras que puse en tu boca, no faltarán de tu boca, ni de la boca de tus hijos, ni de la boca de los hijos de tus hijos, dijo el Señor, desde ahora y para siempre.", "reference": "Isaías 59:21"},
  {"text": "Palabra del Señor que vino a Jeremías, después que el rey Sedequías hizo pacto con todo el pueblo en Jerusalén para promulgarles libertad.", "reference": "Jeremías 34:8"},
  {"text": "Porque de cierto les digo que hasta que pasen el cielo y la tierra, ni una jota ni una tilde pasará de la ley, hasta que todo se haya cumplido.", "reference": "Mateo 5:18"},
  {"text": "Yo, pues, les asigno un reino, como mi Padre me lo asignó a mí, para que coman y beban a mi mesa en mi reino, y se sienten en tronos juzgando a las doce tribus de Israel.", "reference": "Lucas 22:29-30"},
  {"text": "Porque no por la ley fue dada a Abraham o a su descendencia la promesa de que sería heredero del mundo, sino por la justicia de la fe.", "reference": "Romanos 4:13"},
  {"text": "Así también está escrito: Fue hecho el primer hombre Adán alma viviente; el postrer Adán, espíritu vivificante.", "reference": "1 Corintios 15:45"},
  {"text": "De modo que si alguno está en Cristo, nueva criatura es; las cosas viejas pasaron; he aquí todas son hechas nuevas.", "reference": "2 Corintios 5:17"},
  {"text": "Y si ustedes son de Cristo, entonces son descendencia de Abraham, herederos según la promesa.", "reference": "Gálatas 3:29"},
  {"text": "que los gentiles son coherederos y miembros del mismo cuerpo, y copartícipes de la promesa en Cristo Jesús por medio del evangelio.", "reference": "Efesios 3:6"},
  {"text": "anulando el acta de los decretos que había contra nosotros, que nos era contraria, quitándola de en medio y clavándola en la cruz.", "reference": "Colosenses 2:14"},
  {"text": "Lazo es al hombre hacer apresuradamente voto de consagración, y después de hacerlo, reflexionar.", "reference": "Proverbios 20:25"},
  {"text": "Porque te extenderás a la mano derecha y a la mano izquierda; y tu descendencia heredará naciones, y habitará las ciudades asoladas.", "reference": "Isaías 54:3"},
  {"text": "Y a ti te daré las llaves del reino de los cielos; y todo lo que atares en la tierra será atado en los cielos; y todo lo que desatares en la tierra será desatado en los cielos.", "reference": "Mateo 16:19"},
  {"text": "Pues les digo, que Cristo Jesús vino a ser siervo de la circuncisión para mostrar la verdad de Dios, para confirmar las promesas hechas a los padres.", "reference": "Romanos 15:8"},
  {"text": "Lo cual es una alegoría, pues estas mujeres son los dos pactos; el uno proviene del monte Sinaí, el cual da hijos para esclavitud; este es Agar... Mas la Jerusalén de arriba, la cual es madre de todos nosotros, es libre.", "reference": "Gálatas 4:24-26"},
  {"text": "elegidos según la presciencia de Dios Padre en santificación del Espíritu, para obedecer y ser rociados con la sangre de Jesucristo: Gracia y paz os sean multiplicadas.", "reference": "1 Pedro 1:2"},
  {"text": "He aquí, yo envío mi mensajero, el cual preparará el camino delante de mí; y vendrá súbitamente a su templo el Señor a quien ustedes buscan, y el ángel del pacto, a quien desean. He aquí viene, ha dicho el Señor de los ejércitos.", "reference": "Malaquías 3:1"},
  {"text": "Socorrió a Israel su siervo, acordándose de la misericordia de la cual habló a nuestros padres, para con Abraham y su descendencia para siempre.", "reference": "Lucas 1:54-55"},
  {"text": "Pero ahora, aparte de la ley, se ha manifestado la justicia de Dios... la justicia de Dios por medio de la fe en Jesucristo, para todos los que creen en él. Porque no hay diferencia.", "reference": "Romanos 3:21-22"},
  {"text": "La copa de bendición que bendecimos, ¿no es la comunión de la sangre de Cristo? El pan que partimos, ¿no es la comunión del cuerpo de Cristo?", "reference": "1 Corintios 10:16"},
  {"text": "siendo manifiesto que sois carta de Cristo expedida por nosotros, escrita no con tinta, sino con el Espíritu del Dios vivo; no en tablas de piedra, sino en tablas de carne del corazón.", "reference": "2 Corintios 3:3"},
  {"text": "Así que ya no son extranjeros ni advenedizos, sino conciudadanos de los santos, y miembros de la familia de Dios.", "reference": "Efesios 2:19"},
  {"text": "enseñándoles que guarden todas las cosas que os he mandado; y he aquí yo estoy con vosotros todos los días, hasta el fin del mundo. Amén.", "reference": "Mateo 28:20"},
  {"text": "Mantengamos firme, sin fluctuar, la profesión de nuestra esperanza, porque fiel es el que prometió.", "reference": "Hebreos 10:23"},
  {"text": "Todas las sendas del Señor son misericordia y verdad para los que guardan su pacto y sus testimonios.", "reference": "Salmos 25:10"},
  {"text": "Acontecerá en aquel tiempo que la raíz de Isaí, la cual estará puesta por pendón a los pueblos, será buscada por las naciones; y su habitación será gloriosa.", "reference": "Isaías 11:10"},
  {"text": "a quien Dios puso como propiciación por medio de la fe en su sangre, para manifestar su justicia, a causa de haber pasado por alto, en su paciencia, los pecados pasados.", "reference": "Romanos 3:25"},
  {"text": "No ha hecho así con ninguna otra de las naciones; y en cuanto a sus juicios, no los conocieron. ¡Aleluya!", "reference": "Salmos 147:20"},
  {"text": "Ahora, pues, si en verdad escuchan mi voz y guardan mi pacto, serán mi especial tesoro entre todos los pueblos... Y ustedes me serán un reino de sacerdotes y una nación santa.", "reference": "Éxodo 19:5-6"},
  {"text": "Me postraré hacia tu santo templo, y alabaré tu nombre por tu misericordia y tu fidelidad; porque has engrandecido tu nombre, y tu palabra sobre todas las cosas.", "reference": "Salmos 138:2"},
  {"text": "Porque el Señor ama la justicia y no desampara a sus santos. Para siempre serán guardados; mas la descendencia de los impíos será destruida.", "reference": "Salmos 37:28"},
  {"text": "Porque cuando Dios hizo la promesa a Abraham, no pudiendo jurar por otro mayor, juró por sí mismo, diciendo: De cierto te bendeciré con abundancia y te multiplicaré grandemente.", "reference": "Hebreos 6:13-14"},
  {"text": "Por tanto, Jesús es hecho fiador de un mejor pacto. Y los otros sacerdotes llegaron a ser muchos, debido a que por la muerte no podían continuar; mas este, por cuanto permanece para siempre, tiene un sacerdocio inmutable.", "reference": "Hebreos 7:22-24"},
  {"text": "Pues les digo, que Cristo Jesús vino a ser siervo de la circuncisión para mostrar la verdad de Dios, para confirmar las promesas hechas a los padres, y para que los gentiles glorifiquen a Dios por su misericordia.", "reference": "Romanos 15:8-9"},
  {"text": "Mas ustedes son linaje escogido, real sacerdocio, nación santa, pueblo adquirido por Dios, para que anuncien las virtudes de aquel que los llamó de las tinieblas a su luz admirable.", "reference": "1 Pedro 2:9"}
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
                # Para la versión 20.x, programar de forma diferente
                job_queue = self.application.job_queue
                # Programar una verificación cada hora
                job_queue.run_repeating(
                    self.enviar_promesas_diarias,
                    interval=3600,  # cada hora (3600 segundos)
                    first=10
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
        print("🔍 Variables de entorno disponibles:")
        for key in os.environ.keys():
            if 'BOT' in key or 'TOKEN' in key:
                print(f"   {key} = {os.environ[key]}")
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