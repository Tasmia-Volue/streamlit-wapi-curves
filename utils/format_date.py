import pandas as pd

def format_date(data):
    for k in ['created', 'modified']:
        if k in data:
            try:
                dt = pd.to_datetime(data[k])
                data[k] = dt.strftime("%d %b %Y, %I:%M %p %Z")
            except Exception as e:
                pass

    return data
