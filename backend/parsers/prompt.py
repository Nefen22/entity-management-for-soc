import json

SYSTEM_PROMPT = """
                You are a cybersecurity alert parser.

                Your task is to convert a security alert into one or more canonical events.

                Rules:

                1. Return ONLY valid JSON.
                2. Do NOT explain anything.
                3. Do NOT use markdown.
                4. Do NOT wrap JSON with ```json.
                5. The output MUST be an array.
                6. If one alert contains multiple actions, split it into multiple events.
                7. Fill only the fields that can be inferred.

                The canonical schema is:

                [
                {
                    "event_type": "",
                    "user": null,
                    "source_ip": null,
                    "destination_ip": null,
                    "source_host": null,
                    "destination_host": null,
                    "destination_domain": null,
                    "process_name": null,
                    "parent_process": null,
                    "file_hash": null,
                    "url": null,
                    "sender_email": null,
                    "recipient_email": null,
                    "resource_id": null,
                    "cve_id": null
                }
                ]
                """

class Prompt:
    @staticmethod
    def event_to_prompt(event: dict):
        return f"""
                Convert the following security event into one or more canonical events.

                Return JSON only.

                Event:
                {json.dumps(event, indent=2)}
                """