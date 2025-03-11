import logging
import os
import tiktoken
from litellm import acompletion

from deep_research.utils.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Initialize the encoder.
try:
    encoder = tiktoken.get_encoding("o200k_base")
except Exception:
    encoder = tiktoken.get_encoding("cl100k_base")

async def generate_object(model, system, prompt, schema):
    response = None
    try:
        response = await acompletion(
            model=model,
            response_format=schema,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": prompt.strip()}],
            #temperature=self.temperature,
            #max_tokens=300,
        )
        result = response.choices[0].message["content"].strip()
        logger.info(f"LLM response: {result}")
        return result
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}\n {response}")
        raise e


def trim_prompt(prompt: str, context_size: int = None) -> str:
    if context_size is None:
        context_size = int(os.environ.get("CONTEXT_SIZE", 128000))
    if not prompt:
        return ""
    tokenized = encoder.encode(prompt)
    length = len(tokenized)
    if length <= context_size:
        return prompt
    overflow_tokens = length - context_size
    # Rough estimate: average 3 characters per token.
    chunk_size = len(prompt) - overflow_tokens * 3
    MinChunkSize = 140
    if chunk_size < MinChunkSize:
        return prompt[:MinChunkSize]
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)
    splits = splitter.split_text(prompt)
    trimmed_prompt = splits[0] if splits else ""
    if len(trimmed_prompt) == len(prompt):
        return trim_prompt(prompt[:chunk_size], context_size)
    return trim_prompt(trimmed_prompt, context_size)
