import logging
import os
import hashlib
from typing import Optional, Dict

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

import boto3
from botocore.exceptions import BotoCoreError, ClientError

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_openai_client = OpenAI() if _OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") else None
_cloudwatch = boto3.client("cloudwatch")

METRICS_NAMESPACE = os.getenv("METRICS_NAMESPACE", "ComplimentsSkill")

def _put_metric(metric_name: str, dimensions: Optional[Dict[str, str]] = None, value: float = 1.0) -> None:
    dims = []
    if dimensions:
        for k, v in dimensions.items():
            dims.append({"Name": k, "Value": v})
    try:
        _cloudwatch.put_metric_data(
            Namespace=METRICS_NAMESPACE,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": dims,
                    "Value": value,
                    "Unit": "Count",
                }
            ],
        )
    except (BotoCoreError, ClientError) as e:
        logger.warning("CloudWatch metric failed: %s", e)

def _get_locale(handler_input: HandlerInput) -> str:
    try:
        return handler_input.request_envelope.request.locale or "en-US"
    except Exception:
        return "en-US"

def _ab_variant(handler_input: HandlerInput) -> str:
    forced = os.getenv("AB_FORCE_VARIANT")
    if forced in {"A", "B"}:
        return forced
    try:
        user_id = handler_input.request_envelope.context.system.user.user_id or "anon"
    except Exception:
        user_id = "anon"
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
    bucket = int(digest[:2], 16)  # 0..255
    return "A" if bucket < 128 else "B"

def generate_compliment(variant: str) -> str:
    fallback = "You're doing great — keep it up!"
    if _openai_client is None:
        logger.warning("OpenAI client unavailable or API key not set; using fallback compliment.")
        return fallback

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        system_prompt = (
            "You are a warm, upbeat compliment generator for a voice assistant. "
            "Return exactly one, family-friendly compliment, one sentence, 8–20 words, no emojis, no quotes."
            if variant == "A"
            else
            "You generate crisp, delightful compliments for voice. Exactly one sentence, 8–18 words, no emojis, no quotes, no lists. Vary tone subtly."
        )
        completion = _openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
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
        locale = _get_locale(handler_input)
        variant = _ab_variant(handler_input)
        compliment = generate_compliment(variant)
        _put_metric("SessionLaunch", {"Locale": locale, "Variant": variant})

        follow_rate = float(os.getenv("FOLLOWUP_RATE", "0"))
        if follow_rate > 0:
            # Deterministic prompt to reduce repeated asks: ask only on variant B
            if variant == "B":
                speak_output = f"{compliment} Want another?"
                reprompt = "Would you like another compliment?"
                return handler_input.response_builder.speak(speak_output).ask(reprompt).response
        return handler_input.response_builder.speak(compliment).response

class GetComplimentIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("GetComplimentIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        locale = _get_locale(handler_input)
        variant = _ab_variant(handler_input)
        compliment = generate_compliment(variant)
        _put_metric("ComplimentGenerated", {"Locale": locale, "Variant": variant})

        follow_rate = float(os.getenv("FOLLOWUP_RATE", "0"))
        if follow_rate > 0 and variant == "B":
            speak_output = f"{compliment} Want another?"
            reprompt = "Would you like another compliment?"
            return handler_input.response_builder.speak(speak_output).ask(reprompt).response
        return handler_input.response_builder.speak(compliment).response

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        locale = _get_locale(handler_input)
        variant = _ab_variant(handler_input)
        compliment = generate_compliment(variant)
        _put_metric("AnotherRequested", {"Locale": locale, "Variant": variant})
        # Keep session open for possible chains
        return handler_input.response_builder.speak(compliment + " Want another?").ask("Another one?").response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Optional[Response]:
        return handler_input.response_builder.speak("Okay! Come back anytime for a boost.").response

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
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

