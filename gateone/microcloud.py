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
import requests

from auth import BaseAuthHandler

# Localization support
_ = get_translation()

class MicrocloudAuthHandler(BaseAuthHandler):
  @tornado.web.asynchronous
  def get(self):
    check = self.get_argument("check", None)
    if check:
      # TODO testing user session contents
      logging.debug("*** microcloud check lab")
      logging.debug(self.get_secure_cookie('gateone_user'))

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

    # TODO microcloud endpoint from environment
    # TODO check if it's valid / set
    endpoint = os.environ['MICROCLOUD']

    # parse lab token from domain name
    hostname = self.request.host.split(':')[0]

    # TODO harcoded domains & better checking
    if hostname.endswith('.demo.10xlabs.net'):
      lab_token = hostname.split('.')[0]
    else:
      lab_token = None

    # FIXME handle invalid tokens
    logging.debug("Authention for lab " + lab_token)

    # TODO verify lab_token before storing in session
    #      throw error on 404/401
    # http://docs.python-requests.org/en/latest/index.html
    #req = requests.get(endpoint + "/labs/" + lab_token)
    #lab = req.json

    #if not 'vms' in lab:
    #  lab['vms'] = []
    
    self.user_login('10xeng', lab_token)
    
    next_url = self.get_argument("next", None)
    if next_url:
      self.redirect(next_url)
    else:
      self.redirect(self.settings['url_prefix'])

  def user_login(self, user, lab_token):
    """
    Called immediately after a user authenticates successfully.  Saves
    session information in the user's directory.  Expects *user* to be a
    string containing the username or userPrincipalName. e.g. 'user@REALM'
    or just 'someuser'.
    """
    logging.debug("!!!! microcloud user_login(%s)" % user)
    # Make a directory to store this user's settings/files/logs/etc
    user_dir = os.path.join(self.settings['user_dir'], user)
    logging.debug("user_dir = %s " % user_dir)
    if not os.path.exists(user_dir):
        logging.info(_("Creating user directory: %s" % user_dir))
        mkdir_p(user_dir)
        os.chmod(user_dir, 0o700)

    session_file = os.path.join(user_dir, 'session')
    session_file_exists = os.path.exists(session_file)
    if session_file_exists:
        session_data = open(session_file).read()
        try:
            session_info = tornado.escape.json_decode(session_data)
        except ValueError: # Something wrong with the file
            session_file_exists = False # Overwrite it below
    if not session_file_exists:
        with open(session_file, 'w') as f:
            # Save it so we can keep track across multiple clients
            session_info = {
                'upn': user, # FYI: UPN == userPrincipalName
                'session': generate_session_id(),
                'lab': lab_token
            }
            session_info_json = tornado.escape.json_encode(session_info)
            f.write(session_info_json)
    self.set_secure_cookie(
        "gateone_user", tornado.escape.json_encode(session_info))

    
  
