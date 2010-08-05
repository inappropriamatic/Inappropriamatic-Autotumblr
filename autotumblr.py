#!/usr/bin/python
## INAPPROPRIAMATIC
## inappropriamatic.tumblr.com 
import httplib, urllib
import os
import logging
from random import choice, randint
import ConfigParser
import tempfile
import uu
import time
import shutil

CONFIG_PATH = '/home/inappropriamatic/code/autotumblr/autotumblr.config'

class AutoTumblr():
    
    def __init__(self):
        self.tumblr_url = "tumblr.com"
        self.api_path   = "/api/write"
    
        self.porn_folder = None
        self.posted_folder = None
        
        self.email = None
        self.password = None
        
        self.sub_type  = None
        self.sub_group = None
        self.sub_state = None    
        
        self.up_file = None  # the file to post
    
        self.log_filename = None
    
    
    def timestamp(self):
        """Returns a string with the current time.  Used for logging"""
        timestruct = time.localtime()
        year = timestruct[0]
        month = timestruct[1]
        day = timestruct[2]
        hour = timestruct[3]
        minute = timestruct[4]
        second = timestruct[5]
        
        return str(year) + '-' + str(month) + '-' + str(day) +"\t" + str(hour) +':' + str(minute) + ':' + str(second)
        
    
    def connect_and_post(self):
        """Connect to tumblr and send an image in an http POST.  Max file size 5mb"""
        image = open(self.up_file)

        params = urllib.urlencode({'email': self.email,
                                   'password': self.password,
                                   'type': self.sub_type,
                                   'group': self.sub_group,
                                   'state': self.sub_state,
                                   #'click-through-url' : self.sub_group,
                                   'data': image.read()
                                       })
        
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
                   
        conn = httplib.HTTPConnection(self.tumblr_url, 80)
        conn.request("POST", self.api_path, params, headers)
        response = conn.getresponse()
        logging.info(str(response.status) + "," +  str(response.reason))


        if response.status == 201:
            self.move_file()
        else:
            logging.info("-- Failed --" + str(response.read()) )
        
        
        conn.close()
    
    
    def choose_file(self):
        """Pick a file randomly out of your porn folder"""
        files = os.listdir(self.porn_folder)
        
        if "posted" in files:
            files.remove("posted")
            
        self.up_file = str(self.porn_folder) + "/" + choice(files)
        
        logging.info("Chose file " + str(self.up_file))
        
    

    def move_file(self):
        """Move a file and add a random prefix (as no to clobber files with similar names"""
        dest = self.posted_folder + '/' + str(randint(1,900000)) + '___' + self.up_file
        shutil.move(self.up_file, dest)
        logging.info("File renamed and moved to " + dest)
    
    

    def configure(self):
        """Read in the configuration file, set up logging"""
        confp = ConfigParser.ConfigParser()
        
        confp.readfp(open(CONFIG_PATH))
        
        self.porn_folder = confp.get("directories", "porn-folder", 0)
        self.posted_folder = confp.get("directories", "posted-folder", 0)
        
        self.email = confp.get("credentials", "email", 0)
        self.password = confp.get("credentials", "password", 0)
        
        
        self.sub_type = confp.get("submission", "type", 0)
        self.sub_group = confp.get("submission", "group", 0)
        self.sub_state = confp.get("submission", "state", 0)
        
        
        # set up logging
        self.log_filename = confp.get("logging", "logfile")
        logging.basicConfig(filename=self.log_filename,level=logging.DEBUG, filemode='a')
        
        logging.info(self.timestamp())
        
    
    
    def run(self):
        self.configure()
        self.choose_file()
        self.connect_and_post()
        
        
        
if __name__ == "__main__":
    at = AutoTumblr()
    at.run()
