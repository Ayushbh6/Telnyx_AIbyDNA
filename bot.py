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
from pipecat.audio.mixers.soundfile_mixer import SoundfileMixer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.telnyx import TelnyxFrameSerializer
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from openai.types.chat import ChatCompletionToolParam
from pipecat.frames.frames import Frame, TTSSpeakFrame, MixerEnableFrame


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
    
    # More robust path resolution for the audio file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    background_noise_path = os.path.join(current_dir, "static", "office-ambience.mp3")
    
    # Add debug logging
    logger.debug(f"Loading background noise from: {background_noise_path}")
    if not os.path.exists(background_noise_path):
        logger.error(f"Background noise file not found at: {background_noise_path}")
        raise FileNotFoundError(f"Background noise file not found at: {background_noise_path}")
    
    soundfile_mixer = SoundfileMixer(
        sound_files={"office": background_noise_path},
        default_sound="office",
        volume=2.0,
    )
    
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_out_enabled=True,
            audio_out_mixer=soundfile_mixer,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            vad_audio_passthrough=True,
            serializer=TelnyxFrameSerializer(stream_id, outbound_encoding, inbound_encoding),
        ),
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o", max_tokens=250, temperature=0.8)

    # REGISTER THE 'get_company_info' TOOL FUNCTION
    llm.register_function("get_company_info", get_company_info, start_callback=start_get_company_info)

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2",
        smart_format=True,
        diarize=True,
        utterances=True,
        utterances_vad=True,
        utterances_vad_threshold=0.5,
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
                "Είσαι ο 'AIby DNA Assistant', ο επίσημος ψηφιακός βοηθός της AI by DNA. Πάντα πρέπει να παρουσιάζεσαι ως 'AIby DNA Assistant' και να αναφέρεις ότι είσαι εδώ για να παρέχεις σύντομες, κατανοητές και φιλικές πληροφορίες για την εταιρεία μας, τις υπηρεσίες και τις λύσεις της. Ξεκίνα κάθε συνομιλία στα Ελληνικά, προσαρμόζοντας σε Αγγλικά μόνο αν ο χρήστης το ζητήσει ρητά. Οι απαντήσεις σου πρέπει να είναι 1-2 σύντομες προτάσεις, με ζεστό, ενθουσιώδη και προσιτό τόνο. Για λεπτομέρειες σχετικά με την AI by DNA, χρησιμοποίησε τη λειτουργία 'get_company_info'."
            ),
        },
    ]

    # ADD THE TOOL DEFINITION FOR THE COMPANY INFO
    tools = [
        ChatCompletionToolParam(
            type="function",
            function={
                "name": "get_company_info",
                "description": "Προσφέρει λεπτομέρειες για την AI by DNA, τις υπηρεσίες και τις λύσεις της, με έμφαση στην καινοτομία, την αξιοπιστία και τη φιλική εξυπηρέτηση.",
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
            allow_interruptions=False,
            enable_metrics=True,
            enable_usage_metrics=True,
            report_only_initial_ttfb=True,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        # Enable the background noise mixer
        await task.queue_frame(MixerEnableFrame(True))
        # Kick off the conversation with a cheerful welcome
        messages.append({
            "role": "system",
            "content": "Χαίρετε! Είμαι ο 'AIby DNA Assistant', ο επίσημος ψηφιακός βοηθός της AI by DNA, έτοιμος να σας παρέχω σύντομες και φιλικές πληροφορίες για την εταιρεία μας. Πώς μπορώ να σας εξυπηρετήσω σήμερα;"
        })
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