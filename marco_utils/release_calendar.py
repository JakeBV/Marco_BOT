import pytz
import time
from datetime import datetime
from datetime import timedelta


from num2t4ru import num2text
import pymorphy2

def days_counter(dates):
    season = dates['season']
    chapters = dates['chapters']
    birthdays = dates['birthdays']
    date_now = datetime.now(pytz.timezone('Europe/Moscow'))
    if isinstance(season, int):
        days_to_season = int((season - time.time()) / 86400 + 1)
        season_text = f'Заключительный сезон выйдет осенью 2020, примерно ' \
            f'через {days_to_season} {get_number_and_noun(days_to_season, "день").split(" ")[-1]}\n'
    else:
        episode_release_date = season[list(season)[-1]]
        episode = list(season)[-1]
        if episode_release_date < time.time():
            season_text = ''
        else:
            for episode, episode_release_date in season.items():
                if episode_release_date > time.time():
                    break
            date_episode = datetime.fromtimestamp(episode_release_date,
                                                  pytz.timezone('Europe/Moscow')).strftime('%H:%M:%S %d.%m.%Y')

            date_to_episode = datetime.strptime(f'{date_episode} +0300', '%H:%M:%S %d.%m.%Y %z') - timedelta(days=1)
            difference_in_seconds = abs(time.mktime(date_to_episode.timetuple()) - time.mktime(date_now.timetuple()))
            difference_in_minutes = difference_in_seconds / 60
            difference_in_hours = difference_in_minutes / 60
            days_to_date = int(difference_in_seconds / 86400)
            hours_to_date = int(difference_in_hours % 24)
            minutes_to_date = int(difference_in_minutes % 60)
            minutes_left = ''
            hours_left = ''
            days_left = ''
            if minutes_to_date:
                minutes_text = get_number_and_noun(minutes_to_date, "минуты").split(" ")
                if minutes_text[-2] == 'один':
                    minutes_text[-1] = 'минуту'
                minutes_left = f'{minutes_to_date} {minutes_text[-1]}'
            if hours_to_date:
                hours_left = f'{hours_to_date} {get_number_and_noun(hours_to_date, "час").split(" ")[-1]} '
            if days_to_date:
                days_left = f'{days_to_date} {get_number_and_noun(days_to_date, "день").split(" ")[-1]} '
            days_hour_minute = f'{days_left}{hours_left}{minutes_left}'.strip()
            season_text = f'{episode}-й эпизод выйдет через {days_hour_minute}.\n'
    chapter = list(chapters)[-1]
    chapter_release_date = chapters[list(chapters)[-1]]
    if chapter_release_date < time.time():
        chapter_text = ''
    else:
        for chapter, chapter_release_date in chapters.items():
            if chapter_release_date > time.time():
                break
        days_to_chapter = int((chapter_release_date - time.time()) / 86400 + 1)
        chapter_text = f'{chapter}-я глава выйдет ' \
            f'через {days_to_chapter} {get_number_and_noun(days_to_chapter, "день").split(" ")[-1]}\n'
    birthday_text = ''
    if birthdays[str(date_now.month)].get(str(date_now.day)) is not None:
        birthday_text = birthdays[str(date_now.month)][str(date_now.day)]
    now = datetime.fromtimestamp(time.time(), pytz.timezone('Europe/Moscow')).strftime('%H:%M:%S %d.%m.%Y')
    return f'<b>У меня {now} (GMT+3)</b>\n{season_text}{chapter_text}{birthday_text}'




# источник http://zabaykin.ru/?p=415
def get_number_and_noun(numeral, noun):
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse(noun)[0]
    v1, v2, v3 = word.inflect({'sing', 'nomn'}), word.inflect({'gent'}), word.inflect({'plur', 'gent'})
    return num2text(num=numeral, main_units=((v1.word, v2.word, v3.word), 'm'))






