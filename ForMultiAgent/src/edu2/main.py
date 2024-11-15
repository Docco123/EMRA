#!/usr/bin/env python
import sys
import warnings

from edu2.crew import Edu2



#from langtrace_python_sdk import langtrace

#langtrace.init(api_key = 'cab575027336c92068db5e8776ac39656abea59672ce5bcf3bf1588a3addec8f')


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'input': '20 patients, whose odds of survival without care ranges uniformly from 0.1 to 0.3, whose odds of survival with care ranges uniformly from 0.6 to 0.9, and whose number of blood units required ranges uniformly from 0 to 3, are incoming to a local care facility. You have 4 spots on a medevac helicopter that transport the patients to the nearest full-service facility, and 10 beds to treat patients locally,  30 units of blood, and 3 medical personnel. Patients with increasing degree of severity require proportionally more treatment time, higher priority for beds, and more blood units. You will need to allocate resources to maximize the number of lives saved.',
    }
    Edu2().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Edu2().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Edu2().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Edu2().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
