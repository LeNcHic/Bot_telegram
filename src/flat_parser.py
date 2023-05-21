import cianparser
import pandas as pd


def get_data(deal_type_, accommodation_type_, location_, rooms_):
    data = cianparser.parse(
        deal_type=deal_type_,
        accommodation_type=accommodation_type_,
        location=location_,
        rooms=rooms_,
        start_page=1,
        end_page=1,
        is_saving_csv=False,
        is_latin=False,
        is_express_mode=True,
        is_by_homeowner=False,
    )
    df = pd.json_normalize(data)
    return df


def get_top_links(data):
    return data['link'][:5]


def get_the_cheapest(data):
    buff = data.min(axis=0)
    return buff['link'][:5]


def get_the_biggest(data):
    buff = data.max(axis=0)
    return buff['total_meters'][:5]
