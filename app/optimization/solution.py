"""Defines a protocol for solutions"""

import typing


class ProblemSolution(typing.Protocol):
    solution: typing.Any
