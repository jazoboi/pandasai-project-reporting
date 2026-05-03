"""
Jira REST API client.

Handles authentication, paginated issue fetching, and
sprint/board metadata extraction.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterator

import httpx
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class JiraConfig:
    """Jira connection configuration."""
    base_url: str
    email: str
    api_token: str
    project_key: str
    max_results: int = 100


class JiraClient:
    """Client for the Jira REST API.

    Fetches issues, sprints, and project metadata with
    automatic pagination and rate limit handling.

    Parameters
    ----------
    config : JiraConfig
        Connection settings.
    """

    def __init__(self, config: JiraConfig) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            auth=(config.email, config.api_token),
            timeout=30.0,
        )

    def fetch_issues(
        self,
        jql: str | None = None,
        fields: list[str] | None = None,
    ) -> pd.DataFrame:
        """Fetch all issues matching a JQL query.

        Parameters
        ----------
        jql : str, optional
            JQL filter (defaults to all project issues).
        fields : list[str], optional
            Fields to retrieve.

        Returns
        -------
        pd.DataFrame
            Flattened issue data.
        """
        if jql is None:
            jql = f"project = {self._config.project_key} ORDER BY created DESC"

        if fields is None:
            fields = [
                "summary", "status", "issuetype", "priority",
                "assignee", "created", "updated", "resolutiondate",
                "story_points", "sprint", "labels",
            ]

        issues = list(self._paginate_search(jql, fields))
        logger.info("Fetched %d issues for project %s", len(issues), self._config.project_key)
        return self._flatten_issues(issues)

    def fetch_sprints(self, board_id: int) -> pd.DataFrame:
        """Fetch all sprints for a board."""
        url = f"/rest/agile/1.0/board/{board_id}/sprint"
        response = self._client.get(url)
        response.raise_for_status()

        sprints = response.json().get("values", [])
        return pd.DataFrame(sprints)

    def _paginate_search(
        self, jql: str, fields: list[str]
    ) -> Iterator[dict]:
        """Paginate through Jira search results."""
        start_at = 0
        while True:
            response = self._client.post(
                "/rest/api/3/search",
                json={
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": self._config.max_results,
                    "fields": fields,
                },
            )
            response.raise_for_status()
            data = response.json()

            for issue in data.get("issues", []):
                yield issue

            total = data.get("total", 0)
            start_at += self._config.max_results
            if start_at >= total:
                break

    @staticmethod
    def _flatten_issues(issues: list[dict]) -> pd.DataFrame:
        """Flatten nested Jira issue JSON into a flat DataFrame."""
        rows = []
        for issue in issues:
            fields = issue.get("fields", {})
            rows.append({
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name"),
                "type": fields.get("issuetype", {}).get("name"),
                "priority": fields.get("priority", {}).get("name"),
                "assignee": (fields.get("assignee") or {}).get("displayName"),
                "created": fields.get("created"),
                "updated": fields.get("updated"),
                "resolved": fields.get("resolutiondate"),
            })
        return pd.DataFrame(rows)
