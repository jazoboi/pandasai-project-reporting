"""
PandasAI natural language query engine.

Wraps PandasAI to enable natural language analytics on
project management DataFrames.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a PandasAI query."""
    question: str
    answer: str
    chart_path: str | None = None
    generated_code: str = ""


class ProjectAnalyzer:
    """Natural language analytics on project data.

    Wraps PandasAI SmartDataframe to enable questions like
    "Show bug trends by sprint" on Jira ticket data.

    Parameters
    ----------
    api_key : str
        OpenAI API key for PandasAI LLM backend.
    model : str
        Model name (default: gpt-4o).
    """

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self._llm = OpenAI(api_token=api_key, model=model)
        self._smart_df: SmartDataframe | None = None

    def load_data(self, df: pd.DataFrame) -> None:
        """Load a DataFrame for querying.

        Parameters
        ----------
        df : pd.DataFrame
            Project/ticket data (typically from JiraClient).
        """
        self._smart_df = SmartDataframe(
            df,
            config={
                "llm": self._llm,
                "save_charts": True,
                "save_charts_path": "output/charts/",
                "verbose": False,
            },
        )
        logger.info("Loaded %d rows for analysis", len(df))

    def ask(self, question: str) -> QueryResult:
        """Ask a natural language question about the data.

        Parameters
        ----------
        question : str
            Plain-English analytics question.

        Returns
        -------
        QueryResult
            Answer with optional chart path.
        """
        if self._smart_df is None:
            raise RuntimeError("No data loaded. Call load_data() first.")

        result = self._smart_df.chat(question)

        return QueryResult(
            question=question,
            answer=str(result),
            chart_path=self._find_latest_chart(),
        )

    @staticmethod
    def _find_latest_chart() -> str | None:
        """Find the most recently generated chart file."""
        import os
        chart_dir = "output/charts/"
        if not os.path.exists(chart_dir):
            return None
        charts = sorted(
            [f for f in os.listdir(chart_dir) if f.endswith(".png")],
            key=lambda f: os.path.getmtime(os.path.join(chart_dir, f)),
            reverse=True,
        )
        return os.path.join(chart_dir, charts[0]) if charts else None
