import unittest
from unittest.mock import Mock, patch
import asyncio 

# Attempt to add project root to sys.path for direct execution of this test file.
# This might be necessary if the test runner doesn't handle it.
import sys
from os.path import abspath, join, dirname
sys.path.insert(0, abspath(join(dirname(__file__), '..', '..', '..')))

from bot.helper.video_utils.extra_selector import ExtraSelect

# Minimal mocks for dependencies if they cannot be imported or are too complex.
try:
    from bot import VID_MODE
except ImportError:
    VID_MODE = {'merge_rmaudio': 'Merge & Remove Audio'} 

try:
    from bot.helper.ext_utils.status_utils import get_readable_file_size
except ImportError:
    get_readable_file_size = lambda size: f"{size}B"


class TestExtraSelectStreamsSelect(unittest.TestCase):

    def setUp(self):
        # Common setup for mock_executor for each test
        self.mock_executor = Mock()
        self.mock_executor.listener = Mock()
        self.mock_executor.listener.tag = "TestUser"
        # Ensure mid is a string as it's used in f-string logs in the original code
        self.mock_executor.listener.mid = "12345" 
        self.mock_executor.mode = "merge_rmaudio" # Corresponds to VID_MODE key
        self.mock_executor.name = "test_video.mkv"
        self.mock_executor.size = 100000
        self.mock_executor.data = {} # Reset for each test

        # Default mock for config_dict, can be overridden in specific tests if needed
        self.patcher_config = patch('bot.helper.video_utils.extra_selector.config_dict')
        self.mock_config_dict = self.patcher_config.start()
        self.mock_config_dict.get.side_effect = lambda key, default="": {
            'SUPPORTED_LANGUAGES': 'tel,te,తెలుగు,hin,hi', # Ensures telugu_tags = ['tel', 'te', 'తెలుగు']
            'ALWAYS_REMOVE_LANGUAGES': 'tam,ta,தமிழ்,mal,ml,മലയാളം' 
        }.get(key, default)
        
        self.patcher_logger = patch('bot.helper.video_utils.extra_selector.LOGGER')
        self.mock_logger = self.patcher_logger.start()

        self.selector = ExtraSelect(self.mock_executor)
        # Attach necessary mocked/imported parts directly to the instance for test isolation
        self.selector.VID_MODE = VID_MODE 
        self.selector.get_readable_file_size = get_readable_file_size

    def tearDown(self):
        self.patcher_config.stop()
        self.patcher_logger.stop()

    def run_async(self, coro):
        return asyncio.run(coro)

    # Test Scenarios:

    def test_1_no_streams_none(self):
        """Test with None as streams input."""
        self.run_async(self.selector.streams_select(None))
        self.assertIn('streams_to_remove', self.mock_executor.data)
        self.assertEqual(self.mock_executor.data['streams_to_remove'], [])

    def test_1_no_streams_empty_list(self):
        """Test with an empty list as streams input."""
        self.run_async(self.selector.streams_select([]))
        self.assertIn('streams_to_remove', self.mock_executor.data)
        self.assertEqual(self.mock_executor.data['streams_to_remove'], [])

    def test_2_only_video_stream(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertEqual(self.mock_executor.data['streams_to_remove'], [])

    def test_3_video_and_telugu_audio(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertEqual(self.mock_executor.data['streams_to_remove'], [])

    def test_4_video_and_non_telugu_audio(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'eng'}, 'codec_name': 'aac'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(1, self.mock_executor.data['streams_to_remove'])
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_5_video_telugu_audio_english_audio(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},
            {'index': 2, 'codec_type': 'audio', 'tags': {'language': 'eng'}, 'codec_name': 'mp3'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertNotIn(1, self.mock_executor.data['streams_to_remove']) # Telugu
        self.assertIn(2, self.mock_executor.data['streams_to_remove'])    # English
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_6_video_multiple_telugu_audios_english_audio(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},
            {'index': 2, 'codec_type': 'audio', 'tags': {'language': 'తెలుగు'}, 'codec_name': 'ac3'}, # Another Telugu variant
            {'index': 3, 'codec_type': 'audio', 'tags': {'language': 'eng'}, 'codec_name': 'mp3'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertNotIn(1, self.mock_executor.data['streams_to_remove']) # Telugu 1
        self.assertNotIn(2, self.mock_executor.data['streams_to_remove']) # Telugu 2
        self.assertIn(3, self.mock_executor.data['streams_to_remove'])    # English
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_7_multiple_non_telugu_audios(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'eng'}, 'codec_name': 'aac'},
            {'index': 2, 'codec_type': 'audio', 'tags': {'language': 'hin'}, 'codec_name': 'mp3'}, # Hindi (non-Telugu for this rule)
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(1, self.mock_executor.data['streams_to_remove']) # English
        self.assertIn(2, self.mock_executor.data['streams_to_remove']) # Hindi
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 2)

    def test_8_telugu_audio_only(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertEqual(self.mock_executor.data['streams_to_remove'], [])

    def test_9_non_telugu_audio_only(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'audio', 'tags': {'language': 'eng'}, 'codec_name': 'aac'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(0, self.mock_executor.data['streams_to_remove'])
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_10_video_and_subtitle_stream(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'subtitle', 'tags': {'language': 'eng'}, 'codec_name': 'srt'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(1, self.mock_executor.data['streams_to_remove']) # Subtitle
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_11_video_telugu_audio_subtitle(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},
            {'index': 2, 'codec_type': 'subtitle', 'tags': {'language': 'eng'}, 'codec_name': 'srt'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertNotIn(1, self.mock_executor.data['streams_to_remove']) # Telugu audio
        self.assertIn(2, self.mock_executor.data['streams_to_remove'])    # Subtitle
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)
        
    def test_12_complex_mix(self):
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},      # Keep
            {'index': 2, 'codec_type': 'audio', 'tags': {'language': 'eng'}, 'codec_name': 'mp3'},      # Remove
            {'index': 3, 'codec_type': 'audio', 'tags': {'language': 'tam'}, 'codec_name': 'ac3'},      # Remove (non-Telugu)
            {'index': 4, 'codec_type': 'subtitle', 'tags': {'language': 'eng'}, 'codec_name': 'srt'}, # Remove
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        
        removed_streams = self.mock_executor.data['streams_to_remove']
        self.assertNotIn(0, removed_streams) # Video
        self.assertNotIn(1, removed_streams) # Telugu audio

        self.assertIn(2, removed_streams)    # English audio
        self.assertIn(3, removed_streams)    # Tamil audio
        self.assertIn(4, removed_streams)    # Subtitle
        
        self.assertEqual(len(removed_streams), 3)

    def test_audio_no_language_tag(self):
        """Test audio stream with no language tag, should be removed."""
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {}, 'codec_name': 'aac'}, # No language tag
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(1, self.mock_executor.data['streams_to_remove'])
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_audio_empty_language_tag(self):
        """Test audio stream with an empty language tag, should be removed."""
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': ''}, 'codec_name': 'aac'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(1, self.mock_executor.data['streams_to_remove'])
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_audio_und_language_tag(self):
        """Test audio stream with 'und' (undefined) language tag, should be removed."""
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'und'}, 'codec_name': 'aac'},
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertIn(1, self.mock_executor.data['streams_to_remove'])
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 1)

    def test_metadata_stream_handling(self):
        """Test that metadata streams are kept and not added to streams_to_remove."""
        initial_streams_data = [
            {'index': 0, 'codec_type': 'video', 'height': 720, 'codec_name': 'h264'},
            {'index': 1, 'codec_type': 'audio', 'tags': {'language': 'tel'}, 'codec_name': 'aac'},
            {'index': 2, 'codec_type': 'data', 'tags': {'title': 'Chapter Information'}, 'codec_name': 'bin_data'}, # Metadata stream
        ]
        self.run_async(self.selector.streams_select(initial_streams_data))
        self.assertNotIn(2, self.mock_executor.data['streams_to_remove'])
        self.assertEqual(len(self.mock_executor.data['streams_to_remove']), 0)


if __name__ == '__main__':
    unittest.main()
