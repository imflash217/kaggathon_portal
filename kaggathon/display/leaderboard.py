from typing import Dict

import pandas as pd
import streamlit as st

from kaggathon.config import ADMIN_USERNAME, SHOW_TOP_K_ONLY
from kaggathon.submissions.submissions_manager import \
    SingleParticipantSubmissions


class Leaderboard:
    def __init__(self, submission_manager, evaluator) -> None:
        self.submission_manager = submission_manager
        self.evaluator = evaluator

    @st.cache(
        hash_funcs={SingleParticipantSubmissions: lambda x: x.submissions_hash()},
        show_spinner=False,
    )
    def _get_sorted_leaderboard(
        self,
        participants_dict: Dict[str, SingleParticipantSubmissions],
        username: str,
    ):
        for participant in participants_dict.values():
            participant.update_results(self.evaluator)

        metric_names = [metric.name() for metric in self.evaluator.metrics()]

        # leaderboard as a pandas dataframe
        leaderboard = pd.DataFrame(
            [
                [
                    pname,
                    SingleParticipantSubmissions.get_datetime_from_path(best_result[0]),
                    *best_result[1],
                ]
                for pname, best_result in [
                    (pname, p.get_best_result()) for pname, p in participants_dict.items()
                ]
                if best_result is not None
            ],
            columns=["Participant Name", "Submission Time", *metric_names],
        )
        leaderboard = leaderboard.sort_values(
            by=metric_names + ["Submission Time"],
            ascending=[False] * len(metric_names) + [True],
            ignore_index=True,
        )
        leaderboard.index += 1  # TODO: what does this do??
        if username != ADMIN_USERNAME:
            leaderboard = leaderboard.iloc[:SHOW_TOP_K_ONLY]
        return leaderboard

    def display_leaderboard(self, username: str, leaderboard_placeholder=None):
        leaderboard = self._get_sorted_leaderboard(
            self.submission_manager.participants, username
        )
        if leaderboard_placeholder is not None:
            leaderboard_placeholder.table(leaderboard)
        else:
            st.table(leaderboard)
