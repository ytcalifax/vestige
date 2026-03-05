from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

BASE_URL: str = "https://dv.parliament.bg/DVWeb/broeveList.faces"
BASE_HOST: str = "https://dv.parliament.bg/DVWeb/"

DEFAULT_HEADERS: dict[str, str] = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://dv.parliament.bg",
    "Pragma": "no-cache",
    "Referer": "https://dv.parliament.bg/DVWeb/broeveList.faces",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
}

# ---------------------------------------------------------------------------
# Form field keys (POST body)
# ---------------------------------------------------------------------------

FIELD_ACTIVE_TAB: str = "active_tab"
FIELD_NOT_FIRST: str = "broi_form:not_first"
FIELD_JSP61: str = "broi_form:_idJsp61"
FIELD_JSP67: str = "broi_form:_idJsp67"
FIELD_JSP69: str = "broi_form:_idJsp69"
FIELD_FROM_DATE: str = "broi_form:from_date"
FIELD_TO_DATE: str = "broi_form:to_date"
FIELD_PERIOD: str = "broi_form:period_"
FIELD_SELECT_PAGE_TOP: str = "broi_form:selectPageTop"
FIELD_SELECT_PAGE: str = "broi_form:selectPage"
FIELD_FORM_SUBMIT: str = "broi_form_SUBMIT"
FIELD_LINK_HIDDEN: str = "broi_form:_link_hidden_"
FIELD_DATE_IZD: str = "date_izd_"
FIELD_IDCL: str = "broi_form:_idcl"
FIELD_ID_: str = "id_"
FIELD_ID_OBJ: str = "idObj"
FIELD_RAZDEL: str = "razdel_"
FIELD_BROI: str = "broi_"
FIELD_VIEW_STATE: str = "javax.faces.ViewState"

VALUE_ACTIVE_TAB: str = "2"
VALUE_NOT_FIRST: str = "1"
VALUE_FORM_SUBMIT: str = "1"
VALUE_CHANGE_PAGE_CMD: str = "broi_form:chP"

# ---------------------------------------------------------------------------
# HTML element identifiers
# ---------------------------------------------------------------------------

TABLE_ID: str = "broi_form:dataTable1"
TBODY_ID: str = "broi_form:dataTable1:tbody_element"
SELECT_PAGE_ID: str = "broi_form:selectPage"
VIEW_STATE_NAME: str = "javax.faces.ViewState"
RESULTS_SPAN_CLASS: str = "mark"

LINK_CONTENT_ID_SUFFIX: str = "_idJsp101"
LINK_DOWNLOAD_ID_SUFFIX: str = "_idJsp109"
DOWNLOAD_TBODY_PATTERN: str = r"broi_form:_idJsp\d+:tbody_element"
DOWNLOAD_HREF_PATTERN: str = r"fileUploadShowing"

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Matches text like:  Брой 23, 27.2.2026 г.
# or:                 Брой 21, 21.2.2026 г. (извънреден)
ISSUE_RE: re.Pattern[str] = re.compile(
    r"Брой\s+(\d+),\s+([\d.]+\.\d{4})\s+г\.(?:\s*\((\S+)\))?",
    re.UNICODE,
)

# Extract parameters from onclick JS:
#   [['broi_','23'],['idObj','12386'],['date_izd_','2026-02-27'],['razdel_','1']]
ONCLICK_PARAM_RE: re.Pattern[str] = re.compile(
    r"\['(broi_|idObj|date_izd_|razdel_|id_)'\s*,\s*'([^']*)'\]"
)

RESULTS_TEXT_RE: re.Pattern[str] = re.compile(r"Намерени")
RESULTS_NUMBER_RE: re.Pattern[str] = re.compile(r"(\d+)")

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

FIRST_PAGE: int = 1

