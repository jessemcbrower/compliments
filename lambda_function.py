import logging
import os
from typing import Optional

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_openai_client = OpenAI() if _OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") else None

def generate_compliment() -> str:
    fallback = "You're doing great — keep it up!"
    if _openai_client is None:
        logger.warning("OpenAI client unavailable or API key not set; using fallback compliment.")
        return fallback

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        completion = _openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a warm, upbeat compliment generator for a voice assistant. "
                        "Return exactly one, family-friendly compliment, one sentence, 8–20 words, "
                        "no emojis, no quotes."
                    ),
                },
                {"role": "user", "content": "Give me a compliment."},
            ],
            temperature=0.9,
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "64")),
            timeout=8,
        )
        text = (completion.choices[0].message.content or "").strip()
        text = " ".join(text.split())
        return text or fallback
    except Exception as e:
        logger.error("OpenAI error: %s", e, exc_info=True)
        return fallback

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        compliment = generate_compliment()
        return handler_input.response_builder.speak(compliment).response

class GetComplimentIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("GetComplimentIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        compliment = generate_compliment()
        return handler_input.response_builder.speak(compliment).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        speak_output = "Say, give me a compliment."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        speak_output = "I can give you a compliment. Just say, give me a compliment."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
            or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        return handler_input.response_builder.speak("Goodbye! Have a great day!").response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return os.getenv("DEBUG_INTENT_REFLECTOR", "false").lower() == "true" and ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        intent_name = ask_utils.get_intent_name(handler_input)
        return handler_input.response_builder.speak(f"You just triggered {intent_name}.").response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Optional[Response]:
        logger.error("Unhandled exception: %s", exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetComplimentIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

