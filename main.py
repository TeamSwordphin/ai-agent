import os
import argparse

from functions.call_function import available_functions, call_function
from prompts import system_prompt
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import MAX_LOOP_ITERATIONS

def start_agent():
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbox")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
    
    function_call_results = []

    for _ in range(MAX_LOOP_ITERATIONS):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            )
        )

        candidates = response.candidates
        function_call_results = []

        if candidates is not None:
            for candidate in candidates:
                messages.append(candidate.content)

        if response.usage_metadata is not None:
            if args.verbose == True:
                print(f"User prompt: {args.user_prompt}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        else:
            raise RuntimeError("Response is missing usage metadata")

        if response.function_calls is not None:
            for function_call in response.function_calls:
                function_call_result = call_function(function_call, args.verbose)
                parts = function_call_result.parts

                if len(parts) == 0:
                    raise Exception("Parts should not be empty")

                if parts[0].function_response.response == None:
                    raise Exception("Function reponse should not be None")

                if args.verbose:
                    print(f"-> {parts[0].function_response.response}")

                function_call_results.extend(parts)
                
            messages.append(types.Content(role="user", parts=function_call_results))
        else:
            print(response.text)
            return True

    return False

def main():
    load_dotenv()

    if start_agent() == False:
        print("Failed to generate the proper responses in time!")
        exit(1)
    else:
        print("Succeeded")


main()