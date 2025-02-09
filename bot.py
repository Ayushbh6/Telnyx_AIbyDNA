#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os
import sys

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.telnyx import TelnyxFrameSerializer
from pipecat.services.openai import OpenAISTTService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from pipecat.audio.mixers.soundfile_mixer import SoundfileMixer

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


AI_by_DNA_greek = f"""
Ενδυνάμωση οργανισμών με Ενσυνείδητη Τεχνητή Νοημοσύνη (Agentic AI)

Η AI by DNA είναι ένας οργανισμός μετασχηματισμού Τεχνητής Νοημοσύνης που υποστηρίζει φιλόδοξους οργανισμούς να κλιμακώσουν τις δυνατότητες ΤΝ και Δεδομένων τους, ενισχύοντας την αποδοτικότητα, την απόδοση και την ανάπτυξη.

Είμαστε ο αξιόπιστος συνεργάτης σας για να σας καθοδηγήσουμε στον μετασχηματισμό της ΤΝ. Είμαστε ουδέτεροι και θα συνθέσουμε την καλύτερη λύση για τις ανάγκες σας. Αν δεν υπάρχει, θα την δημιουργήσουμε για εσάς.

Συνομιλιακός Πράκτορας
Φαρμακευτική Φροντίδα
«Η AI by DNA έχει επαναπροσδιορίσει τον τρόπο με τον οποίο τα πικτογράμματα μας επικοινωνούν πληροφορίες στους ασθενείς, μετατρέποντάς τα σε μια εμπειρία συνομιλίας σε φυσική γλώσσα για εκείνους!!!»
Σοφία Δημαγού (Piktocare | GET2WORK)

Συνομιλιακοί Πράκτορες
Οι συνομιλίες είναι οι νέες αγορές. Οι συνομιλιακοί πράκτορες που βασίζονται στην ΤΝ παρέχουν εξατομικευμένη, σε πραγματικό χρόνο και σε βάθος αλληλεπίδραση.
Αποκαλύψτε νέες ευκαιρίες με AI by Chat: Με το AI by Chat μπορείτε να υποστηρίξετε αντιδραστικά και να προτείνετε ανά πάσα στιγμή τα προϊόντα και τις υπηρεσίες σας. Μπορείτε να προωθήσετε προληπτικά, να κερδίσετε και να διατηρήσετε πελάτες.
Ξεκλειδώστε τη δύναμη του AI by Phone: Οι ανθρωποειδείς φωνητικοί βοηθοί ΤΝ αλλάζουν ριζικά τον τρόπο με τον οποίο οι επιχειρήσεις χρησιμοποιούν τις τηλεφωνικές γραμμές τους. Βελτιώστε την παραγωγικότητα, την αποδοτικότητα και την ικανοποίηση των πελατών.
Κλιμακώστε τις δυνατότητές σας με το AI by Clone: Ένας βίντεο-πράκτορας, που παρουσιάζει ένα ανθρωποειδές avatar, συνομιλεί με ανθρώπους μέσα σε ένα συγκεκριμένο πλαίσιο γνώσης, μέσω ήχου και σε πολλές γλώσσες. Μεταμορφώστε την εμπειρία των πελατών σας.

Βοηθοί Γνώσης
Στον γρήγορο ρυθμό του σήμερα, η γρήγορη πρόσβαση σε ακριβείς πληροφορίες και η αξιόπιστη λήψη δράσεων είναι κλειδιά για την ενίσχυση της αποδοτικότητας.
Μοναδική Εστίαση στην Ανάκτηση Εσωτερικών Δεδομένων: Οι βοηθοί της AI by DNA εστιάζουν στην ανάκτηση εσωτερικών πληροφοριών, αντλώντας απρόσκοπτα από πολύπλοκες πηγές, για να δημιουργήσουν τις δικές σας μηχανές αναζήτησης βασισμένες σε γνώση.
Αυτό σημαίνει ασφαλείς διαδικασίες, βελτιωμένες ροές πληροφοριών και εργασίας, δηλαδή πιο ακριβείς, αποδοτικές και βελτιωμένες διαδικασίες.
Βελτιώστε την αποδοτικότητα στη ρύθμιση και συμμόρφωση, τη διαχείριση αποθεμάτων και τη λειτουργία.

Μηχανές Αποφάσεων
Επεξεργασία Δεδομένων & Προγνωστική Ανάλυση για Διορατικές Λύσεις: Οδηγεί την καινοτομία, η AI by DNA εξάγει πληροφορίες από πολύπλοκα σύνολα δεδομένων. Οι δυνατότητες ανάλυσης δεδομένων σας δίνουν τη δυνατότητα να εξάγετε δράσιμες πληροφορίες.
Βελτιώστε τη λήψη αποφάσεων, τη λειτουργική και εμπορική απόδοση.
Λήψη αποφάσεων σε πραγματικό χρόνο με βάση τα δεδομένα: Η AI by DNA παρέχει πληροφορίες που βοηθούν στα εργαλεία κατανομής πόρων σε πραγματικό χρόνο, προσφέροντας βελτιστοποίηση, ολοκληρωμένη διαχείριση εσόδων και δυναμική τιμολόγηση.

«Ψάχνετε να αξιοποιήσετε τη δύναμη των προηγμένων γλωσσικών μοντέλων με μια βάση σε πληροφορίες που βασίζονται σε δεδομένα; Χρειάζεστε έναν προσαρμοσμένο πράκτορα με προγνωστική ανάλυση, δυνατότητες ανάκτησης και απρόσκοπτη ενσωμάτωση με αποθηκευτικούς χώρους διανυσμάτων και άλλα εργαλεία; Είμαστε εδώ για να σχεδιάσουμε, να αναπτύξουμε και να αναπτύξουμε προσαρμοσμένες λύσεις που ανταποκρίνονται στους συγκεκριμένους επιχειρηματικούς σας στόχους. Αφήστε μας να μετατρέψουμε τα δεδομένα και το πλαίσιο σας σε δράσιμη νοημοσύνη.»
Γιώργος Κοτζαμανής, Συνιδρυτής | Chief Operating Officer

Επικοινωνήστε με την «AI by DNA» σήμερα.
«Ζούμε σε μια εποχή μαζικής τεχνολογικής διαταραχής σε σχεδόν όλους τους τομείς της εργασίας και της ζωής. Ετοιμαζόμασταν για αυτό, δουλεύουμε πάνω σε αυτό, αλλά τώρα είναι η ώρα να εστιάσουμε στο τι μπορούμε να πετύχουμε για εσάς.» - Κώστας Βαρσάμος, Συνιδρυτής | CEO

Γραφεία: Ελλάδα (Αθήνα) | Γερμανία (Φρανκφούρτη) - Email: contact@aibydna.com
"""


async def run_bot(
    websocket_client,
    stream_id: str,
    outbound_encoding: str,
    inbound_encoding: str,
):
    # Create soundfile mixer for office ambience
    soundfile_mixer = SoundfileMixer(
        sound_files={"office": "assets/office_ambience.mp3"},  # Using relative path
        default_sound="office",
        volume=2.0,
    )

    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_out_enabled=True,
            audio_out_mixer=soundfile_mixer,  # Add the mixer here
            add_wav_header=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            vad_audio_passthrough=True,
            serializer=TelnyxFrameSerializer(stream_id, outbound_encoding, inbound_encoding),
        ),
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

    stt = OpenAISTTService(
        model="whisper-1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="Xp5npDqAjtdG3QS7EahZ",
    )

    messages = [
        {
            "role": "system",
            "content": "Είσαι ο προσωπικός βοηθός της AI by DNA, μια εταιρεία μετασχηματισμού Τεχνητής Νοημοσύνης. Είσαι εδώ για να βοηθήσεις τους χρήστες με πληροφορίες σχετικά με τις υπηρεσίες και τη λειτουργία της εταιρείας. Οι κύριες υπηρεσίες μας περιλαμβάνουν: Συνομιλιακούς Πράκτορες (AI by Chat, AI by Phone, AI by Clone), Βοηθούς Γνώσης, και Μηχανές Αποφάσεων. Να είσαι φιλικός, επαγγελματικός και να απαντάς μόνο στις ερωτήσεις που σου γίνονται. Να μιλάς πάντα στα ελληνικά εκτός αν ο χρήστης ζητήσει αγγλικά. Να παρουσιάζεις πάντα την εταιρεία με θετικό τρόπο. Οι απαντήσεις σου θα μετατραπούν σε ήχο, οπότε απόφυγε τη χρήση ειδικών χαρακτήρων.\n\nΕπίσημες πληροφορίες της εταιρείας:\n" + AI_by_DNA_greek,
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),  # Websocket input from client
            stt,  # Speech-To-Text
            context_aggregator.user(),
            llm,  # LLM
            tts,  # Text-To-Speech
            transport.output(),  # Websocket output to client
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            #audio_in_sample_rate=8000,
            #audio_out_sample_rate=8000,
            allow_interruptions=False,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        # Kick off the conversation.
        messages.append({"role": "system", "content": "Παρακαλώ συστήσου στον χρήστη."})
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)