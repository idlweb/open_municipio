from fabric.api import cd, env, execute, hide, put, require, roles, run, sudo, task
from fabric.utils import fastprint

from venv import run_venv

import os


## Webserver management
@task
@roles('web')
def reload():    
    """
    Reload the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Reloading Nginx webserver..." % env, show_prefix=True)
        sudo('/etc/init.d/nginx reload')
        fastprint(" done." % env, end='\n')


@task
@roles('web')
def start():    
    """
    Start the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Starting Nginx webserver..." % env, show_prefix=True)
        sudo('/etc/init.d/nginx start')
        fastprint(" done." % env, end='\n')  


@task
@roles('web')
def stop():    
    """
    Stop the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Stopping Nginx webserver..." % env, show_prefix=True)
        sudo('/etc/init.d/nginx stop')
        fastprint(" done." % env, end='\n')  


@task
@roles('web')
def restart():    
    """
    Restart the webserver on the remote host.
    """
    with hide('stdout', 'running'):
        fastprint("Restarting Nginx webserver...", show_prefix=True)
        sudo('/etc/init.d/nginx restart')
        fastprint(" done." % env, end='\n')  


@task
@roles('om')
def enable_site(site_name):
    """
    Enable a webserver's virtualhost.
    """
    with hide('stdout', 'running'):
        fastprint("Enabling site %s..." % site_name, show_prefix=True)
#        sudo('nginx_ensite %s' % site_name)
        with cd('/etc/nginx/sites-enabled'):
            sudo('ln -fs ../sites-available/%s .' % site_name)
        fastprint(" done." % env, end='\n')  
  

@task
@roles('om')
def disable_site(site_name):
    """
    Disable a webserver's virtualhost.
    """
    with hide('stdout', 'running'):
        fastprint("Disabling site %s..." % site_name, show_prefix=True)
#        sudo('a2dissite %s' % site_name)
        with cd('/etc/nginx/sites-enabled'):
            sudo('rm %s' % site_name)
        fastprint(" done." % env, end='\n')  
      

@task
@roles('om')
def upload_conf():
    """
    Upload webserver configuration to the remote host.
    """
    require('environment', provided_by=('staging', 'production'))
    ## upload custom Nginx directives
    fastprint("Uploading vhost configuration for %(app_domain)s..." % env, show_prefix=True)
    with hide('stdout', 'running'):
#        source = os.path.join(env.local_repo_root, 'apache', 'httpd.conf.%(environment)s' % env)
#        with cd('/etc/apache2'):
#            dest = 'httpd.conf'
#            put(source, dest, use_sudo=True, mode=0644)
#            sudo('chown root:root %s' % dest)
        ## upload Virtual Host configuration
        source = os.path.join(env.local_repo_root, 'nginx', 'vhost.conf.%(environment)s' % env)
        with cd('/etc/nginx/sites-available'):
            dest = env.app_domain
            put(source, dest, use_sudo=True, mode=0644)
            sudo('chown root:root %s' % dest)
    fastprint(" done." % env, end='\n')
    
    
@task 
@roles('om')
def update_conf():
    """
    Update webserver configuration on the remote host.
    """
    # TODO add the following
    # upload uwsgi conf
    # start uwsgi
    # reload/start uwsgi
    # 
    execute(upload_conf_uwsgi)
    execute(reload_uwsgi)
    execute(upload_conf)
    execute(enable_site, site_name=env.app_domain)

@task
@roles('om')
def touch_WSGI_script():
    """
    Touch WSGI script to trigger code reload.
    """
    require('domain_root', provided_by=('staging', 'production'))
    fastprint("Triggering code reload..." % env, show_prefix=True)
    with hide('stdout', 'running'):
        nginx_dir = os.path.join(env.domain_root, 'private', 'nginx')
        with cd(nginx_dir):
            run('touch django.wsgi')
    fastprint(" done." % env, end='\n')
    
    
@task
@roles('om')
def clear_logs():
    """
    Clear website-specific logs.
    """
    require('domain_root', provided_by=('staging', 'production'))
    fastprint("Clearing old webserver logs..." % env, show_prefix=True)
    with hide('stdout', 'running'):
        with cd(env.domain_root):
            run('rm -f log/*')
    fastprint(" done." % env, end='\n')

@task
@roles('om')
def stop_uwsgi():
    """
    Kill the master instance of a running uwsgi process
    """
    require('domain_root', provided_by=('staging', 'production'))
    fastprint("Killing running instance of uwsgi ..." % env, show_prefix=True)
    with hide('stdout','running'):
        with cd(env.domain_root):
            run_venv('[ -e "./private/nginx/open_municipio.pid" ] && uwsgi --stop ./private/nginx/open_municipio.pid')
    fastprint(" done." % env, end='\n')


@task
@roles('om')
def reload_uwsgi():
    """
    Reload the master instance of a running uwsgi process
    """
    require('domain_root', provided_by=('staging', 'production'))
    fastprint("Reloading running instance of uwsgi ..." % env, show_prefix=True)
    with hide('stdout','running'):
        with cd(env.domain_root):
            run_venv('uwsgi --reload ./private/nginx/open_municipio.pid')
    fastprint(" done." % env, end='\n')


@task
@roles('om')
def start_uwsgi():
    """
    Start a uwsgi instance for the deployed site
    """
    require('domain_root', provided_by=('staging', 'production'))
    require('project', provided_by=('staging', 'production'))

    fastprint("Starting running instance of uwsgi ..." % env, show_prefix=True)
    with hide('stdout','running'):
        with cd(os.path.join(env.domain_root,'private','nginx')):
            # fab does not work well with background processes,
            # see https://github.com/fabric/fabric/issues/395
            # add a sleep is a workaround

            run_venv('nohup uwsgi --ini %(project)s.uwsgi.ini & sleep 3; exit 0' % env)         
    fastprint(" done." % env, end='\n')

 
@task
@roles('om')
def upload_conf_uwsgi():
    """
    Upload ini file for uwsgi
    """
    ## upload Virtual Host configuration
    require('domain_root', provided_by=('staging', 'production'))
    require('app_domain', provided_by=('staging', 'production'))

    source = os.path.join(env.local_repo_root, 'nginx', '%(project)s.uwsgi.ini' % env)
    with cd(os.path.join(env.domain_root, 'private', 'nginx')):
        dest = "%(project)s.uwsgi.ini" % env
        put(source, dest, use_sudo=False, mode=0644)
    fastprint(" done." % env, end='\n')
 
