import os
import unittest
from pprint import pprint

from .. import Replay


class TestReplayParser(unittest.TestCase):

    folder_path = '{}/test_files/'.format(
        os.path.dirname(os.path.realpath(__file__))
    )

    def test_ensure_all_replays_tested(self):
        for filename in os.listdir(self.folder_path):
            if not filename.endswith('.replay'):
                continue

            # Generate a test name.
            filename = 'test_replay_{}'.format(
                filename.replace('.replay', '').replace('.', '').replace('-', '_').lower()
            )

            self.assertTrue(hasattr(self, filename), filename)

    def test_replay_1(self):
        # Replay ID: A993D8E2447A0887F49234AF27399379
        # Related issue: https://github.com/Galile0/pyrope/issues/4
        # Issue description: Unable to parse players with names containing latin-1 characters.
        replay = Replay('{}1.replay'.format(self.folder_path))

        self.assertEqual(replay.header['Id'], 'A993D8E2447A0887F49234AF27399379')
        self.assertEqual(replay.header['Goals'][0]['PlayerName'], u'Castaño ÍX 1/2')

    def test_replay_2(self):
        # Replay ID: 6790915F4216FEC5E6EBB089D3BA6FF0
        # Related issue: https://github.com/Galile0/pyrope/issues/6
        # Issue description: Unable to parse 'NewDedicatedServerIP' property.
        replay = Replay('{}2.replay'.format(self.folder_path))
        self.assertEqual(replay.header['Id'], '6790915F4216FEC5E6EBB089D3BA6FF0')

        self.assertIsNone(replay.netstream)

        # Parse the network data.
        replay.parse_netstream()

        self.assertIsNotNone(replay.netstream)

    def test_replay_3(self):
        # Replay ID: 010D2D7944D262BC2AAF2FA5DD23AA6E
        # Related issue: https://github.com/Galile0/pyrope/issues/7
        # Issue description: KeyError when parsing netstream.
        replay = Replay('{}3.replay'.format(self.folder_path))
        self.assertEqual(replay.header['Id'], '010D2D7944D262BC2AAF2FA5DD23AA6E')

        self.assertIsNone(replay.netstream)

        # Parse the network data.
        replay.parse_netstream()

        self.assertIsNotNone(replay.netstream)

    def test_replay_4(self):
        # Replay ID: 512256CE4C695326BB8E5AAA4680A293
        # Related issue: https://github.com/Galile0/pyrope/issues/9
        # Issue description: KeyError: 'Engine.PlayerReplicationInfo:bIsSpectator'
        replay = Replay('{}4.replay'.format(self.folder_path))
        self.assertEqual(replay.header['Id'], '512256CE4C695326BB8E5AAA4680A293')

        self.assertIsNone(replay.netstream)

        # Parse the network data.
        replay.parse_netstream()

        self.assertIsNotNone(replay.netstream)

    def test_replay_5(self):
        # Replay ID: 772810F44196DADD653608A44146D167
        # Related issue: https://github.com/Galile0/pyrope/issues/10
        # Issue description: IndexError: list index out of range
        replay = Replay('{}5.replay'.format(self.folder_path))
        self.assertEqual(replay.header['Id'], '772810F44196DADD653608A44146D167')

    def test_replay_6(self):
        # Replay ID: 9A93C12646BB2517DFCE19B514B85CA8
        # Related issue: https://github.com/Galile0/pyrope/issues/11
        # Issue description: No support for puck type.
        replay = Replay('{}6.replay'.format(self.folder_path))
        self.assertEqual(replay.header['Id'], '9A93C12646BB2517DFCE19B514B85CA8')

        self.assertIsNone(replay.netstream)

        # Parse the network data.
        replay.parse_netstream()

        self.assertIsNotNone(replay.netstream)

    def test_replay_7(self):
        # Replay ID: 6B111DEA41797216FFA7D3B01B225006
        # Related issue: https://github.com/Galile0/pyrope/issues/12
        # Issue description: KeyErrors. Root cause as yet unknown.
        replay = Replay('{}7.replay'.format(self.folder_path))
        self.assertEqual(replay.header['Id'], '6B111DEA41797216FFA7D3B01B225006')

        self.assertIsNone(replay.netstream)

        # Parse the network data.
        replay.parse_netstream()

        self.assertIsNotNone(replay.netstream)
