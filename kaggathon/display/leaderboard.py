from typing import Dict

import pandas as pd
import streamlit as st

from kaggathon.config import ADMIN_USERNAME, SHOW_TOP_K_ONLY
from kaggathon.submissions.submissions_manager import SingleParticipantSubmissions


class Leaderboard:
    def __init__(self, submission_manager, evaluator) -> None:
        self.submission_manager = submission_manager
        self.evaluator = evaluator
        self.id = None
        self.metric_names = [metric.name() for metric in self.evaluator.metrics()]

    # @st.cache_data(
    #     hash_funcs={
    #         SingleParticipantSubmissions: lambda x: x.submissions_hash(),
    #         "kaggathon.display.leaderboard.Leaderboard": lambda x: hash(x.id),
    #         },
    #     show_spinner=False,
    #     persist=True,
    # )
    def _get_sorted_leaderboard(
        self,
        participants_dict: Dict[str, SingleParticipantSubmissions],
        username: str,
    ):
        for participant in participants_dict.values():
            participant.update_results(self.evaluator)

        # metric_names = [metric.name() for metric in self.evaluator.metrics()]

        # leaderboard as a pandas dataframe
        leaderboard = pd.DataFrame(
            [
                [
                    pname,
                    "",
                    SingleParticipantSubmissions.get_datetime_from_path(best_result[0]),
                    *best_result[1],
                ]
                for pname, best_result in [
                    (pname, p.get_best_result()) for pname, p in participants_dict.items()
                ]
                if best_result is not None
            ],
            columns=["Team", "Members", "Submission Time", *self.metric_names],
        )
        leaderboard = leaderboard.sort_values(
            by=self.metric_names + ["Submission Time"],
            ascending=[False] * len(self.metric_names) + [True],
            ignore_index=True,
        )
        leaderboard.index += 1  # TODO: careful with this!!!
        if username != ADMIN_USERNAME:
            leaderboard = leaderboard.iloc[:SHOW_TOP_K_ONLY]

        # reset the index and save it as Rank
        leaderboard = leaderboard.reset_index().rename(columns={"index": "#Rank"})
        leaderboard = leaderboard.reset_index(drop=True)
        return leaderboard

    def display_leaderboard(self, username: str, leaderboard_placeholder=None):
        # print(f"✅ {self.submission_manager.participants}, \n, {username}")
        leaderboard = self._get_sorted_leaderboard(
            self.submission_manager.participants, username
        )

        # apply color styling to the dataframe
        styled_leaderboard = leaderboard.style.apply(func=self.color_top_rankers, axis=1)
        # styled_leaderboard.data = styled_leaderboard.data.reset_index(drop=True)
        if leaderboard_placeholder is not None:
            leaderboard_placeholder.dataframe(
                styled_leaderboard,
                use_container_width=True,
                column_order=["#Rank", "Team", "Members", *self.metric_names],
                hide_index=True,
            )
            # leaderboard_placeholder.dataframe(leaderboard, use_container_width=True, hide_index=True)
        else:
            st.dataframe(
                leaderboard,
                use_container_width=True,
                hide_index=True,
                column_order=["#Rank", "Team", "Members", *self.metric_names],
            )

        # if leaderboard_placeholder is not None:
        #     leaderboard_placeholder.table(leaderboard)
        # else:
        #     st.table(leaderboard)

    def color_top_rankers(self, row):
        color = "#000000"
        if row["#Rank"] == 1:
            bg_color = "#FFF78A"
            return ["color: %s; background-color: %s" % (color, bg_color)] * len(row)
        elif row["#Rank"] == 2:
            bg_color = "#F3F8FF"  # "#FAF7F0"
            return ["color: %s; background-color: %s" % (color, bg_color)] * len(row)
        elif row["#Rank"] == 3:
            bg_color = "#DFD3C3"  # "#45FFCA"
            return ["color: %s; background-color: %s" % (color, bg_color)] * len(row)
        else:
            bg_color = "white"
            return ["color: %s; background-color: %s" % (color, bg_color)] * len(row)
