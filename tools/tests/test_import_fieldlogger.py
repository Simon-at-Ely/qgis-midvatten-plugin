# -*- coding: utf-8 -*-
import utils_for_tests
import midvatten_utils as utils
from definitions import midvatten_defs as defs
from date_utils import datestring_to_date
import utils_for_tests as test_utils
from utils_for_tests import init_test
from tools.tests.mocks_for_tests import DummyInterface
from nose.tools import raises
from mock import mock_open, patch, MagicMock
from mocks_for_tests import MockUsingReturnValue, MockReturnUsingDict, MockReturnUsingDictIn, MockQgisUtilsIface, MockNotFoundQuestion, MockQgsProjectInstance, DummyInterface2, mock_answer
import mock
import io
import midvatten
import os
import PyQt4
from import_data_to_db import midv_data_importer, FieldloggerImport
import import_data_to_db
from collections import OrderedDict
import midvsettings

TEMP_DB_PATH = u'/tmp/tmp_midvatten_temp_db.sqlite'
MIDV_DICT = lambda x, y: {('Midvatten', 'database'): [TEMP_DB_PATH], ('Midvatten', 'locale'): [u'sv_SE']}[(x, y)]

MOCK_DBPATH = MockUsingReturnValue(MockQgsProjectInstance([TEMP_DB_PATH]))
DBPATH_QUESTION = MockUsingReturnValue(TEMP_DB_PATH)

class TestFieldLoggerImporterDb(object):
    answer_yes = mock_answer('yes')
    answer_no = mock_answer('no')
    CRS_question = MockUsingReturnValue([3006])
    mocked_iface = MockQgisUtilsIface()  #Used for not getting messageBar errors
    mock_askuser = MockReturnUsingDictIn({u'It is a strong': answer_no.get_v(), u'Please note!\nThere are ': answer_yes.get_v()}, 1)
    skip_popup = MockUsingReturnValue('')

    @mock.patch('midvatten.utils.askuser', answer_yes.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QInputDialog.getInteger', CRS_question.get_v)
    @mock.patch('create_db.PyQt4.QtGui.QFileDialog.getSaveFileName', DBPATH_QUESTION.get_v)
    def setUp(self):
        self.iface = DummyInterface()
        self.midvatten = midvatten.midvatten(self.iface)
        try:
            os.remove(TEMP_DB_PATH)
        except OSError:
            pass
        self.midvatten.new_db()

    def tearDown(self):
        #Delete database
        os.remove(TEMP_DB_PATH)

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def _test_load_file(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')
        utils.sql_alter_db(u'''INSERT INTO zz_staff ("staff") VALUES ("HS")''')
        utils.sql_alter_db(u'''INSERT INTO zz_flowtype ("type", "unit") VALUES ("Aveflow", "m3/s")''')
        utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("Temperature", "Temp", "m3/s")''')

        f = [
            u"Location;date_time;value;comment\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_data_to_db.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.MessagebarAndLog')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _test_load_file(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename ):
                mock_charset.return_value = 'utf-8'
                mock_savefilename.return_value = [filename]

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                # Set settings:
                #for setting in importer.settings:
                #    if isinstance(setting, import_data_to_db.StaffQuestion):
                #        setting.staff = u'teststaff'
                test_string = utils_for_tests.create_test_string(importer.observations)
                return test_string

            test_string = _test_load_file(self, filename)
            reference = u'[{date_time: 2016-03-30 15:29:26, parametername: q.comment, sublocation: Rb1505.quality, value: hej}, {date_time: 2016-03-30 15:30:39, parametername: q.syre.mg/L, sublocation: Rb1512.quality, value: 67}, {date_time: 2016-03-30 15:31:30, parametername: s.turbiditet.FNU, sublocation: Rb1512.sample, value: 899}, {date_time: 2016-03-30 15:29:26, parametername: q.konduktivitet.µS/cm, sublocation: Rb1505.quality, value: 863}, {date_time: 2016-03-30 15:30:09, parametername: f.comment, sublocation: Rb1615.flow, value: gick bra}, {date_time: 2016-03-30 15:30:40, parametername: q.syre.%, sublocation: Rb1512.quality, value: 58}, {date_time: 2016-03-30 15:34:13, parametername: l.meas.m, sublocation: Rb1608.level, value: 555}, {date_time: 2016-03-30 15:30:39, parametername: q.comment, sublocation: Rb1512.quality, value: test}, {date_time: 2016-03-30 15:31:30, parametername: s.comment, sublocation: Rb1202.sample, value: hej2}, {date_time: 2016-03-30 15:34:40, parametername: l.comment, sublocation: Rb1608.level, value: testc}, {date_time: 2016-03-30 15:30:09, parametername: f.Accvol.m3, sublocation: Rb1615.flow, value: 357}, {date_time: 2016-03-30 15:34:13, parametername: l.comment, sublocation: Rb1608.level, value: ergv}, {date_time: 2016-03-30 15:30:39, parametername: q.temperatur.grC, sublocation: Rb1512.quality, value: 8}]'
            assert test_string == reference

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def _test_staff_not_given(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1")''')

        f = [
            u"Location;date_time;value;comment\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_data_to_db.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.MessagebarAndLog')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _test_staff_not_given(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename ):
                mock_charset.return_value = 'utf-8'
                mock_savefilename.return_value = [filename]

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                importer.start_import(importer.observations)
                mock_MessagebarAndLog.critical.assert_called_with(bar_msg=u'Import error, staff not given')

    @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
    def test(self):
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1202")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1608")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1615")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1505")''')
        utils.sql_alter_db(u'''INSERT INTO obs_points ("obsid") VALUES ("Rb1512")''')
        utils.sql_alter_db(u'''INSERT INTO zz_staff ("staff") VALUES ("teststaff")''')
        try:
            utils.sql_alter_db(u'''INSERT INTO zz_flowtype ("type", "unit") VALUES ("Accvol", "m3")''')
        except:
            pass
        try:
            utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("turbiditet", "turb", "FNU")''')
        except:
            pass
        try:
            utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("konduktivitet", "kond", "µS/cm")''')
        except:
            pass
        try:
            utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("syre", "syre", "mg/L")''')
        except:
            pass
        try:
            utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("syre", "syre", "%")''')
        except:
            pass
        try:
            utils.sql_alter_db(u'''INSERT INTO zz_w_qual_field_parameters ("parameter", "shortname", "unit") VALUES ("temperatur", "temp", "grC")''')
        except:
            pass

        f = [
            u"Location;date_time;value;comment\n",
            u"Rb1202.sample;30-03-2016;15:31:30;hej2;s.comment\n",
            u"Rb1608.level;30-03-2016;15:34:40;testc;l.comment\n",
            u"Rb1615.flow;30-03-2016;15:30:09;357;f.Accvol.m3\n",
            u"Rb1615.flow;30-03-2016;15:30:09;gick bra;f.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;ergv;l.comment\n",
            u"Rb1608.level;30-03-2016;15:34:13;555;l.meas.m\n",
            u"Rb1512.sample;30-03-2016;15:31:30;899;s.turbiditet.FNU\n",
            u"Rb1505.quality;30-03-2016;15:29:26;hej;q.comment\n",
            u"Rb1505.quality;30-03-2016;15:29:26;863;q.konduktivitet.µS/cm\n",
            u"Rb1512.quality;30-03-2016;15:30:39;test;q.comment\n",
            u"Rb1512.quality;30-03-2016;15:30:39;67;q.syre.mg/L\n",
            u"Rb1512.quality;30-03-2016;15:30:39;8;q.temperatur.grC\n",
            u"Rb1512.quality;30-03-2016;15:30:40;58;q.syre.%\n",
            ]

        with utils.tempinput(''.join(f)) as filename:
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            @mock.patch('import_data_to_db.utils.QtGui.QFileDialog.getOpenFileNames')
            @mock.patch('import_data_to_db.utils.QtGui.QInputDialog.getText')
            @mock.patch('import_data_to_db.utils.MessagebarAndLog')
            @mock.patch('midvatten_utils.QgsProject.instance', MOCK_DBPATH.get_v)
            def _t(self, filename, mock_MessagebarAndLog, mock_charset, mock_savefilename ):
                mock_charset.return_value = 'utf-8'
                mock_savefilename.return_value = [filename]

                ms = MagicMock()
                ms.settingsdict = OrderedDict()
                importer = FieldloggerImport(self.iface.mainWindow(), ms)
                importer.parse_observations_and_populate_gui()

                #Set settings:
                for setting in importer.settings:
                    if isinstance(setting, import_data_to_db.StaffQuestion):
                        setting.staff = u'teststaff'

                stored_settings = {u's.comment': {u'import_method': u'comment'},
                                   u'l.comment': {u'import_method': u'comment'},
                                   u'f.comment': {u'import_method': u'comment'},
                                   u'q.comment': {u'import_method': u'comment'},
                                   u'l.meas.m': {u'import_method': u'w_level'},
                                   u'f.Accvol.m3': {u'import_method': u'w_flow', u'flowtype': u'Accvol', u'unit': u'm3'},
                                   u's.turbiditet.FNU': {u'import_method': u'w_qual_field', u'parameter': u'turbiditet', u'unit': u'FNU', u'depth': u'', u'instrument': u'testid'},
                                   u'q.konduktivitet.µS/cm': {u'import_method': u'w_qual_field', u'parameter': u'konduktivitet', u'unit': u'µS/cm', u'depth': u'', u'instrument': u'testid'},
                                   u'q.syre.mg/L': {u'import_method': u'w_qual_field', u'parameter': u'syre', u'unit': u'mg/L', u'depth': u'', u'instrument': u'testid'},
                                   u'q.syre.%': {u'import_method': u'w_qual_field', u'parameter': u'syre', u'unit': u'%', u'depth': u'', u'instrument': u'testid'},
                                   u'q.temperatur.grC': {u'import_method': u'w_qual_field', u'parameter': u'temperatur', u'unit': u'grC', u'depth': u'', u'instrument': u'testid'}}
                importer.set_parameters_using_stored_presets(stored_settings, importer.parameter_imports)
                importer.start_import(importer.observations)


            _t(self, filename)


            test_string = utils_for_tests.create_test_string(dict([(k, utils.sql_load_fr_db(u'select * from %s'%k)) for k in (u'w_levels', u'w_qual_field', u'w_flow', u'zz_staff', u'comments')]))
            reference_string = u'{comments: (True, [(Rb1608, 2016-03-30 15:34:40, testc, teststaff), (Rb1202, 2016-03-30 15:31:30, hej2, teststaff)]), w_flow: (True, [(Rb1615, testid, Accvol, 2016-03-30 15:30:09, 357.0, m3, gick bra)]), w_levels: (True, [(Rb1608, 2016-03-30 15:34:13, 555.0, None, None, ergv)]), w_qual_field: (True, [(Rb1505, teststaff, 2016-03-30 15:29:26, testid, konduktivitet, 863.0, 863, µS/cm, None, hej), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, syre, 67.0, 67, mg/L, None, test), (Rb1512, teststaff, 2016-03-30 15:30:39, testid, temperatur, 8.0, 8, grC, None, test), (Rb1512, teststaff, 2016-03-30 15:30:40, testid, syre, 58.0, 58, %, None, ), (Rb1512, teststaff, 2016-03-30 15:31:30, testid, turbiditet, 899.0, 899, FNU, None, )]), zz_staff: (True, [(teststaff, )])}'
            #reference = u'[{date_time: 2016-03-30 15:29:26, parametername: q.comment, sublocation: Rb1505.quality, value: hej}, {date_time: 2016-03-30 15:30:39, parametername: q.syre.mg/L, sublocation: Rb1512.quality, value: 67}, {date_time: 2016-03-30 15:31:30, parametername: s.turbiditet.FNU, sublocation: Rb1512.sample, value: 899}, {date_time: 2016-03-30 15:29:26, parametername: q.konduktivitet.µS/cm, sublocation: Rb1505.quality, value: 863}, {date_time: 2016-03-30 15:30:09, parametername: f.comment, sublocation: Rb1615.flow, value: gick bra}, {date_time: 2016-03-30 15:30:40, parametername: q.syre.%, sublocation: Rb1512.quality, value: 58}, {date_time: 2016-03-30 15:34:13, parametername: l.meas.m, sublocation: Rb1608.level, value: 555}, {date_time: 2016-03-30 15:30:39, parametername: q.comment, sublocation: Rb1512.quality, value: test}, {date_time: 2016-03-30 15:31:30, parametername: s.comment, sublocation: Rb1202.sample, value: hej2}, {date_time: 2016-03-30 15:34:40, parametername: l.comment, sublocation: Rb1608.level, value: testc}, {date_time: 2016-03-30 15:30:09, parametername: f.Accvol.m3, sublocation: Rb1615.flow, value: 357}, {date_time: 2016-03-30 15:34:13, parametername: l.comment, sublocation: Rb1608.level, value: ergv}, {date_time: 2016-03-30 15:30:39, parametername: q.temperatur.grC, sublocation: Rb1512.quality, value: 8}]'
            assert test_string == reference_string

