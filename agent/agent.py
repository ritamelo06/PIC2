import os
import traceback
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)
MODEL = os.getenv("LLM_MODEL")

SYSTEM_PROMPT = """You are an expert Python developer.
Your task is to write a Python script that solves the user's request.
Output ONLY raw Python code. Do not use markdown formatting (like ```python).
Do not include any explanations. Ensure the code is self-contained.
If the code requires testing, include assert statements at the end.
"""

def run_agent(task_description: str, max_iterations: int = 3):
    print(f"Task: {task_description}\n")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task_description}
    ]

    for iteration in range(1, max_iterations + 1):
        print(f"--- Iteration {iteration} ---")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.0
        )
        generated_code = response.choices[0].message.content.strip()
        
        print(f"LLM generated:\n{generated_code}\n")
        
        try:
            exec_globals = {}
            exec(generated_code, exec_globals)
            print("SUCCESS! The code executed without errors.")
            break
            
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"ERROR detected by the interpreter:\n{error_msg}\n")
            
            messages.append({"role": "assistant", "content": generated_code})
            messages.append({
                "role": "user", 
                "content": f"Your code produced the following error:\n{error_msg}\nPlease fix the code and output the complete corrected script."
            })

if __name__ == "__main__":

    # should fail since numpy is not installed in the env
    task = "Write a Python script that imports the `numpy` library and creates a 2x2 array of ones. Then, include an assert statement to check the sum of all elements is 4."
    run_agent(task)