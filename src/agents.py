"""1個の問題を解くエージェント"""
import asyncio
import os
from enum import Enum
from typing import List

from bs4 import BeautifulSoup

import code_verification
from utils import llm
from utils.http import download_page
from utils.logging import log, logger


class Status(Enum):
    """エージェントのステータス"""

    # 初期状態
    NOT_STARTED = 1
    # 問題を解いている状態
    STARTED = 2
    # 問題を解いた状態
    FINISHED = 3


class Agent:
    """1個の問題を解くエージェント"""

    def __init__(self, contest_code: str, problem_code: str):
        self.contest_code: str = contest_code
        self.problem_code: str = problem_code
        self.status: Status = Status.NOT_STARTED
        log(f"{self.contest_code}/{self.problem_code}のエージェントを作成しました")

    @classmethod
    def run(cls, _agents: List["Agent"]) -> List[asyncio.Task]:
        """それぞれのエージェントが問題を解く"""
        # イベントループを作成する
        loop = asyncio.get_event_loop()
        # タスクのリストを作成する
        futures = [asyncio.ensure_future(agent.main()) for agent in _agents]
        log(f"{len(futures)}個のエージェントを作成しました")
        # イベントループを実行する
        result = loop.run_until_complete(asyncio.wait(futures))
        loop.close()
        return result

    async def main(self):
        # ステータスによって処理を分岐する
        while True:
            if self.status == Status.NOT_STARTED:
                try:
                    await self.not_started()
                except:
                    logger.exception()
            elif self.status == Status.STARTED:
                try:
                    await self.started()
                except:
                    logger.exception()
            elif self.status == Status.FINISHED:
                # 問題を解いた後の処理
                try:
                    await self.finished()
                except:
                    logger.exception()
                break
            # 1秒待つ
            await asyncio.sleep(1)

    def has_result_file(self) -> bool:
        """回答ファイルがあるかどうかを確認する"""
        return os.path.exists(f"./target/{self.contest_code}/{self.problem_code}.py")

    async def download_problem(self) -> str:
        """問題をダウンロードする"""
        url = (
            "https://www.qcoder.jp/contests/"
            + self.contest_code
            + "/problems/"
            + self.problem_code
        )
        page = await download_page(url)
        soup = BeautifulSoup(page, "html.parser")
        return soup.get_text()

    async def try_download_problem(self) -> str:
        """問題をダウンロードする"""
        for _ in range(3):
            try:
                problem_text = await self.download_problem()
                if problem_text:
                    return problem_text
            except:
                logger.exception()
            await asyncio.sleep(1)
        else:
            return ""

    async def save_problem(self, problem_text: str) -> bool:
        """問題を保存する"""
        self.problem = problem_text
        return True

    async def solve_problem(self, problem_text: str) -> bool:
        """問題を解く"""
        messages = []
        messages.append(
            {
                "role": "system",
                "content": "以下の競技プログラミングの回答プログラムを出力してください。使えるライブラリはmath, qiskit, qiskit.circuit.libraryのみです。",
            }
        )
        messages.append({"role": "user", "content": problem_text})
        generated_text = await llm.async_generate_text(messages)
        program = parse_program(generated_text)
        return program

    async def save_program(self, program: str) -> bool:
        """回答を保存する"""
        self.program = program
        return True

    async def save_result_file(self) -> bool:
        """回答ファイルを保存する"""
        if not hasattr(self, "program"):
            return False
        with open(f"./target/{self.contest_code}/{self.problem_code}.py", "w") as f:
            f.write(self.program)
        return True

    async def not_started(self):
        """問題を解く前の処理"""

        # 現在の状態を確認する
        if self.has_result_file():
            # 回答ファイルがある場合は、問題を解いた後の処理に移る
            self.status = Status.FINISHED
            return

        # 問題をダウンロードする
        problem_text = await self.try_download_problem()
        if not problem_text:
            # ダウンロードに失敗した場合は、いったん終了する
            log(f"{self.contest_code}/{self.problem_code}の問題のダウンロードに失敗しました")
            return

        success = await self.save_problem(problem_text)
        if success:
            self.status = Status.STARTED
            log(f"{self.contest_code}/{self.problem_code}の問題を解き始めます")
        else:
            log(f"{self.contest_code}/{self.problem_code}の問題の保存に失敗しました")

    async def started(self):
        """問題を解く処理"""
        # 問題の入力を受け取る
        problem_text = self.problem

        # 問題の回答を出力する
        program = await self.solve_problem(problem_text)
        if not program:
            # 回答に失敗した場合は、いったん終了する
            log(f"{self.contest_code}/{self.problem_code}の問題の回答に失敗しました")
            return
        else:
            log(f"{self.contest_code}/{self.problem_code}の問題の回答に成功しました")

        # 回答がコンパイルできるかどうかを確認する
        success = code_verification.is_compilable(program)
        if not success:
            # 回答に失敗した場合は、いったん終了する
            log(f"{self.contest_code}/{self.problem_code}の問題の回答がコンパイルできませんでした")
            return

        success = await self.save_program(program)
        if success:
            self.status = Status.FINISHED
            log(f"{self.contest_code}/{self.problem_code}の問題を解き終わりました")
        else:
            log(f"{self.contest_code}/{self.problem_code}の問題の回答の保存に失敗しました")

    async def finished(self):
        """問題を解いた後の処理"""
        # 回答をファイル出力する
        if not hasattr(self, "program"):
            # 再実行した場合に、回答がない場合は、いったん終了する
            return
        success = await self.save_result_file()
        if not success:
            raise RuntimeError("回答ファイルの出力に失敗しました")
        else:
            log(f"{self.contest_code}/{self.problem_code}の回答ファイルを出力しました")


def parse_program(txt):
    """```で囲まれたプログラム部分を抽出する"""
    import re

    pattern = r"```(.*?)```"
    match = re.search(pattern, txt, re.DOTALL)
    if match:
        program = match.groups()[0]
        if program.startswith("python"):
            program = program[6:]
        return program
    else:
        return ""
