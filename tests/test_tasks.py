from nogamespy import tasks
from nogamespy.database import db_session
from nogamespy import models
import factories


def test_pull_qtracker_txt_list():
    tasks.pull_master()


def test_pull_qtracker_master():
    tasks.pull_master('65.112.87.186')


def test_refresh_all_servers():
    tasks.refresh_all_servers()


def test_after_all_servers_are_refreshed_fixes_offline_since_none():
    """Test that servers with offline_since=None are set to online=True"""
    # Create a server that has inconsistent state: offline but never went offline
    server = factories.Server(online=False, offline_since=None)
    
    db_session.add(server)
    db_session.commit()
    
    # The server should start with inconsistent state
    assert server.online == False
    assert server.offline_since is None
    
    # Call the function that should fix the inconsistent state
    tasks.after_all_servers_are_refreshed([])
    
    # Refresh the server object from database
    db_session.refresh(server)
    
    # The server should now be marked as online since offline_since is None
    assert server.online == True
    assert server.offline_since is None
