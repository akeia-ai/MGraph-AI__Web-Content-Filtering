
from osbot_utils.utils.Env import not_in_github_action

def skip__if_not__in_github_actions():
    import pytest
    if not_in_github_action():
        pytest.skip('For performance reasons only run this test in GitHub Actions')