import pathlib
import sys

import streamlit as st

from kaggathon.config import (ADMIN_USERNAME, ARGON2_KWARGS, EVALUATOR_CLASS,
                              EVALUATOR_KWARGS, MAX_NUM_USERS,
                              PASSWORDS_DB_FILE, SUBMISSIONS_DIR,
                              VALID_SUBMISSION_FILE_EXTENSION)
from kaggathon.display.leaderboard import Leaderboard
from kaggathon.display.personal_progress import PersonalProgress
from kaggathon.login.login import Login
from kaggathon.login.username_password_manager import \
    UsernamePasswordManagerArgon2
from kaggathon.submissions.submission_sidebar import SubmissionSidebar
from kaggathon.submissions.submissions_manager import SubmissionManager

st.markdown("## Leaderboard")
leaderboard_placeholder = st.empty()
progress_placeholder = st.empty()


def get_login():
    password_manager = UsernamePasswordManagerArgon2(PASSWORDS_DB_FILE, **ARGON2_KWARGS)
    return Login(password_manager, MAX_NUM_USERS)


# @st.cache(allow_output_mutation=True)
@st.cache_data(persist=True)
def get_submissions_manager():
    return SubmissionManager(SUBMISSIONS_DIR)


# @st.cache(allow_output_mutation=True)
@st.cache_data(persist=True)
def get_submission_sidebar(username: str):
    return SubmissionSidebar(
        username,
        get_submissions_manager(),
        submission_validator=get_evaluator().validate_submission,
        submission_file_extension=VALID_SUBMISSION_FILE_EXTENSION,
    )


# @st.cache(allow_output_mutation=True)
@st.cache_data(persist=True)
def get_evaluator():
    return EVALUATOR_CLASS(**EVALUATOR_KWARGS)


# @st.cache(allow_output_mutation=True)
@st.cache_data(persist=True)
def get_leaderboard():
    return Leaderboard(get_submissions_manager(), get_evaluator())


@st.cache_data(persist=True)
def get_users_without_admin():
    return [
        user
        for user in get_submissions_manager().participants.keys()
        if user != ADMIN_USERNAME
    ]


# @st.cache(allow_output_mutation=True)
@st.cache_data(persist=True)
def get_personal_progress(username: str):
    return PersonalProgress(
        get_submissions_manager().get_participant(username), get_evaluator()
    )


def display_user_progess_for_admin():
    selected_user = st.sidebar.selectbox("Select a user", get_users_without_admin())
    if selected_user is not None:
        get_personal_progress(selected_user).show_progress(progress_placeholder)


# sanity check
if "login" not in st.session_state:
    st.session_state.login = get_login()
login = st.session_state["login"]  # access the login object from session state
login.init()  # initialize the login state


if login.run_and_return_if_access_is_allowed() and not login.has_user_signed_out():
    username = login.get_username()
    get_submission_sidebar(username).run_submission()
    get_leaderboard().display_leaderboard(username, leaderboard_placeholder)
    if (
        get_submissions_manager().participant_exists(username)
        and username != ADMIN_USERNAME
    ):
        get_personal_progress(username).show_progress(progress_placeholder)
    if username == ADMIN_USERNAME:
        display_user_progess_for_admin()
else:
    get_leaderboard().display_leaderboard("", leaderboard_placeholder)
