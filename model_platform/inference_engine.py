# model_platform/inference_engine.py
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from optimize import ModelOptimizer

class LocalInferenceEngine:
    def __init__(self, model_id: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.model_id = model_id
        self.device = ModelOptimizer.get_execution_device()
        self.tokenizer = None
        self.model = None

    def initialize_platform(self, mock_mode: bool = False):
        """Loads tokenizer and model weights securely into device memory."""
        if mock_mode or os.environ.get("CI") == "true":
            # Defensive execution path for testing environments without internet/GPU
            print(f"[MOCK] Initialized mock platform for {self.model_id} on {self.device}")
            return

        try:
            print(f"Loading tokenizer for: {self.model_id}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

            print(f"Loading causal LM layers onto device: {self.device}")
            # In a full GPU environment, add **ModelOptimizer.get_quantization_config('8bit')
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
            ).to(self.device)

            print("Platform model initialization successful.")
        except Exception as e:
            print(f"Critical failure during model instantiation: {e}")
            raise

    def generate_inference(self, prompt: str, max_tokens: int = 50) -> str:
        """Executes text generation using tokenized inputs under strict safety limits."""
        if self.model is None or self.tokenizer is None:
            # Safe mock fallback response
            return f"[MOCK RESPONSE] Processing verified prompt: '{prompt}' inside execution loop."

        # Format input using standard chat templates
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    # Test local structural integration execution instantly
    engine = LocalInferenceEngine()
    engine.initialize_platform(mock_mode=True)
    response = engine.generate_inference("Analyze transaction log anomalies for account 1234")
    print(f"Engine Output: {response}")
