import os
import json
import time
from dotenv import load_dotenv
load_dotenv()

from typing import Tuple
import google.generativeai as genai
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM

api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

model_actor = genai.GenerativeModel("gemini-2.5-flash-lite")
model_evaluator = genai.GenerativeModel("gemini-2.5-flash-lite")
model_reflector = genai.GenerativeModel("gemini-2.5-flash-lite")

FAILURE_MODE_BY_QID = {}

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> Tuple[str, int, int]:
    start_time = time.time()
    context_str = "\n".join([f"{c.title}: {c.text}" for c in example.context])
    prompt = f"{ACTOR_SYSTEM}\n\nQUESTION: {example.question}\n\nCONTEXT:\n{context_str}\n"
    if reflection_memory:
        prompt += f"\nREFLECTION MEMORY:\n" + "\n".join(reflection_memory)
        
    try:
        response = model_actor.generate_content(prompt)
        answer = response.text.strip()
        tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
    except Exception as e:
        print(f"Actor Error: {e}")
        answer = "Error generating answer."
        tokens = 0
        
    latency = int((time.time() - start_time) * 1000)
    return answer, tokens, latency

def evaluator(example: QAExample, answer: str) -> Tuple[JudgeResult, int, int]:
    start_time = time.time()
    prompt = f"{EVALUATOR_SYSTEM}\n\nQUESTION: {example.question}\nGOLD ANSWER: {example.gold_answer}\nPREDICTED ANSWER: {answer}"
    try:
        response = model_evaluator.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        judge = JudgeResult(**data)
        tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
    except Exception as e:
        print(f"Evaluator Error: {e}")
        judge = JudgeResult(score=0, reason="Error during evaluation.")
        tokens = 0
        
    latency = int((time.time() - start_time) * 1000)
    return judge, tokens, latency

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> Tuple[ReflectionEntry, int, int]:
    start_time = time.time()
    context_str = "\n".join([f"{c.title}: {c.text}" for c in example.context])
    prompt = f"{REFLECTOR_SYSTEM}\n\nQUESTION: {example.question}\nCONTEXT:\n{context_str}\nPREDICTED ANSWER: {judge.reason}\nEVALUATOR REASON: {judge.reason}\nATTEMPT ID: {attempt_id}"
    try:
        response = model_reflector.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        data = json.loads(response.text)
        data["attempt_id"] = attempt_id
        ref_entry = ReflectionEntry(**data)
        tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0
    except Exception as e:
        print(f"Reflector Error: {e}")
        ref_entry = ReflectionEntry(attempt_id=attempt_id, failure_reason="Error", lesson="Error", next_strategy="Try again.")
        tokens = 0
        
    latency = int((time.time() - start_time) * 1000)
    return ref_entry, tokens, latency
