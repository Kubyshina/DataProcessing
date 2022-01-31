import scrapy
import json
import re
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'
    inst_passw = '#PWD_INSTAGRAM_BROWSER:10:1643131213:AZZQAGTPs6xfu+lt7ppOoFuIqKbWrZ4VaEX53g+SZCn8PJlFrepy7g4RoBJ9hG8g+yNb2R3TWGMrJek2u4SWHgpXYJPp7CijVJirea6j+tAGshfXR9HonVrpXtM9HF0oH+v2RlGNdeDqkBSgLuKb'
    users_for_parse = ['artificial_intelligence.23', 'gnaneswarrao_pappapa']
    api_url = 'https://i.instagram.com/api/v1'
    posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_passw},
                                 headers={'X-CSRFToken': csrf_token})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            #for user in self.users_for_parse:
            #    yield response.follow(f'/{user}',
            #                          callback=self.followers_parse,
            #                          cb_kwargs={'username': deepcopy(user)})
            for user in self.users_for_parse:
                yield response.follow(f'/{user}',
                                      callback=self.following_parse,
                                      cb_kwargs={'username': deepcopy(user)})

    def followers_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url = f'{self.api_url}/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page'
        print(url)

        yield response.follow(url,
                              callback=self.user_followers_parse,
                              cb_kwargs={'username': deepcopy(username),
                                         'user_id': deepcopy(user_id),
                                         'pages': 12},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def following_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url = f'{self.api_url}/friendships/{user_id}/following/?count=12'
        print(url)

        yield response.follow(url,
                              callback=self.user_following_parse,
                              cb_kwargs={'user_id': deepcopy(user_id),
                                         'pages': 12},
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'})

    def user_followers_parse(self, response: HtmlResponse, username, user_id, pages):
        j_data = response.json()
        page_info = j_data.get('big_list')
        if page_info:
            url = f'{self.api_url}/friendships/{user_id}/followers/?count=12&max_id={pages}&search_surface=follow_list_page'

            yield response.follow(url,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'username': deepcopy(username),
                                             'user_id': user_id,
                                             'pages': deepcopy(pages + 12)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_id = user_id,
                follower_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url')
            )
            yield item

    def user_following_parse(self, response: HtmlResponse, user_id, pages):
        j_data = response.json()
        page_info = j_data.get('big_list')
        if page_info:
            url = f'{self.api_url}/friendships/{user_id}/following/?count=12&max_id={pages}'

            yield response.follow(url,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'user_id': user_id,
                                             'pages': deepcopy(pages + 12)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_id=user_id,
                following_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url')
            )
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
