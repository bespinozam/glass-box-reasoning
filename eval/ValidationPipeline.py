from eval.utils import create_hanoi_prompt
from models.deepseek import load_model, load_tokenizer
from puzzles.hanoi_tower.output_parser import parse_hanoi_output
from puzzles.hanoi_tower.automated_validator import AutomatedValidator
from puzzles.hanoi_tower.output_logger import OutputLogger

class ValidationPipe:
    def __init__(self, model_name):
        self.model_name = model_name

        self.tokenizer = load_tokenizer(model_name)
        self.model = load_model(model_name)


    def run_evaluation(self, level_limit=5, num_samples=5, verbose=False):
        print(f"Running evaluation for model {self.model_name}")
        logger = OutputLogger(
            run_id="test_run_2025",
            model_name=self.model_name,
            puzzle_name="hanoi"
        )
        print(f"Output directory: {logger.output_dir}")
        run_results = {}

        for current_level in range(1, level_limit + 1):
            print(f"Running evaluation for level {current_level}")
            run_results[str(current_level)] = {"passed": 0, "parse_failed": 0, "validation_failed": 0}
            for sample_iter in range(num_samples):
                print(f"\tSample {sample_iter}")
                prompt = create_hanoi_prompt(self.tokenizer, current_level)
                prompt_tokens = self.tokenizer(prompt, return_tensors="pt")
                prompt_length = prompt_tokens['input_ids'].shape[1]

                response = []
                for token in self.model.generate_streaming(
                    prompt = prompt,
                    max_new_tokens = 65000,
                    temperature = 1.0,
                    top_p = 1.0,
                    do_sample = True
                ):
                    response.append(token)
                    if verbose:
                        print(token, end="", flush=True)

                # Parsing output to check for solution
                response_length = len(response)
                response_as_text = "".join(response)
                moves, error = parse_hanoi_output(response_as_text)

                if moves:
                    validator = AutomatedValidator(n_disks=current_level)
                    result = validator.validate_solution(moves, verbose=False)
                    logger.log_iteration_with_validation(
                        n_disks=current_level,
                        raw_output=response_as_text,
                        input_prompt=prompt,
                        validation_result=result,
                        tokens_used=prompt_length+response_length,
                        parsed_output=moves,
                        parse_error=result["error_message"]
                    )

                    if result["is_solved"]:
                        run_results[str(current_level)]["passed"] += 1
                    else:
                        run_results[str(current_level)]["validation_failed"] += 1

                else:
                    logger.log_iteration_with_validation(
                        n_disks=current_level,
                        raw_output=response_as_text,
                        input_prompt=prompt,
                        validation_result={},
                        tokens_used=prompt_length+response_length,
                        parsed_output=moves,
                        parse_error=error
                    )

                    run_results[str(current_level)]["parse_failed"] += 1

        # Print final results
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        for level, results in run_results.items():
            print(f"\nLevel {level}:")
            print(f"  Passed: {results['passed']}/{num_samples}")
            print(f"  Parse Failed: {results['parse_failed']}/{num_samples}")
            print(f"  Validation Failed: {results['validation_failed']}/{num_samples}")
        print("="*60)

        return run_results