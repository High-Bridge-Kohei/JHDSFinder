class Event:
    INIT_UI = "Initialize UI!"
    EASY_SETTING_CONDITION_CHANGED = "Easy setting condition changed!"
    DETAIL_SETTING_CONDITION_CHANGED = "Detail setting condition changed!"
    EASY_SETTING_CHECKED = "Easy setting checked!"
    EASY_SETTING_UNCHECKED = "Easy setting unchecked!"
    DETAIL_SETTING_CHECKED = "Detail setting checked!"
    DETAIL_SETTING_UNCHECKED = "Detail setting unchecked!"

    GETTING_EASY_CONDITION_EVENTS = [
        INIT_UI,
        EASY_SETTING_CONDITION_CHANGED,
        EASY_SETTING_CHECKED,
    ]
    GETTING_DETAIL_CONDITION_EVENTS = [
        DETAIL_SETTING_CHECKED,
    ]
    CONDITION_CHANGED = GETTING_EASY_CONDITION_EVENTS + GETTING_DETAIL_CONDITION_EVENTS

    COMPANY_SELECTED_ON_TABLE = "Company selected on table!"
    COMPANY_CODE_ENTERED = "Company code entered!"

    COMPANY_CODE_CHANGED = [COMPANY_CODE_ENTERED, COMPANY_SELECTED_ON_TABLE]
