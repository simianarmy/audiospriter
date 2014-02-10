from functools import partial
import os
import unittest
import json
import shutil
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from audiosprite import AudioSprite
from audiosprite.exceptions import (
        InvalidSource
)


data_dir = os.path.join(os.path.dirname(__file__), 'data')
export_dir = os.path.join(data_dir, 'out')

class AudioSpriteTests(unittest.TestCase):

    def setUp(self):
        self.sprite = AudioSprite('test1')
        self.sprite.setSilence(False)
        self.testout = 'sprite'

    def tearDown(self):
        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)
        
    def assertWithinTolerance(self, val, expected, tolerance=None, percentage=None):
        if percentage is not None:
            tolerance = val * percentage
        lower_bound = val - tolerance
        upper_bound = val + tolerance
        self.assertWithinRange(val, lower_bound, upper_bound)

    def assertWithinRange(self, val, lower_bound, upper_bound):
        self.assertTrue(lower_bound < val < upper_bound,
                        "%s is not in the acceptable range: %s - %s" %
                        (val, lower_bound, upper_bound))

    def add_two(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test1.mp3'))
        self.sprite.addAudio(os.path.join(data_dir, 'test2.mp3'))
        
    def load_audio(self, fmt):
        outfile = os.path.join(export_dir, fmt, self.testout)
        return AudioSegment.from_file(outfile + '.' + fmt, fmt)

    def test_create(self):
        self.assertIsInstance(self.sprite, AudioSprite)

    def test_is_indexable(self):
        self.add_two()
        self.assertTrue(self.sprite[0]['seg'] == self.sprite._files[0]['seg'])
        self.assertTrue(self.sprite[1]['seg'] == self.sprite._files[1]['seg'])

    def test_find_index_by_path(self):
        self.add_two()
        self.assertEqual(self.sprite.findIndexOf(os.path.join(data_dir, 'test1.mp3')), 0)
        self.assertEqual(self.sprite.findIndexOf(os.path.join(data_dir, 'test2.mp3')), 1)

    def test_empty_file_list(self):
        self.assertTrue(len(self.sprite) == 0)

    def test_add_good_audio_saves_filepath(self):
        f = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(f)
        self.assertTrue(self.sprite[0]['path'] == f)

    def test_add_good_audio_creates_audio_segment(self):
        f = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(f)
        self.assertTrue(len(self.sprite[0]['seg']) > 0)

    def test_add_missing_audio_raises_exception(self):
        badPath = os.path.join(data_dir, 'idontexist.mp3')
        func = partial(self.sprite.addAudio, badPath)
        self.assertRaises(InvalidSource, func)

    def test_length_is_total_milliseconds(self):
        self.add_two()
        self.assertEqual(len(self.sprite), len(self.sprite[0]['seg']) + len(self.sprite[1]['seg']))

    def test_is_iterable(self):
        self.add_two()
        i = 0

        for f in self.sprite:
            i += 1
        self.assertEqual(i, 2)

    def test_save_supports_multiple_formats(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        outfile = os.path.join(export_dir, self.testout)

        for fmt in AudioSprite.EXPORT_FORMATS:
            self.assertTrue(self.sprite.save(export_dir, self.testout, formats=[fmt]))

    def test_save_supports_m4a(self):
        self.sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        self.assertTrue(self.sprite.save(export_dir, self.testout, formats=['m4a']))
        saved = self.load_audio('m4a')
        self.assertTrue(len(saved) > 0)

    def test_save_generates_datafile(self):
        self.sprite.addAudio(os.path.join(data_dir, 'bach.ogg'))
        self.sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        outfile = os.path.join(export_dir, self.testout)
        self.assertTrue(self.sprite.save(export_dir, self.testout, formats=['ogg']))

        with open(outfile + '.json', 'r') as jsonfile:
            data = json.loads(jsonfile.read())
            self.assertEqual(data['sprite_id'], self.sprite._id)
            self.assertEqual(len(data['sounds']), 2)

    def test_datafile_contains_start_per_sound(self):
        self.sprite.addAudio(os.path.join(data_dir, 'bach.ogg'))
        self.sprite.addAudio(os.path.join(data_dir, 'test3.mp3'))
        self.sprite.save(export_dir, self.testout, formats=['ogg'])
        outfile = os.path.join(export_dir, self.testout)

        with open(outfile + '.json', 'r') as jsonfile:
            data = json.loads(jsonfile.read())
            for s in data['sounds']:
                self.assertTrue(s['start'] >= 0)

    def test_assign_volume_to_single_file(self):
        fpath = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(fpath)
        gain = self.sprite[0]['seg'].rms
        self.sprite.changeFileVolume(fpath, -2)
        self.assertTrue(self.sprite[0]['seg'].rms < gain)

    def test_modified_volume_in_datafile(self):
        fpath = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(fpath)
        og_gain = self.sprite[0]['seg'].rms 
        self.sprite.changeFileVolume(fpath, -2)
        self.sprite.save(export_dir, self.testout, formats=['ogg'])
        outfile = os.path.join(export_dir, self.testout)

        with open(outfile + '.json', 'r') as jsonfile:
            data = json.loads(jsonfile.read())
            self.assertTrue(og_gain > data['sounds'][0]['rms'])

    def test_generates_new_export_dir_if_none(self):
        self.assertFalse(os.path.isdir(export_dir))

        fpath = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(fpath)
        self.sprite.save(export_dir, self.testout, formats=['ogg'])
        self.assertTrue(os.path.isdir(export_dir))

    def test_generates_export_dir_per_format(self):
        fpath = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(fpath)
        self.sprite.save(export_dir, self.testout, formats=['ogg'])
        self.assertTrue(os.path.isdir(os.path.join(export_dir, 'ogg')))

    def test_save_source_flag_genrates_files_per_format(self):
        fpath = os.path.join(data_dir, 'test1.mp3')
        self.sprite.addAudio(fpath)
        self.sprite.save(export_dir, self.testout, formats=['ogg'], save_source=True)
        self.assertTrue(os.path.exists(os.path.join(export_dir, 'ogg', 'test1.ogg')))
        
    def test_silence_on_inserts_silence_config_between_audio_configs(self):
        self.add_two()
        self.sprite[1]['id'] == 'SILENCE'

    def test_save_with_silence_on_adds_silence_between_tracks(self):
        self.sprite.setSilence(True)
        self.add_two()
        self.sprite.save(export_dir, self.testout, formats=['mp3'])
        saved = self.load_audio('mp3')
        print "loaded len = " + str(len(saved))
        print "sprite len = " + str(len(self.sprite))
        self.assertWithinRange(len(saved) - 1000, len(self.sprite) - 20, len(self.sprite) + 20)


if __name__ == "__main__":
    import sys

    if sys.version_info >= (3, 1):
        unittest.main(warnings="ignore")
    else:
        unittest.main()

