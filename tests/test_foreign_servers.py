import os
import pytest
import subprocess
import sys


class TestForeignMasterServers:
    """Test the FOREIGN_MASTER_SERVERS environment variable functionality"""
    
    def test_parsing_logic(self):
        """Test the parsing logic for FOREIGN_MASTER_SERVERS"""
        def parse_foreign_servers(env_value):
            """Extract the parsing logic to test it directly"""
            foreign_servers_env = env_value.strip() if env_value else ''
            if foreign_servers_env:
                return [ip.strip() for ip in foreign_servers_env.split(',') if ip.strip()]
            return []
        
        # Test cases
        test_cases = [
            ('', []),
            ('1.2.3.4', ['1.2.3.4']),
            ('1.2.3.4,5.6.7.8', ['1.2.3.4', '5.6.7.8']),
            ('1.2.3.4,5.6.7.8,9.10.11.12', ['1.2.3.4', '5.6.7.8', '9.10.11.12']),
            (' 1.2.3.4 , 5.6.7.8 , 9.10.11.12 ', ['1.2.3.4', '5.6.7.8', '9.10.11.12']),
            ('1.2.3.4,,5.6.7.8', ['1.2.3.4', '5.6.7.8']),  # Empty values filtered out
            ('  ,  ,  ', []),  # Only empty/whitespace values
        ]
        
        for input_val, expected in test_cases:
            result = parse_foreign_servers(input_val)
            assert result == expected, f"Input '{input_val}': expected {expected}, got {result}"
    
    def test_settings_with_no_foreign_servers(self):
        """Test settings loading when no FOREIGN_MASTER_SERVERS is set"""
        result = subprocess.run([
            sys.executable, '-c', 
            '''
import sys
sys.path.insert(0, "/home/runner/work/nogamespy-vietcong/nogamespy-vietcong")
from nogamespy import settings
assert settings.FOREIGN_MASTER_SERVERS == []
assert "pull_master" in settings.CELERYBEAT_SCHEDULE
assert "refresh_all_servers" in settings.CELERYBEAT_SCHEDULE
print("SUCCESS: No foreign servers configured correctly")
'''
        ], capture_output=True, text=True, env={**os.environ, 'FOREIGN_MASTER_SERVERS': ''})
        
        assert result.returncode == 0, f"Settings loading failed: {result.stderr}"
        assert 'SUCCESS' in result.stdout
    
    def test_settings_with_foreign_servers(self):
        """Test settings loading with FOREIGN_MASTER_SERVERS set"""
        result = subprocess.run([
            sys.executable, '-c', 
            '''
import sys
sys.path.insert(0, "/home/runner/work/nogamespy-vietcong/nogamespy-vietcong")
from nogamespy import settings
expected = ["1.2.3.4", "5.6.7.8"]
assert settings.FOREIGN_MASTER_SERVERS == expected
assert "pull_master_0" in settings.CELERYBEAT_SCHEDULE
assert "pull_master_1" in settings.CELERYBEAT_SCHEDULE
assert settings.CELERYBEAT_SCHEDULE["pull_master_0"]["args"] == ["1.2.3.4"]
assert settings.CELERYBEAT_SCHEDULE["pull_master_1"]["args"] == ["5.6.7.8"]
assert "refresh_all_servers" in settings.CELERYBEAT_SCHEDULE
# Should not have the default pull_master task when foreign servers are configured
assert "pull_master" not in settings.CELERYBEAT_SCHEDULE
print("SUCCESS: Foreign servers configured correctly")
'''
        ], capture_output=True, text=True, env={**os.environ, 'FOREIGN_MASTER_SERVERS': '1.2.3.4,5.6.7.8'})
        
        assert result.returncode == 0, f"Settings loading failed: {result.stderr}"
        assert 'SUCCESS' in result.stdout