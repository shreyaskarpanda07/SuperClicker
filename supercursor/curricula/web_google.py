"""
Google Workspace & Web Productivity Curriculum for SuperCursor.
Covers Google Docs, Sheets, Search tools, and general browser productivity.
"""

CURRICULUM = {
    "name": "Google & Web Productivity",
    "target_apps": ["chrome", "msedge", "firefox", "brave", "browser", "google_workspace"],
    "lessons": [
        {
            "id": "google_sheets_formulas",
            "title": "Google Sheets: Formulas & Pivot Tables",
            "description": "Master VLOOKUP/XLOOKUP, conditional formatting, and interactive pivot tables.",
            "steps": [
                {
                    "step": 1,
                    "target": "Formula Bar",
                    "spoken": "Click into the formula bar at the top or type equals to begin entering a function.",
                    "label": "Formula Bar (fx)",
                    "shortcut": "=",
                    "action": "type"
                },
                {
                    "step": 2,
                    "target": "Insert Menu / Pivot Table",
                    "spoken": "Go to Insert on the top menu bar and choose Pivot Table to aggregate your dataset.",
                    "label": "Insert > Pivot Table",
                    "action": "click"
                },
                {
                    "step": 3,
                    "target": "Sharing & Access Permissions",
                    "spoken": "Click the green Share button in the top right to grant viewer or editor permissions.",
                    "label": "Share Document",
                    "action": "click"
                }
            ]
        },
        {
            "id": "google_search_power_tools",
            "title": "Google Advanced Search Operators",
            "description": "Find exact files, documentation, and research papers instantly without clutter.",
            "steps": [
                {
                    "step": 1,
                    "target": "Search Input Box",
                    "spoken": "Use operators like site colon, filetype colon pdf, or quotation marks for verbatim matches.",
                    "label": "Advanced Search Filter",
                    "action": "type"
                },
                {
                    "step": 2,
                    "target": "Search Tools & Date Filter",
                    "spoken": "Click Tools underneath the search bar to filter results by Past Year or custom date ranges.",
                    "label": "Tools > Any Time",
                    "action": "click"
                }
            ]
        }
    ]
}
