# Latest result of each dashboard endpoint, used as context by the Ask AI chat.
dashboard_data = {
    "pipeline": {},
    "market_overview": {},
    "comparative_analysis": {},
    "recent_market_trends": {},
}


def save_dashboard_data(page, data_name, filter_key, value):
    """Stores the latest result of an endpoint in dashboard_data."""
    page_data = dashboard_data[page]

    if data_name not in page_data:
        page_data[data_name] = {}

    page_data[data_name][filter_key] = value
