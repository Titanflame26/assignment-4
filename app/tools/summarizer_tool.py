import os
import json
import aiohttp
from typing import Tuple, Optional

from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# ===================================================
#   Pydantic Structured Output Schema
# ===================================================

class SummaryOutput(BaseModel):
    summary: str
    key_points: list[str]


class SummarizerError(Exception):
    """Raised when summarization fails."""
    pass


# ===================================================
#   Summarizer Tool
# ===================================================

class SummarizerTool:
    """
    Summarizer using:
    - Primary: Google Gemini (google-generativeai)
    - Fallback: Ollama local models

    Returns:
        summary: str
        key_points: List[str]
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        self.gemini_client = None
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_client = genai
            except Exception:
                self.gemini_client = None

    # --------------------------------------------------------------
    # PUBLIC SUMMARIZATION ENTRYPOINT
    # --------------------------------------------------------------
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type((SummarizerError, aiohttp.ClientError)),
    )
    async def summarize(self, text: str) -> Tuple[str, list]:
        """
        Returns summary and key points.
        """

        # Try Gemini first
        if self.gemini_client:
            try:
                parsed = await self._summarize_gemini(text)
                if parsed:
                    return parsed.summary, parsed.key_points
            except Exception:
                pass  # fallback to Ollama

        # Fallback to Ollama
        parsed = await self._summarize_ollama(text)
        return parsed.summary, parsed.key_points

    # --------------------------------------------------------------
    # GEMINI SUMMARIZATION
    # --------------------------------------------------------------
    async def _summarize_gemini(self, text: str) -> Optional[SummaryOutput]:
        """
        Uses Google Gemini to produce structured JSON output.
        """

        try:
            model = self.gemini_client.GenerativeModel("gemini-pro")

            prompt = f"""
            Summarize the following text in 120–200 words and provide 4–7 key bullet points.
            
            Return ONLY valid JSON strictly matching this schema:
            
            {{
              "summary": "string",
              "key_points": ["point1", "point2", "point3"]
            }}
            
            Text:
            {text}
            """

            response = model.generate_content(prompt)

            if not response or not response.text:
                raise SummarizerError("Gemini returned empty response.")

            json_data = self._extract_json(response.text)
            if not json_data:
                raise SummarizerError("Gemini returned invalid JSON.")

            # Pydantic validation — strong type checking
            return SummaryOutput.model_validate(json_data)

        except (ValidationError, Exception) as e:
            raise SummarizerError(f"Gemini summarization failed: {e}")

    # --------------------------------------------------------------
    # OLLAMA FALLBACK
    # --------------------------------------------------------------
    async def _summarize_ollama(self, text: str) -> SummaryOutput:
        """
        Local fallback summarization using Ollama (llama3).
        """

        prompt = f"""
        Summarize the following text in ~150 words and list 4-7 key points.

        Return ONLY valid JSON matching:
        
        {{
          "summary": "string",
          "key_points": ["...", "..."]
        }}

        Text:
        {text}
        """

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt},
                timeout=60,
            ) as resp:
                if resp.status != 200:
                    raise SummarizerError(f"Ollama request failed: HTTP {resp.status}")

                data = await resp.json()
                raw_text = data.get("response") or data

        json_data = self._extract_json(raw_text)
        if not json_data:
            raise SummarizerError("Ollama returned invalid JSON.")

        return SummaryOutput.model_validate(json_data)

    # --------------------------------------------------------------
    # JSON Extractor (Robust)
    # --------------------------------------------------------------
    def _extract_json(self, text: str) -> Optional[dict]:
        """
        Extracts JSON object from LLM text (handles cases where LLM adds text around JSON).
        """
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start == -1 or end == -1:
                return None
            return json.loads(text[start:end])
        except Exception:
            return None
