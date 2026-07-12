import os
import json
import re
import requests
from google import genai
from google.genai import types
from .prompt import Prompt, SYSTEM_PROMPT
import re
from json_repair import repair_json
from .alert_parser import normalize_url


class LLM_Client:
    MODEL = "gemini-3.5-flash"

    _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    @classmethod
    def parse(cls, event: dict, encode_entity: dict):
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.1
        )

        user_content = Prompt.event_to_prompt(event)

        response = cls._client.models.generate_content(
            model=cls.MODEL,
            contents=user_content,
            config=config
        )
        
        events = response.text
        print(f"LLM respone: {events}")
        for key, value in encode_entity.items():
            events = events.replace(key, normalize_url(value))
        return json.loads(repair_json(events))
