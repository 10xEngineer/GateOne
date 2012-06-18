# -*- coding: utf-8 -*-

# Import stdlib stuff
import os
import logging

# Import our own stuff
from utils import mkdir_p, generate_session_id
from utils import get_translation

# 3rd party imports
import tornado.web
import tornado.auth
import tornado.escape

from auth import BaseAuthHandler

# Localization support
_ = get_translation()

class MicrocloudAuthHandler(BaseAuthHandler):
  @tornado.web.asynchronous
  def get(self):
    logging.info("Microcloud::get")
    check = self.get_argument("check", None)
    if check:
      self.set_header ('Access-Control-Allow-Origin', '*')
      user = self.get_current_user()
      if user:
        self.write('authenticated')
      else:
        self.write('unauthenticated')
      self.finish()
      return
    
    logout = self.get_argument("logout", None)
    if logout:
      self.clear_cookie('gateone_user')
      self.user_logout('10xeng')
      return

    self.user_login('10xeng')
    
    next_url = self.get_argument("next", None)
    if next_url:
      self.redirect(next_url)
    else:
      self.redirect(self.settings['url_prefix'])

  
