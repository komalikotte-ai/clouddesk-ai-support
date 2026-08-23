import streamlit as st
import requests
import textwrap


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CloudDesk AI Support",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000/chat"

CONFIDENCE_THRESHOLD = 0.70


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# HTML RENDER HELPER
# Streamlit's markdown parser treats 4+ leading spaces as a
# code block, which breaks indented HTML strings. dedent()
# strips the common leading whitespace so the HTML renders
# properly instead of showing up as literal text.
# ============================================================

def render_html(content: str) -> None:
    # Strip leading whitespace from every line. Markdown treats
    # 4+ leading spaces as a code fence, so any indentation left
    # in an HTML string gets shown as literal text instead of
    # being rendered as HTML.
    cleaned = "\n".join(line.lstrip() for line in content.splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


# Color coding per category so Billing / Technical / Account Access /
# Unknown are visually distinct at a glance instead of identical gray
# pills.
CATEGORY_STYLES = {
    "billing": {
        "text": "#1d4ed8",
        "bg": "#eff6ff",
        "border": "#bfdbfe",
    },
    "technical": {
        "text": "#c2410c",
        "bg": "#fff7ed",
        "border": "#fed7aa",
    },
    "account_access": {
        "text": "#6d28d9",
        "bg": "#f5f3ff",
        "border": "#ddd6fe",
    },
    "unknown": {
        "text": "#475467",
        "bg": "#f6f7f9",
        "border": "#e3e6ec",
    },
}


def category_pill_html(category: str) -> str:
    style = CATEGORY_STYLES.get(
        str(category).lower(),
        CATEGORY_STYLES["unknown"],
    )
    label = str(category).replace("_", " ").title()
    return (
        '<div class="meta-pill" style="'
        f'color:{style["text"]};'
        f'background:{style["bg"]};'
        f'border-color:{style["border"]};'
        '">'
        f'Category <strong style="color:{style["text"]}">{label}</strong>'
        '</div>'
    )


# ============================================================
# CUSTOM CSS
# IMPORTANT:
# CSS is placed inside a style block only.
# It is NOT displayed as page content.
# ============================================================

render_html(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html,
    body,
    [class*="css"] {
        font-family: "Inter", sans-serif;
        font-size: 16px;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(99, 102, 241, 0.10),
                transparent 32%
            ),
            radial-gradient(
                circle at 4% 100%,
                rgba(20, 184, 166, 0.07),
                transparent 30%
            ),
            #f4f6fb;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 34px;
        padding-bottom: 56px;
        padding-left: 38px;
        padding-right: 38px;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7eaf0;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 30px;
        padding-left: 20px;
        padding-right: 20px;
    }

    .sidebar-brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }

    .sidebar-logo {
        width: 38px;
        height: 38px;
        border-radius: 11px;
        background: linear-gradient(135deg, #6366f1, #4338ca);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(67, 56, 202, 0.28);
    }

    .sidebar-brand {
        color: #111827;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .sidebar-subtitle {
        margin-left: 50px;
        color: #98a2b3;
        font-size: 12.5px;
        font-weight: 600;
        margin-bottom: 30px;
        letter-spacing: 0.01em;
    }

    .sidebar-heading {
        color: #9aa4b2;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        margin: 24px 0 10px 8px;
    }

    .sidebar-nav-active {
        background: linear-gradient(135deg, #eef0ff, #e5e8ff);
        color: #4338ca;
        border-radius: 10px;
        padding: 11px 12px;
        font-size: 14.5px;
        font-weight: 650;
        margin-bottom: 5px;
        border: 1px solid #dcdfff;
    }

    .sidebar-nav {
        color: #667085;
        border-radius: 10px;
        padding: 11px 12px;
        font-size: 14.5px;
        font-weight: 500;
        margin-bottom: 5px;
    }

    .sidebar-nav:hover {
        background: #f5f6fa;
    }

    .sidebar-status {
        margin-top: 32px;
        padding: 14px;
        border: 1px solid #e7eaf0;
        border-radius: 12px;
        background: #fafbfc;
    }

    .sidebar-status-title {
        color: #344054;
        font-size: 13.5px;
        font-weight: 650;
    }

    .sidebar-status-text {
        color: #98a2b3;
        font-size: 11.5px;
        margin-top: 4px;
        line-height: 1.5;
    }

    .online-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #16a34a;
        margin-right: 5px;
        vertical-align: middle;
        box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.15);
    }


    /* ========================================================
       HEADER
       ======================================================== */

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 26px;
    }

    .page-title {
        color: #0f172a;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }

    .page-subtitle {
        color: #667085;
        font-size: 15px;
        margin-top: 6px;
        font-weight: 500;
    }

    .header-status {
        border: 1px solid #bfe8cc;
        background: linear-gradient(135deg, #f2fbf5, #e8f8ee);
        color: #15803d;
        padding: 9px 15px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 650;
        white-space: nowrap;
    }


    /* ========================================================
       CHAT PANEL
       (card chrome now lives on the native Streamlit
       container, targeted via its stable key class)
       ======================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chat-panel-header) {
        background: #ffffff;
        border: 1px solid #e5e7eb !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 34px rgba(16, 24, 40, 0.06);
        overflow: hidden;
    }

    /* Streamlit adds automatic spacing between every element
       inside a container. We zero that out here so spacing
       inside the chat panel is controlled entirely by our own
       CSS margins/padding below, instead of stacking on top
       of Streamlit's defaults. */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chat-panel-header)
        [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chat-panel-header)
        > div {
        padding: 0 0 22px 0 !important;
    }

    /* The header bleeds edge-to-edge, but everything else inside
       the panel (welcome text, category cards, suggestions, chat
       messages) needs its own horizontal inset now that the
       container's default padding has been removed. */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.chat-panel-header)
        [data-testid="stHorizontalBlock"] {
        padding-left: 26px;
        padding-right: 26px;
    }

    .st-key-chat_panel {
        border-radius: 20px;
    }

    .chat-panel-header {
        padding: 20px 26px;
        border-bottom: 1px solid #edf0f4;
        background: linear-gradient(180deg, #fbfbfe, #ffffff);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .chat-header-left {
        display: flex;
        align-items: center;
        gap: 13px;
    }

    .ai-avatar {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #eef0ff, #e0e4ff);
        color: #4f46e5;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 19px;
        font-weight: 700;
    }

    .ai-name {
        color: #111827;
        font-size: 16px;
        font-weight: 700;
    }

    .ai-description {
        color: #98a2b3;
        font-size: 12.5px;
        margin-top: 2px;
        font-weight: 500;
    }

    .chat-online {
        color: #15803d;
        font-size: 12.5px;
        font-weight: 650;
    }


    /* ========================================================
       WELCOME
       ======================================================== */

    .welcome-container {
        text-align: center;
        max-width: 650px;
        margin: 30px auto 34px auto;
        padding: 0 25px;
    }

    .welcome-icon {
        width: 62px;
        height: 62px;
        margin: 0 auto 20px auto;
        border-radius: 18px;
        background: linear-gradient(135deg, #6366f1, #4338ca);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
        font-weight: 700;
        box-shadow: 0 10px 24px rgba(67, 56, 202, 0.25);
    }

    .welcome-title {
        color: #0f172a;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .welcome-description {
        color: #667085;
        font-size: 15.5px;
        line-height: 1.65;
        margin-top: 12px;
    }

    .welcome-note {
        color: #98a2b3;
        font-size: 13.5px;
        line-height: 1.55;
        margin-top: 10px;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-title {
        color: #344054;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 12px;
        padding: 0 26px;
    }


    /* ========================================================
       INFO PANEL
       ======================================================== */

    .info-panel {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 28px rgba(16, 24, 40, 0.045);
    }

    .info-title {
        color: #0f172a;
        font-size: 17px;
        font-weight: 700;
    }

    .info-subtitle {
        color: #98a2b3;
        font-size: 12.5px;
        margin-top: 3px;
        font-weight: 500;
    }

    .info-status {
        margin-top: 18px;
        background: linear-gradient(135deg, #f2fbf5, #e8f8ee);
        color: #15803d;
        border: 1px solid #bfe8cc;
        border-radius: 10px;
        padding: 11px 12px;
        font-size: 13px;
        font-weight: 650;
    }

    .info-divider {
        border-top: 1px solid #edf0f4;
        margin: 20px 0;
    }

    .info-label {
        color: #9aa4b2;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 11px;
    }

    .category-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0;
        color: #344054;
        font-size: 14px;
        font-weight: 600;
        border-bottom: 1px solid #f1f3f6;
    }

    .category-row:last-child {
        border-bottom: none;
    }

    .category-icon {
        width: 30px;
        height: 30px;
        border-radius: 9px;
        background: #eef0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #4f46e5;
        font-size: 13px;
    }

    .info-value {
        color: #344054;
        font-size: 14.5px;
        font-weight: 650;
    }

    .info-ready {
        margin-top: 6px;
        color: #15803d;
        font-size: 11.5px;
        font-weight: 650;
    }

    .info-about {
        color: #667085;
        font-size: 13px;
        line-height: 1.65;
    }


    /* ========================================================
       SUGGESTIONS
       ======================================================== */

    .suggestion-box {
        background: #fafbfc;
        border: 1px solid #e7eaf0;
        border-radius: 12px;
        padding: 13px 14px;
        min-height: 60px;
        transition: all 0.15s ease;
    }

    .suggestion-box:hover {
        border-color: #c7c9ff;
        background: #fbfbff;
    }

    .suggestion-category {
        color: #4f46e5;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .suggestion-text {
        color: #344054;
        font-size: 13.5px;
        font-weight: 500;
        line-height: 1.5;
    }


    /* ========================================================
       STREAMLIT CHAT OVERRIDES
       ======================================================== */

    [data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding-top: 14px;
        padding-bottom: 14px;
        padding-left: 26px;
        padding-right: 26px;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #29303c;
        font-size: 16px;
        line-height: 1.7;
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
        background: #eef0ff;
        color: #4f46e5;
    }


    /* ========================================================
       RESPONSE METADATA
       ======================================================== */

    .response-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }

    .meta-pill {
        background: #f6f7f9;
        border: 1px solid #e7eaf0;
        color: #667085;
        border-radius: 999px;
        padding: 6px 12px;
        font-size: 12.5px;
        font-weight: 550;
    }

    .meta-pill strong {
        color: #344054;
        font-weight: 700;
        margin-left: 4px;
    }

    .grounded {
        margin-top: 12px;
        color: #15803d;
        background: linear-gradient(135deg, #f2fbf5, #e8f8ee);
        border: 1px solid #bfe8cc;
        border-radius: 10px;
        padding: 10px 13px;
        font-size: 12.5px;
        font-weight: 650;
    }


    /* ========================================================
       ESCALATION
       ======================================================== */

    .escalation {
        margin-top: 14px;
        background: #fffbeb;
        border: 1px solid #f4df9c;
        border-radius: 13px;
        padding: 15px 16px;
    }

    .escalation-title {
        color: #92400e;
        font-size: 14px;
        font-weight: 700;
    }

    .escalation-text {
        color: #78716c;
        font-size: 13px;
        line-height: 1.6;
        margin-top: 5px;
    }

    .escalation-status {
        color: #a16207;
        font-size: 11.5px;
        font-weight: 700;
        margin-top: 9px;
    }


    /* ========================================================
       SOURCES
       ======================================================== */

    .sources-title {
        color: #9aa4b2;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-top: 14px;
        margin-bottom: 7px;
    }

    .source-item {
        display: inline-block;
        background: #fafbfc;
        border: 1px solid #e7eaf0;
        border-radius: 8px;
        color: #667085;
        padding: 6px 10px;
        margin: 2px 5px 2px 0;
        font-size: 12px;
        font-weight: 500;
    }


    /* ========================================================
       INPUT
       ======================================================== */

    [data-testid="stChatInput"] {
        border-top: none;
    }

    [data-testid="stChatInput"] textarea {
        border: 1px solid #dfe3ea !important;
        border-radius: 14px !important;
        background: #ffffff !important;
        color: #111827 !important;
        font-size: 15.5px !important;
        min-height: 54px !important;
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.025);
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.10) !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #e3e6ec;
        background: #ffffff;
        color: #344054;
        font-size: 13px;
        font-weight: 550;
        min-height: 44px;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #c7c9ff;
        color: #4338ca;
        background: #fafaff;
    }


    /* ========================================================
       HIDE STREAMLIT BRANDING
       ======================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding-left: 18px;
            padding-right: 18px;
            padding-top: 22px;
        }

        .page-title {
            font-size: 24px;
        }

        .st-key-chat_panel {
            border-radius: 14px;
        }

        .welcome-container {
            margin-top: 40px;
        }
    }

    @media (max-width: 640px) {

        .page-header {
            align-items: flex-start;
        }

        .header-status {
            display: none;
        }

        .page-subtitle {
            max-width: 270px;
        }

        .welcome-title {
            font-size: 22px;
        }

        .welcome-description {
            font-size: 14px;
        }
    }

    </style>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="sidebar-brand-row">
            <div class="sidebar-logo">◈</div>
            <div class="sidebar-brand">CloudDesk</div>
        </div>
        <div class="sidebar-subtitle">AI Support</div>
        """
    )

    render_html('<div class="sidebar-heading">Workspace</div>')

    render_html('<div class="sidebar-nav-active">◉ &nbsp; Support Console</div>')

    render_html('<div class="sidebar-nav">▣ &nbsp; Knowledge Base</div>')

    render_html('<div class="sidebar-nav">◫ &nbsp; Analytics</div>')

    render_html('<div class="sidebar-nav">⚙ &nbsp; Settings</div>')

    render_html(
        """
        <div class="sidebar-status">
            <div class="sidebar-status-title">
                <span class="online-dot"></span>
                AI System Online
            </div>
            <div class="sidebar-status-text">
                Support service connected
            </div>
        </div>
        """
    )


# ============================================================
# PAGE HEADER
# ============================================================

render_html(
    """
    <div class="page-header">

        <div>
            <div class="page-title">
                Support Console
            </div>

            <div class="page-subtitle">
                AI-powered Tier-1 support for CloudDesk customers
            </div>
        </div>

        <div class="header-status">
            <span class="online-dot"></span>
            AI Online
        </div>

    </div>
    """
)


# ============================================================
# MAIN LAYOUT
# ============================================================

chat_column, info_column = st.columns(
    [2.8, 1],
    gap="large",
)


# ============================================================
# MAIN CHAT COLUMN
# ============================================================

with chat_column:

    with st.container(border=True, key="chat_panel"):

        render_html(
            """
            <div class="chat-panel-header">

                <div class="chat-header-left">

                    <div class="ai-avatar">
                        ◈
                    </div>

                    <div>
                        <div class="ai-name">
                            CloudDesk AI
                        </div>

                        <div class="ai-description">
                            AI Support Assistant
                        </div>
                    </div>

                </div>

                <div class="chat-online">
                    <span class="online-dot"></span>
                    Online
                </div>

            </div>
            """
        )

        # ========================================================
        # EMPTY STATE
        # ========================================================

        if len(st.session_state.messages) == 0:

            render_html(
                """
                <div class="welcome-container">

                    <div class="welcome-icon">
                        ◈
                    </div>

                    <div class="welcome-title">
                        Welcome to CloudDesk Support
                    </div>

                    <div class="welcome-description">
                        Ask a question about billing, technical issues,
                        or account access. CloudDesk AI uses the
                        knowledge base to provide grounded answers.
                    </div>

                    <div class="welcome-note">
                        If your question can't be answered confidently,
                        we'll help escalate it to human support.
                    </div>

                </div>
                """
            )


            # ====================================================
            # WHAT CAN I HELP WITH?
            # ====================================================

            render_html('<div class="section-title">What can I help with?</div>')

            cat1, cat2, cat3 = st.columns(3)

            with cat1:
                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-category">
                            Billing
                        </div>
                        <div class="suggestion-text">
                            Payments, invoices & charges
                        </div>
                    </div>
                    """
                )

            with cat2:
                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-category">
                            Technical Support
                        </div>
                        <div class="suggestion-text">
                            Troubleshooting & technical issues
                        </div>
                    </div>
                    """
                )

            with cat3:
                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-category">
                            Account Access
                        </div>
                        <div class="suggestion-text">
                            Login, password & account access
                        </div>
                    </div>
                    """
                )


            st.markdown("<br>", unsafe_allow_html=True)


            # ====================================================
            # EXAMPLE QUESTIONS
            # ====================================================

            render_html('<div class="section-title">Try asking</div>')

            ex1, ex2 = st.columns(2)

            with ex1:

                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-text">
                            How can I update my payment method?
                        </div>
                    </div>
                    """
                )

                st.markdown("<div style='height:6px'></div>",
                            unsafe_allow_html=True)

                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-text">
                            How do I reset my password?
                        </div>
                    </div>
                    """
                )

            with ex2:

                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-text">
                            Why isn't my account syncing?
                        </div>
                    </div>
                    """
                )

                st.markdown("<div style='height:6px'></div>",
                            unsafe_allow_html=True)

                render_html(
                    """
                    <div class="suggestion-box">
                        <div class="suggestion-text">
                            Why was I charged twice?
                        </div>
                    </div>
                    """
                )


        # ========================================================
        # CHAT HISTORY
        # ========================================================

        for message in st.session_state.messages:

            role = message.get("role", "assistant")

            if role == "user":

                with st.chat_message("user"):

                    st.markdown(
                        message.get("content", "")
                    )

            else:

                with st.chat_message("assistant"):

                    st.markdown(
                        message.get(
                            "content",
                            "No response available.",
                        )
                    )

                    category = message.get(
                        "category",
                        "unknown",
                    )

                    confidence = message.get(
                        "confidence",
                        0.0,
                    )

                    status = message.get(
                        "status",
                        "",
                    )

                    reason = message.get(
                        "reason",
                        "",
                    )

                    sources = message.get(
                        "sources",
                        [],
                    )


                    # --------------------------------------------
                    # RESPONSE META
                    # --------------------------------------------

                    category_pill = category_pill_html(category)

                    meta_html = f"""
                    <div class="response-meta">

                        {category_pill}
                    """

                    # Only show confidence when backend provides
                    # a meaningful value.

                    if confidence is not None:

                        try:

                            confidence_value = float(
                                confidence
                            )

                            meta_html += f"""
                            <div class="meta-pill">
                                Confidence
                                <strong>
                                    {confidence_value:.0%}
                                </strong>
                            </div>
                            """

                        except (
                            TypeError,
                            ValueError,
                        ):
                            pass

                    meta_html += "</div>"

                    render_html(meta_html)


                    # --------------------------------------------
                    # GROUNDED ANSWER
                    # --------------------------------------------

                    if status == "answered":

                        render_html(
                            """
                            <div class="grounded">
                                ✓ &nbsp; Based on CloudDesk Knowledge Base
                            </div>
                            """
                        )


                    # --------------------------------------------
                    # ESCALATION
                    # --------------------------------------------

                    if status == "escalated":

                        safe_reason = (
                            reason
                            if reason
                            else
                            "This question could not be answered confidently using the CloudDesk knowledge base."
                        )

                        render_html(
                            f"""
                            <div class="escalation">

                                <div class="escalation-title">
                                    Let's get a human involved
                                </div>

                                <div class="escalation-text">
                                    {safe_reason}
                                </div>

                                <div class="escalation-status">
                                    Human support recommended
                                </div>

                            </div>
                            """
                        )


                    # --------------------------------------------
                    # SOURCES
                    # --------------------------------------------

                    if sources:

                        render_html('<div class="sources-title">Knowledge Sources</div>')

                        shown_sources = set()

                        for source in sources:

                            if not isinstance(source, dict):
                                continue

                            source_name = source.get(
                                "source",
                                "Unknown",
                            )

                            if not source_name:
                                source_name = "Unknown"

                            # Prevent duplicate source names
                            if source_name in shown_sources:
                                continue

                            shown_sources.add(source_name)

                            render_html(
                                f"""
                                <span class="source-item">
                                    ◇ &nbsp; {source_name}
                                </span>
                                """
                            )


# ============================================================
# RIGHT INFORMATION PANEL
# ============================================================

with info_column:

    render_html(
        """
        <div class="info-panel">

            <div class="info-title">
                AI Support Status
            </div>

            <div class="info-subtitle">
                CloudDesk support service
            </div>

            <div class="info-status">
                <span class="online-dot"></span>
                AI Support Active
            </div>

            <div class="info-divider"></div>

            <div class="info-label">
                Supported Categories
            </div>

            <div class="category-row">
                <div class="category-icon" style="background:#eff6ff;color:#1d4ed8;">▣</div>
                Billing
            </div>

            <div class="category-row">
                <div class="category-icon" style="background:#fff7ed;color:#c2410c;">⚒</div>
                Technical Support
            </div>

            <div class="category-row">
                <div class="category-icon" style="background:#f5f3ff;color:#6d28d9;">◇</div>
                Account Access
            </div>

            <div class="info-divider"></div>

            <div class="info-label">
                Knowledge Base
            </div>

            <div class="info-value">
                15 FAQs indexed
            </div>

            <div class="info-ready">
                ● Ready
            </div>

            <div class="info-divider"></div>

            <div class="info-label">
                AI Configuration
            </div>

            <div class="info-value">
                Confidence threshold
            </div>

            <div style="
                margin-top: 4px;
                color: #111827;
                font-size: 18px;
                font-weight: 700;
            ">
                70%
            </div>

            <div class="info-divider"></div>

            <div class="info-label">
                About
            </div>

            <div class="info-about">
                CloudDesk AI handles Tier-1 support questions
                using retrieval-augmented generation and
                escalates unsupported or low-confidence
                requests to human support.
            </div>

        </div>
        """
    )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask CloudDesk AI a question..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # --------------------------------------------
    # SHOW USER MESSAGE
    # --------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # --------------------------------------------
    # AI RESPONSE
    # --------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("CloudDesk AI is thinking..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "message": question
                    },
                    timeout=60,
                )


                # ----------------------------------------
                # SUCCESS
                # ----------------------------------------

                if response.status_code == 200:

                    result = response.json()


                    answer = result.get(
                        "answer",
                        "No answer returned.",
                    )

                    category = result.get(
                        "category",
                        "unknown",
                    )

                    confidence = result.get(
                        "confidence",
                        0.0,
                    )

                    status = result.get(
                        "status",
                        "unknown",
                    )

                    reason = result.get(
                        "reason",
                        "",
                    )

                    sources = result.get(
                        "sources",
                        [],
                    )


                    # ------------------------------------
                    # ANSWER
                    # ------------------------------------

                    st.markdown(answer)


                    # ------------------------------------
                    # META
                    # ------------------------------------

                    category_pill = category_pill_html(category)

                    meta_html = f"""
                    <div class="response-meta">

                        {category_pill}
                    """

                    try:

                        confidence_value = float(
                            confidence
                        )

                        meta_html += f"""
                        <div class="meta-pill">
                            Confidence
                            <strong>
                                {confidence_value:.0%}
                            </strong>
                        </div>
                        """

                    except (
                        TypeError,
                        ValueError,
                    ):
                        pass

                    meta_html += "</div>"

                    render_html(meta_html)


                    # ------------------------------------
                    # ANSWERED
                    # ------------------------------------

                    if status == "answered":

                        render_html(
                            """
                            <div class="grounded">
                                ✓ &nbsp; Based on CloudDesk Knowledge Base
                            </div>
                            """
                        )


                    # ------------------------------------
                    # ESCALATED
                    # ------------------------------------

                    if status == "escalated":

                        safe_reason = (
                            reason
                            if reason
                            else
                            "This question could not be answered confidently using the CloudDesk knowledge base."
                        )

                        render_html(
                            f"""
                            <div class="escalation">

                                <div class="escalation-title">
                                    Let's get a human involved
                                </div>

                                <div class="escalation-text">
                                    {safe_reason}
                                </div>

                                <div class="escalation-status">
                                    Human support recommended
                                </div>

                            </div>
                            """
                        )


                    # ------------------------------------
                    # SOURCES
                    # ------------------------------------

                    if sources:

                        render_html('<div class="sources-title">Knowledge Sources</div>')

                        shown_sources = set()

                        for source in sources:

                            if not isinstance(source, dict):
                                continue

                            source_name = source.get(
                                "source",
                                "Unknown",
                            )

                            if not source_name:
                                source_name = "Unknown"

                            if source_name in shown_sources:
                                continue

                            shown_sources.add(
                                source_name
                            )

                            render_html(
                                f"""
                                <span class="source-item">
                                    ◇ &nbsp; {source_name}
                                </span>
                                """
                            )


                    # ------------------------------------
                    # SAVE AI RESPONSE
                    # ------------------------------------

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "category": category,
                            "confidence": confidence,
                            "status": status,
                            "reason": reason,
                            "sources": sources,
                        }
                    )


                # ----------------------------------------
                # BACKEND ERROR
                # ----------------------------------------

                else:

                    st.error(
                        "Something went wrong while processing your request. "
                        "Please try again."
                    )


            # --------------------------------------------
            # CONNECTION ERROR
            # --------------------------------------------

            except requests.exceptions.ConnectionError:

                st.error(
                    "CloudDesk AI is temporarily unavailable. "
                    "Please make sure the support service is running."
                )


            # --------------------------------------------
            # TIMEOUT
            # --------------------------------------------

            except requests.exceptions.Timeout:

                st.error(
                    "The AI service took too long to respond. "
                    "Please try again."
                )


            # --------------------------------------------
            # GENERAL ERROR
            # --------------------------------------------

            except Exception:

                st.error(
                    "Something went wrong while processing your request. "
                    "Please try again."
                )