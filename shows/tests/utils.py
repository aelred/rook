from shows.models import Show, Season, Episode


def episode(title, season_num, episode_num, episode_title):
    show = Show.objects.create(title=title, populated=True)
    season = Season.objects.create(show=show, num=season_num)
    return Episode.objects.create(season=season, num=episode_num,
                                  title=episode_title)
