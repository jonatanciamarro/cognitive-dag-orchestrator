"""Dashboard authentication — simple password-based auth for Streamlit."""

from __future__ import annotations

import hmac
import os
import streamlit as st


def _get_password() -> str:
    """Get dashboard password from env or use default."""
    return os.environ.get("DASHBOARD_PASSWORD", "")


def _check_password(password: str) -> bool:
    """Check password against stored hash."""
    stored = _get_password()
    if not stored:
        return True  # No password configured
    return hmac.compare_digest(password, stored)


def require_auth() -> bool:
    """Show login form and return True if authenticated."""
    if not _get_password():
        return True

    if "dashboard_auth" in st.session_state and st.session_state["dashboard_auth"]:
        return True

    st.set_page_config(page_title="Campaign Autopilot — Login", page_icon="🔐")
    st.title("🔐 Campaign Autopilot")

    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if _check_password(password):
                st.session_state["dashboard_auth"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
    return False
