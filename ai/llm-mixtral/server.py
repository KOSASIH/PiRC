# Mixtral 8x7B - 46B params local inference
from vllm import LLM, SamplingParams
import torch

llm = LLM(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    tensor_parallel_size=torch.cuda.device_count(),
    gpu_memory_utilization=0.95
)

prompts = [
    "Analyze Pi Network price action and recommend trade.",
    "What's the optimal Pi/BTC allocation ratio?"
]

sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=512)
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"🤖 {output.outputs[0].text}")
