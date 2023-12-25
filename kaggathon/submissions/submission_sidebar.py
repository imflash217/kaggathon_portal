from io import BytesIO, StringIO
from typing import Callable, Optional, Union

import streamlit as st

from kaggathon.config import ADMIN_USERNAME
from kaggathon.submissions.submissions_manager import (
    SingleParticipantSubmissions, SubmissionManager)


class SubmissionSidebar:
    def __init__(
        self,
        username: str,
        submission_manager: SubmissionManager,
        submission_file_extension: Optional[str] = None,
        submission_validator: Optional[Callable[[Union[StringIO, BytesIO]], bool]] = None,
    ) -> None:
        self.username = username
        self.submission_manager = submission_manager
        self.submission_file_extension = submission_file_extension
        self.submission_validator = submission_validator
        self.participant: SingleParticipantSubmissions = None
        self.file_uploader_key = f"file upload {username}"

    def init_participant(self):
        self.submission_manager.add_participant(self.username, exists_ok=True)
        self.participant = self.submission_manager.get_participant(self.username)

    def _upload_submission(
        self, io_stream: Union[BytesIO, StringIO], submission_name: Optional[str] = None
    ):
        self.init_participant()
        self.participant.add_submission(
            io_stream, submission_name, self.submission_file_extension
        )

    def submit(self):
        file_extension_suffix = (
            f"(.{self.submission_file_extension})"
            if self.submission_file_extension
            else None
        )
        submission_io_stream = st.sidebar.file_uploader(
            "Upload your submission file " + file_extension_suffix,
            type=self.submission_file_extension,
            key=self.file_uploader_key,
        )
        submission_name = st.sidebar.text_input(
            label="Submission name (optional): ", value="", max_chars=30
        )
        if st.sidebar.button("Submit 📮"):
            if submission_io_stream is None:
                st.sidebar.error("❌ Please upload a file.")
            else:
                submission_failed = True
                with st.spinner("⏫ Validating & Uploading your submission..."):
                    if self.submission_validator is None or self.submission_validator(
                        submission_io_stream
                    ):
                        self._upload_submission(submission_io_stream, submission_name)
                        submission_failed = False
                if submission_failed:
                    st.sidebar.error("❌ Upload failed. The submission file is NOT valid.")
                else:
                    st.sidebar.success("✅ Upload successful!")

    def run_submission(self):
        st.sidebar.title(f"Hi `@{self.username}`! Welcome 🙏 ")
        if self.username != ADMIN_USERNAME:
            st.sidebar.markdown("## Submit Your Results ⤵️ ")
            self.submit()
