import json
import re
from typing import Optional, Dict, List
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion


class LLMError(Exception):
    pass


class LLMAPIError(LLMError):
    pass


class LLMClient:
    def __init__(
            self,
            api_key: str,
            base_url: str,
            default_model: str
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.default_model = default_model

    def chat_completion(
            self,
            messages: List[Dict[str, str]],
            model: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            stream: bool = False,
            **kwargs
    ) -> ChatCompletion:
        model = model or self.default_model
        try:
            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
        except Exception as e:
            raise LLMAPIError(f"API Error: {str(e)}") from e

    async def async_chat_completion(
            self,
            messages: List[Dict[str, str]],
            model: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            stream: bool = False,
            **kwargs
    ) -> ChatCompletion:
        model = model or self.default_model
        try:
            return await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
        except Exception as e:
            raise LLMAPIError(f"API Error: {str(e)}") from e


def extract_json(text: str) -> str:
    match = re.search(r'\{.*\}', text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in response:\n{text}")
    return match.group(0)



def main():
    deepseek = LLMClient(api_key="tpsg-7GOMHqSkUrXtv0XNxKE7Zj0Aof0WjoK", base_url="https://api.metisai.ir/openai/v1")

    with open("aggregated_azarbaijan_west.json", "r", encoding="utf-8") as f:
        inputs = json.load(f)

    results = []

    for idx, item in enumerate(inputs, start=1):
        messages = [
            {
                "role": "system",
                "content": """```
                You are a JSON transformation assistant. Your task is to read a given input JSON representing a recipe and output a new JSON with exactly the following structure:

                ```json
                {
                  "title": string,
                  "location": {
                    "province": string,
                    "city": string,
                    "coordinates": {
                      "latitude": number,
                      "longitude": number
                    }
                  },
                  "ingredients": [
                    {
                      "name": string,
                      "amount": number,
                      "unit": string
                    },
                    …
                  ],
                  "instructions": [
                    string,
                    …
                  ],
                  "meal_type": [ string, … ],
                  "occasion": [ string, … ],
                  "images": {
                    "final_image": string,
                    "step_1": string,
                    "step_2": string,
                    …
                  }
                }
                ```

                **Transformation rules:**
                1. **title**: copy from `input.title`.
                2. **location**: location.province: always set to "گیلان". if missing, set `city`, and `coordinates.latitude`/`longitude` to empty string or null.
                3. **ingredients**: each entry in `input.ingredients` is a string like `"گل نسترن: ۵۰۰ گرم"`.  
                   - Split on the first colon.  
                   - Parse the part before the colon as `name`.  
                   - From the part after the colon, extract the numeric amount (convert Persian/Latin digits to a number) as `amount`, and the remaining text as `unit`.  
                4. **instructions**: if `input.instructions` items are long paragraphs, split them into separate steps whenever you encounter a sentence boundary (e.g. “.” in Persian or line breaks). Trim whitespace.
                5. meal_type: infer one or more appropriate types (e.g. "غذای اصلی", "پیش‌غذا", "دسر", "دریایی") based on the nature of the dish; if you cannot determine, output an empty array.
                6. **Drop** any fields in the input that are not in the target schema (e.g. `url`).
                7. Ensure all keys are in English as shown, values in original language or numeric.
                8. "Respond **only** with valid JSON. "
                9. "Do not wrap it in markdown, do not add any extra text, "
                10. "and ensure there are no trailing commas or comments."
                11. occasion: infer suitable occasions (e.g. "ناهار", "شام", "مهمانی", "ویژه تعطیلات") from cultural context; if unclear, output an empty array.
                12. remove any extra keys: if the input JSON contains any keys not defined in the target schema above, drop them entirely.

                **Begin transformation.**  
                Here is the input JSON:  
                ```json
                {{INPUT_JSON}}
                ```  
                Please output only the transformed JSON.```
                """
            },
            {
                "role": "user",
                "content": "Here is the input JSON:\n```json\n" + json.dumps(item, ensure_ascii=False) + "\n```"
            }
        ]

        response = deepseek.chat_completion(
            messages=messages,
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=1500)

        output_file = "output_azarbaijan_west.json"
        content = response.choices[0].message.content.strip()

        json_str = extract_json(content)

        print(idx, content)

        transformed = json.loads(json_str)
        results.append(transformed)

    with open("transformed_aggregated.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()