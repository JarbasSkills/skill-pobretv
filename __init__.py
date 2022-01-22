from ovos_plugin_common_play.ocp import MediaType, PlaybackType
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    ocp_search, ocp_featured_media
import requests
import bs4
from ovos_utils.parse import fuzzy_match
import random


class PobreTVSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("PobreTV")
        self.supported_media = [MediaType.MOVIE, MediaType.GENERIC]
        self.skill_icon = self.default_bg = "https://www1.pobre.tv/images/logo.png"
        self._featured_movies = []

    def initialize(self):
        # pre-parse for speed
        try:
            self.featured_media()
        except:
            pass

    def _search_pobretv(self, query):
        # this is a wild workaround, we cant search, but urls are generated from imdb ids
        # we serch themoviedb, extract imdb id for the movie, and check if pobre.tv entry exists
        sess = requests.Session()  # TODO requests cache
        url = 'https://api.themoviedb.org/3/search/movie'
        params = {
            "query": query,
            "api_key": "ffb07b773769d55c36ccd83845385205",
            "type": "movie",
            "language": "en-US",
            "include_adult": False
        }
        for r in sess.get(url, params=params).json()["results"]:
            movie_url = f'https://api.themoviedb.org/3/movie/{r["id"]}'
            params = {
                "api_key": "ffb07b773769d55c36ccd83845385205",
                "language": "en-US"
            }
            movie_data = sess.get(movie_url, params=params).json()
            url = f"https://www1.pobre.tv/movies/{movie_data['imdb_id']}"
            if not movie_data['imdb_id']:
                continue
            html = sess.get(url).text
            if "<title>POBRE.TV 404</title>" in html:
                continue
            pic = html.split('content="https://image.tmdb.org/')[-1].split('"/>')[0]
            yield {
                "title": r["title"],
                "image": f"https://image.tmdb.org/{pic}",
                "url": url
            }

    @property
    def javascript(self):
        return """
        document.body.style.overflow = 'hidden';
        document.getElementsByClassName("movieInfos")[0].remove();
        document.getElementById("topBar").remove();
        document.getElementsByClassName("pageNavigator")[1].remove();
        document.getElementsByClassName("pageNavigator")[0].remove();
        document.getElementsByClassName("wrap")[2].remove();
        document.getElementsByClassName("wrap")[1].remove();
        """

    @ocp_featured_media()
    def featured_media(self):
        if not self._featured_movies:
            r = requests.get("https://www1.pobre.tv")
            html = r.text
            soup = bs4.BeautifulSoup(html, parser="html.parser")
            self._featured_movies = [{
                "title": a["title"],
                "image": a.find("img")["src"],
                "match_confidence": 80,
                "media_type": MediaType.MOVIE,
                "uri": a["href"],
                "playback": PlaybackType.WEBVIEW,
                "skill_icon": self.skill_icon,
                "bg_image": a.find("img")["src"],
                "skill_id": self.skill_id,
                "javascript": self.javascript,  # webview can run javascript on page load
            } for a in soup.find_all("a", {"class": "gPoster"}) if "movies/" in a["href"]]
        return self._featured_movies

    # matching
    def match_skill(self, phrase, media_type):
        score = 0
        if self.lang.startswith("pt"):
            score += 10
        if self.voc_match(phrase, "pobretv"):
            score += 50
        if self.voc_match(phrase, "movie") or media_type == MediaType.MOVIE:
            score += 15
        return score

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = self.match_skill(phrase, media_type)
        phrase = self.remove_voc(phrase, "pobretv")
        phrase = self.remove_voc(phrase, "movie")
        for ch in self._search_pobretv(phrase):
            score = base_score + fuzzy_match(ch["title"], phrase) * 100
            yield {
                "match_confidence": score,
                "media_type": MediaType.MOVIE,
                "uri": ch["url"],
                "playback": PlaybackType.WEBVIEW,
                "skill_icon": self.skill_icon,
                "image": ch["image"],
                "bg_image": ch["image"],
                "title": ch["title"],
                "author": "PobreTV"
            }


def create_skill():
    return PobreTVSkill()
