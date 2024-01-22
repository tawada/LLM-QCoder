# LLM-QCoder

LLM-QCoder is a system designed to automate the process of solving problems for coding contests. The system uses OpenAI's large language models (LLM), such as GPT-4, to generate solutions to given programming problems. This document will describe the structure and functionality of the system as extracted from the source code provided.

## Project Structure

The project is structured into several Python modules, which include:

- `main.py`: This is the entry point of the application. It initializes logging, takes input for the contest and problem codes, and then runs the agents to solve the problems.
- `agents.py`: Defines an `Agent` class responsible for solving an individual problem. Agents fetch problems, generate solutions using LLM, and save the output.
- `utils/logging.py`: Contains utilities for setting up and performing logging operations across different levels.
- `utils/http.py`: Provides a simple asynchronous interface to perform HTTP GET requests.
- `utils/llm.py`: Interfaces with the OpenAI API to generate text using large language models asynchronously.
- `README.md`: Provides information about the project (this file).

## Requirements
- Python 3.11
- `requests`: For making HTTP requests.
- `openai`: To interact with the OpenAI API.
- `bs4`: Used for parsing HTML content.
- `asyncio`: For asynchronous control flow and operations.
- An OpenAI API key with access to GPT-4 or a suitable alternative.

## Installation

To install the necessary dependencies for this project, you should run:

```bash
pipenv sync
```

Make sure you have populated the `Pipfile.lock` file with the libraries mentioned in the Requirements section above.

## Usage

To run the system, execute the `main.py` script:

```bash
python src/main.py

# You will be prompted to enter the contest code and then the problem codes separated by comma and space.
```

Once the program is running, you will input the contest code followed by the problem codes separated by comma and space as prompted. The `Agent` instances will carry out the following steps for each problem:

1. Download the problem statement.
2. Generate a solution by using LLM.
3. Save the generated solution program to the appropriate directory.

## Contributing

To contribute to this project, you can follow the standard git workflow:

1. Fork the repository.
2. Clone your fork and create a new branch.
3. Make your changes and commit them.
4. Push the changes to your fork.
5. Submit a pull request to the original repository.

Please make sure your code passes all the existing tests and write new tests for any added functionality.

## License

MIT

## Notes

The `Agent` class uses `asyncio` and is designed to operate concurrently for multiple problems. The `run` class method handles the creation of an event loop and tasks to execute the agents.

## Potential Improvements

- Include exception handling in `http.py` to cater for network-related errors.
- Implement rate-limiting and retries within the `llm.py` module when using the OpenAI API.
- Ensure proper validation and error-handling in the `Agent` logic, especially around downloading problems and generating solutions.
- Create a comprehensive test suite to cover different scenarios and edge cases.
