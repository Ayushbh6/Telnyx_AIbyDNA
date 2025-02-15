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
from openai.types.chat import ChatCompletionToolParam
from pipecat.frames.frames import TTSSpeakFrame

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


AI_by_DNA_greek = f"""
Ενδυναμώνουμε οργανισμούς με Agentic AI
AI by DNA – Ένας οργανισμός μετασχηματισμού μέσω Τεχνητής Νοημοσύνης που υποστηρίζει τις σύγχρονες επιχειρήσεις στην κλιμάκωση των δυνατοτήτων τους σε AI και Data, ενισχύοντας την αποδοτικότητα, την απόδοση και την ανάπτυξη.
Είμαστε ο αξιόπιστος συνεργάτης σας για να καθοδηγήσουμε τον AI μετασχηματισμό σας. Η ομάδα μας αποτελείται από data scientists, AI engineers, software developers, digital innovation και cross-market experts. Διαθέτουμε το δικό μας AI Factory, όπου πειραματιζόμαστε, αναπτύσσουμε και υλοποιούμε agentic λύσεις για εσάς.
Γνωσιακοί Βοηθοί - Knowledge Assistants
Στο σύγχρονο περιβάλλον, η γρήγορη πρόσβαση σε ακριβείς πληροφορίες και η δυνατότητα αξιόπιστης δράσης είναι καθοριστικοί παράγοντες για τη βελτίωση της αποδοτικότητας.
Μοναδική Εστίαση στην Εσωτερική Ανάκτηση Δεδομένων
Οι βοηθοί της AI by DNA εξειδικεύονται στην ανάκτηση εσωτερικών πληροφοριών, αντλώντας δεδομένα από πολλαπλές πηγές. Αυτό σημαίνει βελτιστοποιημένες ροές πληροφοριών, εξασφαλίζοντας ακρίβεια, αποδοτικότητα και ασφάλεια στη διαδικασία 
αναζήτησης, αναθεώρησης και περίληψης πληροφοριών.
Αυξήστε την αποδοτικότητα της επιχείρησής σας
Μειώστε τη χειρωνακτική εργασία
Βελτιώστε τις ροές εργασιών μέσω AI για αξιολόγηση, αναφορές & συμμόρφωση με κανονισμούς και πρότυπα
Συνομιλιακοί Πράκτορες (Conversational Agents)
Μετατρέπουμε τη φυσική γλώσσα στο νέο περιβάλλον διεπαφής με τα δεδομένα και το επιχειρηματικό σας περιεχόμενο. Οι AI-driven Συνομιλιακοί Πράκτορες προσφέρουν προσωποποιημένη, σε πραγματικό χρόνο και εις βάθος αλληλεπίδραση.
Ανακαλύψτε νέες δυνατότητες με το AI by Chat
Προσωποποιήστε, ενημερώστε, προτείνετε, προωθήστε και υποστηρίξτε
Αποκτήστε και διατηρήστε πελάτες
Απελευθερώστε τη δύναμη του AI by Phone
Οι ανθρωποκεντρικοί AI Voice Assistants μεταμορφώνουν τον τρόπο χρήσης των τηλεφωνικών γραμμών
Βελτιώστε τη διαθεσιμότητα επικοινωνίας, την πολυγλωσσική κάλυψη και την ικανοποίηση των πελατών
Επεκτείνετε τις δυνατότητες σας με το AI by Clone
Video-based agents που χρησιμοποιούν ανθρώπινα avatars
Αλληλεπιδρούν και συνομιλούν με τους πελάτες στο δικό σας γνωσιακό πλαίσιοΜεταμορφώστε την εμπειρία των phygital πελατών σας
Μηχανές Υποστήριξης Αποφάσεων - Decision Support Engines
Data Pipeline & Predictive Analytics για Στρατηγικές Επιλογές
Σε έναν κόσμο όπου τα δεδομένα οδηγούν την καινοτομία, οι δυνατότητες επεξεργασίας και ανάλυσης δεδομένων της AI by DNA σας βοηθούν να αποκτήσετε χρήσιμες, δράσιμες πληροφορίες από σύνθετα σύνολα δεδομένων.
Λήψη αποφάσεων βάσει δεδομένων σε πραγματικό χρόνο
Βελτιστοποίηση διαχείρισης πόρων
Συνολική διαχείριση αποθεμάτων
Δυναμική τιμολόγηση σε πραγματικό χρόνο
Ψάχνετε να αξιοποιήσετε προηγμένα γλωσσικά μοντέλα με βάση τα δεδομένα;
Χρειάζεστε προσαρμοσμένους AI πράκτορες με δυνατότητες ανάκτησης, ανάληψης δράσης ή πρόβλεψης, και άψογη ενσωμάτωση σε vector stores και άλλα εργαλεία;
Σχεδιάζουμε, αναπτύσσουμε και υλοποιούμε εξατομικευμένες λύσεις AI που εξυπηρετούν τους συγκεκριμένους επιχειρηματικούς σας στόχους.
Μετατρέψτε τα δεδομένα σας σε Δράσιμη Νοημοσύνη!
Testimonial
Γιώργος Κοτζαμάνης, Συνιδρυτής | Head of AI Factory
Προσθέστε το AI στο DNA της επιχείρησής σας
"Ζούμε σε μια εποχή μαζικής τεχνολογικής ανατροπής σε όλους τους τομείς εργασίας και ζωής. Ήμασταν προετοιμασμένοι γι' αυτό, εργαζόμαστε πάνω του, και τώρα είναι η στιγμή να επικεντρωθούμε σε αυτά που μπορούμε να επιτύχουμε για εσάς."
Κώστας Βαρσάμος, Συνιδρυτής | Managing Partner
AI για Προσωποποιημένη Εμπειρία Καταναλωτή
Βοηθός Αυτοεξυπηρέτησης
"Η AI by DNA φέρνει επανάσταση στον τρόπο επικοινωνίας των πληροφοριών προϊόντων στους πελάτες μας, μετατρέποντάς τις σε μια εμπειρία φυσικής συνομιλίας!"
Σπύρος Μπόκιας
Συνιδρυτής & CEO στην iPHARMA S.A.
Γραφεία: Ελλάδα (Αθήνα) | Γερμανία (Φρανκφούρτη)
Email: contact@aibydna.com
Copyright © 2024-2025 AIbyDNA.com – Όλα τα δικαιώματα διατηρούνται.
"""


async def run_bot(
    websocket_client,
    stream_id: str,
    outbound_encoding: str,
    inbound_encoding: str,
):
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_out_enabled=True,
            add_wav_header=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            vad_audio_passthrough=True,
            serializer=TelnyxFrameSerializer(stream_id, outbound_encoding, inbound_encoding),
        ),
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o", max_tokens=250, temperature=0.8)

    # REGISTER THE 'get_company_info' TOOL FUNCTION
    llm.register_function("get_company_info", get_company_info, start_callback=start_get_company_info)

    stt = OpenAISTTService(
        model="whisper-1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="IvVXvLXxiX8iXKrLlER8",
        model="eleven_turbo_v2_5",
        params=ElevenLabsTTSService.InputParams(
            stability=0.7,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True
        )
    )
    # UPDATED SYSTEM PROMPT (removed the appended company text)
    messages = [
        {
            "role": "system", 
            "content": (
                "Είσαι ο έξυπνος ψηφιακός βοηθός της AI by DNA. ΠΟΛΥ ΣΗΜΑΝΤΙΚΟ:\n\n"
                "ΠΡΕΠΕΙ ΠΑΝΤΑ να συστήνεσαι ως 'ο ψηφιακός βοηθός της AI by DNA' και να αναφέρεις ότι είσαι εδώ για να βοηθήσεις με πληροφορίες για την εταιρεία. Αυτό είναι ΥΠΟΧΡΕΩΤΙΚΟ σε κάθε πρώτη επαφή.\n\n"
                "Άλλες οδηγίες:\n"
                "1. Απαντήσεις: Σύντομες και φιλικές, 1-2 προτάσεις το μέγιστο\n"
                "2. Τόνος: Ζεστός και προσιτός\n"
                "3. Γλώσσα: Ελληνικά (εκτός αν ζητηθούν αγγλικά)\n"
                "4. Στυλ: Απλό και κατανοητό\n"
                "5. Λεπτομέρειες: Μοιράσου περισσότερες πληροφορίες μόνο αν ζητηθούν\n"
                "6. Μορφή: Απλό κείμενο χωρίς ειδικούς χαρακτήρες\n\n"
                "Για λεπτομέρειες σχετικά με την AI by DNA, καλό είναι να καλέσεις τη λειτουργία 'get_company_info'."
            ),
        },
    ]

    # ADD THE TOOL DEFINITION FOR THE COMPANY INFO
    tools = [
        ChatCompletionToolParam(
            type="function",
            function={
                "name": "get_company_info",
                "description": "Προσφέρει λεπτομέρειες για την AI by DNA, τις υπηρεσίες και τις επιδόσεις της.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
            },
        )
    ]
    # CREATE THE CONTEXT WITH BOTH MESSAGES AND TOOLS
    context = OpenAILLMContext(messages, tools)
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),  # Websocket input from client
            stt,  # Speech-To-Text
            context_aggregator.user(),
            llm,  # LLM with tool support!
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
        # Kick off the conversation with a cheerful welcome
        messages.append({"role": "system", "content": "Καλωσόρισες! Είμαι ο ψηφιακός βοηθός της AI by DNA. Είμαι εδώ για να σε βοηθήσω με οποιαδήποτε πληροφορία χρειάζεσαι σχετικά με την εταιρεία μας, τις υπηρεσίες και τις λύσεις μας. Πώς μπορώ να σε εξυπηρετήσω σήμερα;"})
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)

async def start_get_company_info(function_name, llm, context):
    # Execute silently without notifying the user.
    logger.debug(f"Silently executing get_company_info")

async def get_company_info(function_name, tool_call_id, args, llm, context, result_callback):
    # Return the AI_by_DNA_greek company information.
    await result_callback({"company_info": AI_by_DNA_greek})