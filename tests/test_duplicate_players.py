"""
Test for the duplicate player records issue.

This test verifies that removing force_pull=True from the heartbeat handler
prevents duplicate player records from being created.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

# Mock pygeoip before importing tasks to avoid GeoIP.dat file dependency
with patch('pygeoip.GeoIP'):
    from nogamespy import models, tasks, protocol
    from nogamespy.database import db_session


class TestDuplicatePlayersIssue:
    """Test the duplicate player records issue and fix."""

    def setup_method(self):
        """Clean up database before each test."""
        # Clean up any existing data
        db_session.query(models.Player).delete()
        db_session.query(models.Server).delete() 
        db_session.query(models.Map).delete()
        db_session.query(models.Mode).delete()
        db_session.commit()

    def test_register_without_force_pull_prevents_duplicates(self):
        """Test that register without force_pull doesn't pull existing servers."""
        # Create a server
        server, created = models.get_or_create(models.Server, ip='192.168.1.1', info_port=5555)
        assert created
        db_session.commit()
        
        # Mock pull_server_info to track calls
        with patch('nogamespy.tasks.pull_server_info') as mock_pull:
            mock_pull.return_value = True
            
            # Call register without force_pull (existing server)
            result = tasks.register('192.168.1.1', 5555, force_pull=False)
            
            # Should return True but not call pull_server_info
            assert result is True
            mock_pull.assert_not_called()

    def test_register_with_force_pull_always_pulls(self):
        """Test that register with force_pull always pulls server info."""
        # Create a server
        server, created = models.get_or_create(models.Server, ip='192.168.1.2', info_port=5556)
        assert created
        db_session.commit()
        
        # Mock pull_server_info to track calls
        with patch('nogamespy.tasks.pull_server_info') as mock_pull:
            mock_pull.return_value = True
            
            # Call register with force_pull=True (existing server)
            result = tasks.register('192.168.1.2', 5556, force_pull=True)
            
            # Should call pull_server_info even for existing server
            assert result is True
            mock_pull.assert_called_once()

    def test_heartbeat_handler_no_longer_uses_force_pull(self):
        """Test that HeartbeatHandler no longer uses force_pull=True."""
        # Mock the register task
        with patch('nogamespy.protocol.tasks.register') as mock_register:
            mock_register.delay.return_value = MagicMock()
            
            # Create a mock request similar to what UDP handler receives
            mock_request = [b'\\heartbeat\\5555\\final\\']
            mock_handler = protocol.HeartbeatHandler(
                request=mock_request, 
                client_address=('192.168.1.3', 12345), 
                server=None
            )
            
            # Call the handler
            mock_handler.handle()
            
            # Check that register was called (ignoring exact count for now)
            assert mock_register.delay.called
            
            # Get all call arguments to verify force_pull is not present in any call
            for call in mock_register.delay.call_args_list:
                print(f"Call args: {call}")
                # Check that force_pull was not passed (or is False/not present)
                assert 'force_pull' not in call.kwargs or call.kwargs.get('force_pull') is False
            
            # Verify at least one call was made with the expected IP and port
            expected_call_found = False
            for call in mock_register.delay.call_args_list:
                if call.kwargs.get('ip') == '192.168.1.3' and call.kwargs.get('port') == '5555':
                    expected_call_found = True
                    break
            assert expected_call_found, f"Expected call not found in {mock_register.delay.call_args_list}"