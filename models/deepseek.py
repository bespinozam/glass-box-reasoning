from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load reasoning model
DEEPSEEK_R1_1p5B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
DEEPSEEK_R1_7B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

QWEN_BASE = "Qwen/Qwen2.5-1.5B-Instruct"
QWEN_BASE_MATH = "Qwen/Qwen2.5-Math-1.5B"


def load_model(model_name: str):
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    print(f"Model {model_name} loaded")
    print(f"Parameters: {model.num_parameters() / 1e9:.2f}B")
    print(f"Memory: {model.get_memory_footprint() / 1e9:.2f} GB")

    return model


def load_tokenizer(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print(f"Tokenizer for model {model_name} loaded")

    return tokenizer


class Model:
    def __init__(self, model_name, tokenizer):
        self.model = load_model(DEEPSEEK_R1_1p5B)
        self.tokenizer = tokenizer

    def generate_streaming(self, prompt, max_new_tokens, temperature, top_p, do_sample):
        """
        Generate text token-by-token using model() with KV cache. Yields each new token as it's generated.
        """
        was_training = self.model.training

        try:
            self.model.eval()
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_ids = inputs['input_ids'].to(self.model.device)
            past_key_values = None
            generated_tokens = []

            for _ in range(max_new_tokens):
                # Forward pass with cache
                with torch.no_grad():
                    outputs = self.model(input_ids=input_ids, past_key_values=past_key_values, use_cache=True)

                # Update cache for next iteration
                past_key_values = outputs.past_key_values

                # Get logits for the last token
                next_token_logits = outputs.logits[:, -1, :]

                # Apply temperature
                if temperature != 1.0:
                    next_token_logits = next_token_logits / temperature

                # Apply top-p (nucleus) sampling
                if do_sample:
                    # Convert to probabilities
                    probs = torch.softmax(next_token_logits, dim=-1)

                    if top_p < 1.0:
                        # Sort probabilities
                        sorted_probs, sorted_indices = torch.sort(probs, descending=True, dim=-1)
                        cumulative_probs = torch.cumsum(sorted_probs, dim=-1)

                        # Remove tokens with cumulative probability above top_p
                        sorted_indices_to_remove = cumulative_probs > top_p
                        # Keep at least one token
                        sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
                        sorted_indices_to_remove[:, 0] = False

                        # Zero out removed indices
                        sorted_probs[sorted_indices_to_remove] = 0.0
                        sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True)

                        # Sample from filtered distribution
                        next_token = torch.multinomial(sorted_probs, num_samples=1)
                        next_token = sorted_indices.gather(-1, next_token)
                    else:
                        # Sample from full distribution
                        next_token = torch.multinomial(probs, num_samples=1)
                else:
                    # Greedy decoding
                    next_token = next_token_logits.argmax(dim=-1, keepdim=True)

                # Decode and yield the new token
                token_text = self.tokenizer.decode(next_token[0], skip_special_tokens=True)
                yield token_text

                # Check for end of sequence
                if next_token.item() == self.tokenizer.eos_token_id:
                    break

                # Prepare input for next iteration (only the new token)
                input_ids = next_token
                generated_tokens.append(next_token.item())

        finally:
            if was_training:
                self.model.train()
