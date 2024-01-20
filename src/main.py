from agents import Agent
from utils.logging import log, setup_logging

if __name__ == "__main__":
    contest_code = input().strip()
    problem_codes = list(map(lambda x: x.strip(), input().split(", ")))

    setup_logging()
    log(f"コンテスト: {contest_code}")
    log(f"問題: {problem_codes}")

    _agents = [Agent(contest_code, problem_code) for problem_code in problem_codes]

    # エージェントを実行する
    Agent.run(_agents)
