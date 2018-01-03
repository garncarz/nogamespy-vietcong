from nogamespy import tasks


def test_pull_qtracker_txt_list():
    tasks.pull_master()


def test_pull_qtracker_master():
    tasks.pull_master('65.112.87.186')


def test_refresh_all_servers():
    tasks.refresh_all_servers()
