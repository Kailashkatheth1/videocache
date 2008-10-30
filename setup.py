#!/usr/bin/env python

from youtube_cache.config import readMainConfig, readStartupConfig
import logging
import logging.handlers
import os
import pwd
import shutil
import sys

config_file = './youtube_cache_sysconfig.conf'
setup_logfile = './youtube_cache_setup.log'
squid_user = 'squid'
squid_group = 'squid'
squid_conf_dir = '/etc/squid/'
squid_log_dir = '/var/log/squid'
apache_conf_dir = '/etc/httpd/conf.d/'
man_dir = '/usr/share/man/man8/'
mainconf =  readMainConfig(readStartupConfig(config_file, '/'))

# Gloabl Options
base_dir = mainconf.base_dir
temp_dir = os.path.join(base_dir, mainconf.temp_dir)
logfile = mainconf.logfile
pidfile = mainconf.pidfile
format = '%s'

USAGE_ERROR = 1
UID_ERROR = 2
INSTALL_ERROR = 3

# Youtube specific options
youtube_cache_dir = os.path.join(base_dir, mainconf.youtube_cache_dir)

# Metacafe specific options
metacafe_cache_dir = os.path.join(base_dir, mainconf.metacafe_cache_dir)

# Dailymotion specific options
dailymotion_cache_dir = os.path.join(base_dir, mainconf.dailymotion_cache_dir)

# Google.com specific options
google_cache_dir = os.path.join(base_dir, mainconf.google_cache_dir)

# Redtube.com specific options
redtube_cache_dir = os.path.join(base_dir, mainconf.redtube_cache_dir)

# Xtube.com specific options
xtube_cache_dir = os.path.join(base_dir, mainconf.xtube_cache_dir)

# Vimeo.com specific options
vimeo_cache_dir = os.path.join(base_dir, mainconf.vimeo_cache_dir)

# List of cache directories
squid_cache_dir_list = [base_dir, temp_dir, youtube_cache_dir, metacafe_cache_dir, dailymotion_cache_dir, google_cache_dir, redtube_cache_dir, xtube_cache_dir, vimeo_cache_dir]

def set_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename=setup_logfile,
                        filemode='w')
    return logging.info

def create_dir(dir, user=None, group=None, mode=0644):
    """Create a directory in the filesystem with user:group ownership and mode as permissions."""
    try:
        os.makedirs(dir, mode)
        log(format%("Created directory " + dir + " ."))
    except:
        log(format%("Could not create directory " + dir + " ."))
        return False

    if user == None:
        return True

    user = pwd.getpwnam(user)[2]
    if group != None:
        group = pwd.getpwnam(group)[3]
    else:
        group = user

    try:
        os.chown(dir, user, group)
        log(format%("Changed ownership of " + dir + " ."))
    except:
        log(format%("Could not change ownership of directory " + dir + " ."))
        return False

    return True

def create_file(filename, user=None, group=None, mode=0644):
    """Create a file in the filesystem with user:group ownership and mode as permissions."""
    try:
        file = open(filename, 'a')
        file.close()
        log(format%("Created file " + filename + " ."))
    except:
        log(format%("Could not create file " + filename + " ."))
        return False
    
    try:
        os.chmod(filename, mode)
        log(format%("Changed mode of file " + filename + " ."))
    except:
        log(format%("Could not change the mode of the file " + filename + " ."))
        return False

    if user == None:
        return True

    user = pwd.getpwnam(user)[2]
    if group != None:
        group = pwd.getpwnam(group)[3]
    else:
        group = user

    try:
        os.chown(filename, user, group)
        log(format%("Changed ownership of file " + filename + " ."))
    except:
        log(format%("Could not change ownership of file " + filename + " ."))
        return False
    return True

def copy_file(source, dest):
    """Copies the source file to dest file."""
    try:
        shutil.copy2(source, dest)
        log(format%("Copied file " + source + " to " + dest + " ."))
    except:
        log(format%("Could not copy the file " + source + " to file " + dest + " ."))
        return False
    return True

def copy_dir(source, dest):
    """Copies the source directory recursively to dest dir."""
    try:
        if os.path.isdir(dest):
            shutil.rmtree(dest)
            log(format%("Removed already existing directory " + dest + " ."))
    except:
        log(format%("Could not remove the already existing destination directory " + dest + " ."))
        return False
    try:
        shutil.copytree(source, dest)
        log(format%("Copied source directory " + source + " to " + dest + " ."))
    except:
        log(format%("Could not copy directory " + source + " to " + dest + " ."))
        return False
    return True

def generate_httpd_conf():
    """Generates /etc/httpd/conf.d/youtube_cache.conf for apache web server for serving videos."""
    conf_file = os.path.join(apache_conf_dir, 'youtube_cache.conf')
    youtube_cache_conf = """
#
# file : """ + conf_file + """
#
# youtube_cache is a squid url rewriter plugin to cache youtube/metacafe/dailymotion/redtube/xtube/vimeo.com videos.
#

# ------------------- Note This --------------------
# Don't forget to reload httpd and squid services if you change this file.

Alias /video_cache """ + base_dir +"""

<Directory """ + base_dir + """>
  Order Allow,Deny
  #Comment the following line and uncomment the next for public use 
  #Deny from all
  Allow from all
</Directory>
    """

    try:
        file = open(conf_file, 'w')
        file.write(youtube_cache_conf)
        file.close()
        log(format%("Generated config file for Apache webserver in file " + config_file + " ."))
    except:
        log(format%("Could not write config file for apache web server to " + config_file + " ."))
        return False
    return True

def error(error_code):
    """Report error while updating/installing youtube_cache with proper error code."""
    help_message =  """
Usage: python setup.py install (as root/super user)
Please see http://fedora.co.in/youtube_cache/ for more information or getting help.
    """
    install_error =  """
An error has occured while installing youtube_cache.
Please check youtube_cache_setup.log for more details.
Please see http://fedora.co.in/youtube_cache/ for more information or getting help.
    """
    uid_error = """
You must be root to setup/install youtube_cache.
Please see http://fedora.co.in/youtube_cache/ for more information or getting help.
    """
    if error_code == INSTALL_ERROR:
        print install_error
        sys.exit(error_code)
    if error_code == UID_ERROR:
        print uid_error
        sys.exit(UID_ERROR)
    if error_code == USAGE_ERROR:
        print help_message
        sys.exit(USAGE_ERROR)
    return

def success():
    """Print informative messages after successfull installation."""
    message = """
Youtube cache setup has completed successfully.
Now you must reload httpd service on your machine by using the following command
[root@localhost ~]# service httpd reload [ENTER]
Also, you need to configure squid so that it can use youtube_cache as a url rewritor plugin.
Check README file for further configurations of squid, httpd and youtube_cache.
In case of any bugs or problems, check http://fedora.co.in/youtube_cache/ .
    """
    print message

def setup():
    """Perform the setup."""
    if not os.path.isdir(squid_conf_dir):
        if not create_dir(apache_conf_dir):
            error(INSTALL_ERROR)
    else:
        log(format%("Directory " + squid_conf_dir + " already exists."))

    if not os.path.isdir(squid_log_dir):
        if not create_dir(squid_log_dir, squid_user, squid_group):
            error(INSTALL_ERROR)
    else:
        log(format%("Directory " + squid_log_dir + " already exists."))

    for dir in squid_cache_dir_list:
        if not os.path.isdir(dir):
            if not create_dir(dir, squid_user, squid_group, 0755):
                error(INSTALL_ERROR)
        else:
            log(format%("Directory " + dir + " already exists."))

    if not os.path.isdir(man_dir):
        if not create_dir(man_dir):
            error(INSTALL_ERROR)
    else:
        log(format%("Directory " + man_dir + " already exists."))

    if not copy_dir('./youtube_cache/', os.path.join(squid_conf_dir, 'youtube_cache')):
        error(INSTALL_ERROR)

    if not copy_file('./youtube_cache_sysconfig.conf', '/etc/youtube_cache.conf'):
        error(INSTALL_ERROR)

    if not copy_file('./youtube_cache.8.gz', os.path.join(man_dir, 'youtube_cache.8.gz')):
        error(INSTALL_ERROR)

    if not create_file(os.path.join(squid_log_dir, 'youtube_cache.log'), squid_user, squid_group):
        error(INSTALL_ERROR)

    if not create_file(os.path.join(squid_log_dir, 'youtube_cache.pid'), squid_user, squid_group):
        error(INSTALL_ERROR)

    if not generate_httpd_conf():
        error(INSTALL_ERROR)

    success()
    return

if __name__ == '__main__':
    log = set_logging()
    if len(sys.argv) == 2:
        if sys.argv[1] == 'install':
            if os.getuid() != 0:
                log(format%("You must be root to install/setup youtube_cache."))
                error(UID_ERROR)
            else:
                setup()
        else:
            error(USAGE_ERROR)
    else:
        error(USAGE_ERROR)
