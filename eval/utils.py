
def create_hanoi_prompt(tokenizer, n:int=3):
    system_prompt = """
        You are a helpful assistant. Solve this puzzle for me.
        There are three pegs and n disks of different sizes stacked on the first peg. The disks are numbered from 1
        (smallest) to n (largest). Disk moves in this puzzle should follow:
        1. Only one disk can be moved at a time.
        2. Each move consists of taking the upper disk from one stack and placing it on top of another stack.
        3. A larger disk may not be placed on top of a smaller disk.
        The goal is to move the entire stack to the third peg.
        Example: With 3 disks numbered 1 (smallest), 2, and 3 (largest), the initial state is [[3, 2, 1], [], []], and a
        solution might be:
        moves = [[1 , 0 , 2] , [2 , 0 , 1] , [1 , 2 , 1] , [3 , 0 , 2] ,
        [1 , 1 , 0] , [2 , 1 , 2] , [1 , 0 , 2]]
        This means: Move disk 1 from peg 0 to peg 2, then move disk 2 from peg 0 to peg 1, and so on.
        Requirements:
        list of moves.
        • When exploring potential solutions in your thinking process, always include the corresponding complete
        • The positions are 0-indexed (the leftmost peg is 0).
        • Ensure your final answer includes the complete list of moves in the format:
        moves = [[disk id, from peg, to peg], ...]
    """

    user_prompt = f"""
            I have a puzzle with {n} disks of different sizes with
        Initial configuration:
        • Peg 0: {n} (bottom),. . . 2, 1 (top)
        • Peg 1: (empty)
        • Peg 2: (empty)
        Goal configuration:
        • Peg 0: (empty)
        • Peg 1: (empty)
        • Peg 2: {n} (bottom),. . . 2, 1 (top)
        Rules:
        • Only one disk can be moved at a time.
        • Only the top disk from any stack can be moved.
        • A larger disk may not be placed on top of a smaller disk.
        Find the sequence of moves to transform the initial configuration into the goal configuration.
        Remember to give the answer in the next format: moves = [[disk id, from peg, to peg], ...]
    """

    messages = [
        {
            "role": "system",
            "content": f"{system_prompt}"
        },
        {
            "role": "user",
            "content": f"{user_prompt}"
        }
    ]

    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    return formatted_prompt




# pipeline.py

# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
#
#
# class ReasoningPipeline:
#     def __init__(self, model_name, baseline_name=None):
#         """
#         Initialize pipeline with reasoning and baseline models.
#
#         Args:
#             model_name: Reasoning model (e.g., DeepSeek-R1-Distill-Qwen-1.5B)
#             baseline_name: Non-reasoning baseline (e.g., Qwen2.5-1.5B-Instruct)
#         """
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#
#         # Load reasoning model
#         self.reasoning_model = AutoModelForCausalLM.from_pretrained(
#             model_name,
#             torch_dtype=torch.float16,
#             device_map="auto"
#         )
#
#         # Load baseline model (optional)
#         if baseline_name:
#             self.baseline_model = AutoModelForCausalLM.from_pretrained(
#                 baseline_name,
#                 torch_dtype=torch.float16,
#                 device_map="auto"
#             )
#         else:
#             self.baseline_model = None
#
#     def generate_reasoning(self, prompt, max_tokens=2000):
#         """Generate with reasoning model."""
#         inputs = self.tokenizer(prompt, return_tensors="pt").to(
#             self.reasoning_model.device
#         )
#
#         outputs = self.reasoning_model.generate(
#             **inputs,
#             max_new_tokens=max_tokens,
#             temperature=0.7,
#             do_sample=True,
#             return_dict_in_generate=True,
#             output_attentions=True,  # For mechanistic analysis
#             output_hidden_states=True
#         )
#
#         response = self.tokenizer.decode(
#             outputs.sequences[0],
#             skip_special_tokens=True
#         )
#
#         return {
#             'response': response,
#             'outputs': outputs,  # For analysis
#             'tokens': outputs.sequences[0]
#         }
#
#     def generate_baseline(self, prompt, max_tokens=2000):
#         """Generate with baseline model."""
#         if not self.baseline_model:
#             raise ValueError("No baseline model loaded")
#
#         inputs = self.tokenizer(prompt, return_tensors="pt").to(
#             self.baseline_model.device
#         )
#
#         outputs = self.baseline_model.generate(
#             **inputs,
#             max_new_tokens=max_tokens,
#             temperature=0.7,
#             do_sample=True
#         )
#
#         response = self.tokenizer.decode(
#             outputs[0],
#             skip_special_tokens=True
#         )
#
#         return {
#             'response': response,
#             'tokens': outputs[0]
#         }
#
#     def evaluate_problem(self, problem, verify_fn):
#         """
#         Evaluate both models on a problem.
#
#         Args:
#             problem: Problem prompt (str)
#             verify_fn: Function to verify solution correctness
#         """
#         # Generate with reasoning model
#         reasoning_result = self.generate_reasoning(problem)
#         reasoning_correct = verify_fn(reasoning_result['response'])
#
#         # Generate with baseline (if available)
#         if self.baseline_model:
#             baseline_result = self.generate_baseline(problem)
#             baseline_correct = verify_fn(baseline_result['response'])
#         else:
#             baseline_result = None
#             baseline_correct = None
#
#         return {
#             'reasoning': {
#                 'response': reasoning_result['response'],
#                 'correct': reasoning_correct,
#                 'tokens': len(reasoning_result['tokens'])
#             },
#             'baseline': {
#                 'response': baseline_result['response'] if baseline_result else None,
#                 'correct': baseline_correct,
#                 'tokens': len(baseline_result['tokens']) if baseline_result else None
#             }
#         }
#
#
# # Usage:
# pipeline = ReasoningPipeline(
#     model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
#     baseline_name="Qwen/Qwen2.5-1.5B-Instruct"
# )
#
# # Test on Hanoi problem
# problem = create_hanoi_prompt(N=3)
# result = pipeline.evaluate_problem(problem, verify_hanoi_solution)
#
# print(f"Reasoning model: {result['reasoning']['correct']}")
# print(f"Baseline model: {result['baseline']['correct']}")
