# model_platform/optimize.py
import torch

class ModelOptimizer:
    """Handles runtime hardware detection and precision optimization configurations."""

    @staticmethod
    def get_execution_device() -> str:
        """Dynamically assigns hardware acceleration based on platform availability."""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"  # For Apple Silicon compatibility
        return "cpu"

    @staticmethod
    def get_quantization_config(precision_mode: str = "8bit") -> dict:
        """Generates configuration maps for model compression.

        In a production environment, this interfaces with bitsandbytes for 4/8bit
        layers. Here it maps the architectural parameters.
        """
        if precision_mode == "4bit":
            return {
                "load_in_4bit": True,
                "bnb_4bit_compute_dtype": torch.float16,
                "bnb_4bit_quant_type": "nf4"
            }
        elif precision_mode == "8bit":
            return {
                "load_in_8bit": True,
                "torch_dtype": torch.float16
            }
        return {"torch_dtype": torch.float32}
