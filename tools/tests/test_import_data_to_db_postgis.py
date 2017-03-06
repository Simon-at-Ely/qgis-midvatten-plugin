# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin tests the module that handles importing of
  measurements.
 
 This part is to a big extent based on QSpatialite plugin.
                             -------------------
        begin                : 2016-03-08
        copyright            : (C) 2016 by joskal (HenrikSpa)
        email                : groundwatergis [at] gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#
import db_utils
import midvatten_utils as utils
import mock
import utils_for_tests
from mock import call
from mocks_for_tests import MockUsingReturnValue


class _TestWlvllogImportFromDiverofficeFiles(utils_for_tests.MidvattenTestPostgisDbSvImportInstance):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')

        self.importinstance.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]
                    utils_askuser_answer_no_obj = MockUsingReturnValue(None)
                    utils_askuser_answer_no_obj.result = 0
                    utils_askuser_answer_no = MockUsingReturnValue(utils_askuser_answer_no_obj)

                    @mock.patch('midvatten_utils.MessagebarAndLog')
                    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser, mock_messagebar):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']
                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_skip_duplicate_datetimes(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:30', '5.0')''')

        self.importinstance.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if args[1].startswith(u'Do you want to confirm'):
                                mock_result.result = 0
                                return mock_result
                                #mock_askuser.return_value.result.return_value = 0
                            elif args[1].startswith(u'Do you want to import all'):
                                mock_result.result = 0
                                return mock_result
                            elif args[1].startswith(u'Please note!\nForeign keys'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'Please note!\nThere are'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'It is a strong recommendation'):
                                mock_result.result = 0
                                return mock_result
                        mock_askuser.side_effect = side_effect

                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:30, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_filter_dates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        self.importinstance.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if args[1].startswith(u'Do you want to confirm'):
                                mock_result.result = 0
                                return mock_result
                                #mock_askuser.return_value.result.return_value = 0
                            elif args[1].startswith(u'Do you want to import all'):
                                mock_result.result = 0
                                return mock_result
                            elif args[1].startswith(u'Please note!\nForeign keys'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'Please note!\nThere are'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'It is a strong recommendation'):
                                mock_result.result = 0
                                return mock_result

                        mock_askuser.side_effect = side_effect

                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    def test_wlvllogg_import_from_diveroffice_files_all_dates(self):
        files = [(u'Location=rb1',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/03/15 10:30:00,1,10',
                u'2016/03/15 11:00:00,11,101'),
                (u'Location=rb2',
                u'Date/time,Water head[cm],Temperature[°C]',
                u'2016/04/15 10:30:00,2,20',
                u'2016/04/15 11:00:00,21,201'),
                (u'Location=rb3',
                u'Date/time,Water head[cm],Temperature[°C],Conductivity[mS/cm]',
                u'2016/05/15 10:30:00,3,30,5',
                u'2016/05/15 11:00:00,31,301,6')
                 ]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb2')''')
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb3')''')
        db_utils.sql_alter_db(u'''INSERT INTO w_levels_logger (obsid, "date_time", "head_cm") VALUES ('rb1', '2016-03-15 10:31', '5.0')''')

        self.importinstance.charsetchoosen = u'utf-8'
        with utils.tempinput(u'\n'.join(files[0]), self.importinstance.charsetchoosen) as f1:
            with utils.tempinput(u'\n'.join(files[1]), self.importinstance.charsetchoosen) as f2:
                with utils.tempinput(u'\n'.join(files[2]), self.importinstance.charsetchoosen) as f3:

                    filenames = [f1, f2, f3]

                    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
                    @mock.patch('import_data_to_db.utils.Askuser')
                    @mock.patch('qgis.utils.iface', autospec=True)
                    @mock.patch('PyQt4.QtGui.QInputDialog.getText')
                    @mock.patch('import_data_to_db.utils.pop_up_info', autospec=True)
                    @mock.patch('import_data_to_db.utils.select_files')
                    def _test_wlvllogg_import_from_diveroffice_files(self, filenames, mock_filenames, mock_skippopup, mock_encoding, mock_iface, mock_askuser):
                        mock_filenames.return_value = filenames
                        mock_encoding.return_value = [u'utf-8']

                        def side_effect(*args, **kwargs):
                            mock_result = mock.MagicMock()
                            if args[1].startswith(u'Do you want to confirm'):
                                mock_result.result = 0
                                return mock_result
                                #mock_askuser.return_value.result.return_value = 0
                            elif args[1].startswith(u'Do you want to import all'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'Please note!\nForeign keys'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'Please note!\nThere are'):
                                mock_result.result = 1
                                return mock_result
                            elif args[1].startswith(u'It is a strong recommendation'):
                                mock_result.result = 0
                                return mock_result

                        mock_askuser.side_effect = side_effect

                        self.importinstance.wlvllogg_import_from_diveroffice_files()

                    _test_wlvllogg_import_from_diveroffice_files(self, filenames)

                    test_string = utils_for_tests.create_test_string(
                        db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
                    reference_string = ur'''(True, [(rb1, 2016-03-15 10:31, 5.0, None, None, None, None), (rb1, 2016-03-15 10:30:00, 1.0, 10.0, None, None, None), (rb1, 2016-03-15 11:00:00, 11.0, 101.0, None, None, None), (rb2, 2016-04-15 10:30:00, 2.0, 20.0, None, None, None), (rb2, 2016-04-15 11:00:00, 21.0, 201.0, None, None, None), (rb3, 2016-05-15 10:30:00, 3.0, 30.0, 5.0, None, None), (rb3, 2016-05-15 11:00:00, 31.0, 301.0, 6.0, None, None)])'''
                    assert test_string == reference_string


class _TestGeneralImport(utils_for_tests.MidvattenTestPostgisDbSvImportInstance):
    """ Test to make sure wlvllogg_import goes all the way to the end without errors
    """
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg(self):
        file = [(u'obsid',u'date_time',u'head_cm'),
                (u'rb1',u'2016-03-15 10:30:00',u'1')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')

        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, None, None, None, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    @mock.patch('qgis.utils.iface', autospec=True)
    def test_general_import_wlvllogg_missing_not_null_column(self, mock_iface):
        file = [(u'obsids',u'date_time',u'test'),
                (u'rb1',u'2016-03-15 10:30:00',u'1')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)
        mock_iface.messageBar.return_value.createMessage.assert_called_with(u'Error: Import failed, see log message panel')
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_with_comment(self):
        file = [(u'obsid', u'date_time' ,u'head_cm',u'comment'),
                (u'rb1', u'2016-03-15 10:30:00', u'1', u'testcomment')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, None, None, None, testcomment)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_with_temp(self):
        file = [(u'obsid', u'date_time', u'head_cm', u'temp_degc'),
                (u'rb1', u'2016-03-15 10:30:00', u'1', u'5')]
        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 5.0, None, None, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_with_temp_comment(self):
        file = [(u'obsid', u'date_time', u'head_cm', u'temp_degc', u'cond_mscm'),
                (u'rb1', u'2016-03-15 10:30:00', u'1', u'5', u'10')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 5.0, 10.0, None, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_different_order(self):
        file = [(u'obsid', u'cond_mscm', u'date_time', u'head_cm', u'temp_degc'),
                 (u'rb1', u'10', u'2016-03-15 10:30:00', u'1', u'5')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, 1.0, 5.0, 10.0, None, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_only_level_masl(self):
        file = [(u'obsid', u'date_time', u'level_masl'),
                (u'rb1', u'2016-03-15 10:30:00', u'1')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, None, None, None, 1.0, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_only_temp_degc(self):
        file = [(u'obsid', u'date_time', u'temp_degc'),
                 (u'rb1', u'2016-03-15 10:30:00', u'1')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, None, 1.0, None, None, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_general_import_wlvllogg_only_cond_mscm(self):
        file = [(u'obsid', u'date_time', u'cond_mscm'),
                 (u'rb1', u'2016-03-15 10:30:00', u'1')]

        db_utils.sql_alter_db(u'''INSERT INTO obs_points (obsid) VALUES ('rb1')''')
        self.importinstance.general_import(goal_table=u'w_levels_logger', file_data=file)

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, date_time, head_cm, temp_degc, cond_mscm, level_masl, comment from w_levels_logger'''))
        reference_string = ur'''(True, [(rb1, 2016-03-15 10:30:00, None, None, 1.0, None, None)])'''
        assert test_string == reference_string


class _TestImportObsPointsObsLines(utils_for_tests.MidvattenTestPostgisDbSvImportInstance):
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_import_obsids_directly(self):
        db_utils.sql_alter_db(u"INSERT INTO obs_points (obsid) VALUES ('obsid1')")
        db_utils.sql_alter_db(u"INSERT INTO obs_points (obsid) VALUES ('obsid2')")
        result = db_utils.sql_load_fr_db(u'select * from obs_points')
        assert result == (True, [(u'obsid1', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None), (u'obsid2', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)])

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_import_obs_points(self):
        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        self.importinstance.general_import(file_data=f, goal_table=u'obs_points')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html, ST_AsText(geometry) from obs_points'''))

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, 421484.0, 6542696.0, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, POINT(421484 6542696))])'''
        assert test_string == reference_string

    @mock.patch('qgis.utils.iface')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_import_obs_points_already_exist(self, mock_iface):
        db_utils.sql_alter_db(u'''insert into obs_points (obsid) values ('rb1')''')
        self.importinstance.charsetchoosen = [u'utf-8']

        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        self.importinstance.general_import(file_data=f, goal_table=u'obs_points')
        assert call.messageBar().createMessage(u'0 rows imported and 1 excluded for table obs_points. See log message panel for details') in mock_iface.mock_calls

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html, ST_AsText(geometry) from obs_points'''))

        reference_string = ur'''(True, [(rb1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    @mock.patch('midvatten_utils.MessagebarAndLog')
    def test_import_obs_points_duplicates(self, mock_messagebar):
        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1'],
             [u'rb1', u'rb2', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421485', u'6542697', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1'],
             [u'rb1', u'rb3', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'421484', u'6542696', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        self.importinstance.general_import(file_data=f, goal_table=u'obs_points')

        call.info(bar_msg=u'1 rows imported and 2 excluded for table obs_points. See log message panel for details', log_msg=u'2 nr of duplicate rows in file was skipped while importing.\nIn total 2 rows were not imported to obs_points. Probably due to a primary key combination already existing in the database.\n--------------------') in mock_messagebar.mock_calls
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html, ST_AsText(geometry) from obs_points'''))

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, 421484.0, 6542696.0, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, POINT(421484 6542696))])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_import_obs_points_no_east_north(self):
        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'', u'', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1']]

        self.importinstance.general_import(file_data=f,
                                           goal_table=u'obs_points')

        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html, ST_AsText(geometry) from obs_points'''))

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, None, None, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, None)])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_import_obs_points_geometry_as_wkt(self, mock_messagebar):
        f = [[u'obsid', u'name', u'place', u'type', u'length', u'drillstop', u'diam', u'material', u'screen', u'capacity', u'drilldate', u'wmeas_yn', u'wlogg_yn', u'east', u'north', u'ne_accur', u'ne_source', u'h_toc', u'h_tocags', u'h_gs', u'h_accur', u'h_syst', u'h_source', u'source', u'com_onerow', u'com_html', u'geometry'],
             [u'rb1', u'rb1', u'a', u'pipe', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'', u'', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'1', u'POINT(45 55)']]

        self.importinstance.general_import(file_data=f, goal_table=u'obs_points')
        test_string = utils_for_tests.create_test_string(
            db_utils.sql_load_fr_db(u'''select obsid, name, place, type, length, drillstop, diam, material, screen, capacity, drilldate, wmeas_yn, wlogg_yn, east, north, ne_accur, ne_source, h_toc, h_tocags, h_gs, h_accur, h_syst, h_source, source, com_onerow, com_html, ST_AsText(geometry) from obs_points'''))

        reference_string = ur'''(True, [(rb1, rb1, a, pipe, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 1, 45.0, 55.0, 1.0, 1, 1.0, 1.0, 1.0, 1.0, 1, 1, 1, 1, 1, POINT(45 55))])'''
        assert test_string == reference_string

    @mock.patch('midvatten_utils.MessagebarAndLog')
    @mock.patch('midvatten_utils.QgsProject.instance', utils_for_tests.MidvattenTestPostgisNotCreated.mock_instance_settings_database)
    @mock.patch('import_data_to_db.utils.Askuser', mock.MagicMock())
    def test_import_obs_lines_geometry_as_wkt(self, mock_messagebar):
        f = [[u'obsid', u'geometry'],
             [u'line1', u'LINESTRING(1 2, 3 4, 5 6, 7 8)']]

        self.importinstance.general_import(file_data=f, goal_table=u'obs_lines')
        test_string = utils_for_tests.create_test_string(db_utils.sql_load_fr_db(u'''select obsid, ST_AsText(geometry) from obs_lines'''))

        reference_string = ur'''(True, [(line1, LINESTRING(1 2,3 4,5 6,7 8))])'''
        assert test_string == reference_string
