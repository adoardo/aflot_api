async def format_date(date_obj) -> str:
    month_names = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }

    formatted_date = f"{date_obj.day} {month_names[date_obj.month]} {date_obj.year}"
    return formatted_date
