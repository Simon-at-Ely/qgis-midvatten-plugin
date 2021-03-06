# -*- coding: utf-8 -*-
"""
/***************************************************************************
 This part of the Midvatten plugin originates from the PlotSQLite application which plots . 
        Name                 : PlotSQLite
        Description          : Plots charts from data stored in a SQLite database
        Date                 : 2012-12-03 
        Author               : Josef Källgården
        copyright            : (C) 2011 by Josef Källgården
        email                : groundwatergis [at] gmail.com

The PlotSQLite application version 0.2.6 was merged into Midvatten plugin at 2014-05-06
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
import sys, os, locale
from PyQt4 import QtGui, QtCore, uic#, QtSql

import db_utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from functools import partial # only to get combobox signals to work

from sqlite3 import dbapi2 as sqlite
import numpy as np
import matplotlib.pyplot as plt   
from matplotlib.dates import datestr2num
from matplotlib import ticker
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

try:#assume matplotlib >=1.5.1
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT    
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
import datetime
import matplotlib.ticker as tick
#import midvatten_utils as utils
import midvatten_utils as utils
from midvatten_utils import returnunicode as ru
from date_utils import datestring_to_date
from definitions import midvatten_defs as defs
import PyQt4
from PyQt4.QtCore import QCoreApplication

try:
    import pandas as pd
except:
    pandas_on = False
else:
    pandas_on = True

utils.MessagebarAndLog.info(log_msg=u"Python pandas: " + str(pandas_on))
customplot_ui_class =  uic.loadUiType(os.path.join(os.path.dirname(__file__),'..', 'ui', 'customplotdialog.ui'))[0]


class plotsqlitewindow(QtGui.QMainWindow, customplot_ui_class):
    def __init__(self, parent, msettings):#, parent as second arg?
        self.ms = msettings
        self.ms.loadSettings()
        QtGui.QDialog.__init__(self, parent)        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi( self )#due to initialisation of Ui_MainWindow instance
        self.initUI()
        self.tables_columns = db_utils.tables_columns()
        self.LoadTablesFromDB(self.tables_columns)
        self.LastSelections()#fill comboboxes etc with last selected values
        #on close:
        #del self.axes.collections[:]#this should delete all plot objects related to axes and hence not intefere with following tsplots
        self.drawn = False
        
    def initUI(self):
        self.table_ComboBox_1.clear()  
        self.table_ComboBox_2.clear()  
        self.table_ComboBox_3.clear()  
        for i in range(1,3):
            self.clearthings(i)
        # function partial due to problems with currentindexChanged and Combobox
        #self.connect(self.table_ComboBox_1, QtCore.SIGNAL("currentIndexChanged(int)"), partial(self.Table1Changed))#currentIndexChanged caused unnecessary signals when scrolling in combobox
        self.connect(self.table_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.Table1Changed))  
        self.connect(self.Filter1_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.Filter1_1Changed))
        #self.connect(self.Filter1_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.FilterChanged(1,1)))
        self.connect(self.Filter2_ComboBox_1, QtCore.SIGNAL("activated(int)"), partial(self.Filter2_1Changed)) 
        self.connect(self.table_ComboBox_2, QtCore.SIGNAL("activated(int)"), partial(self.Table2Changed)) 
        self.connect(self.Filter1_ComboBox_2, QtCore.SIGNAL("activated(int)"), partial(self.Filter1_2Changed))
        self.connect(self.Filter2_ComboBox_2, QtCore.SIGNAL("activated(int)"), partial(self.Filter2_2Changed)) 
        self.connect(self.table_ComboBox_3, QtCore.SIGNAL("activated(int)"), partial(self.Table3Changed)) 
        self.connect(self.Filter1_ComboBox_3, QtCore.SIGNAL("activated(int)"), partial(self.Filter1_3Changed))
        self.connect(self.Filter2_ComboBox_3, QtCore.SIGNAL("activated(int)"), partial(self.Filter2_3Changed))
        self.connect(self.plot_width, QtCore.SIGNAL("editingFinished()"), partial(self.change_plot_size))
        self.connect(self.plot_height, QtCore.SIGNAL("editingFinished()"), partial(self.change_plot_size))
        self.connect(self.plot_settings_1, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.plot_settings_1))
        self.connect(self.plot_settings_2, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.plot_settings_2))
        self.connect(self.plot_settings_3, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.plot_settings_3))
        self.connect(self.chart_settings, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.chart_settings))

        self.connect(self.select_button_t1f1, QtCore.SIGNAL("clicked()"), partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_1, self.Filter1_ComboBox_1))
        self.connect(self.select_button_t1f2, QtCore.SIGNAL("clicked()"), partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_1, self.Filter2_ComboBox_1))
        self.connect(self.select_button_t2f1, QtCore.SIGNAL("clicked()"), partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_2, self.Filter1_ComboBox_2))
        self.connect(self.select_button_t2f2, QtCore.SIGNAL("clicked()"), partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_2, self.Filter2_ComboBox_2))
        self.connect(self.select_button_t3f1, QtCore.SIGNAL("clicked()"), partial(self.select_in_filterlist_from_selection, self.Filter1_QListWidget_3, self.Filter1_ComboBox_3))
        self.connect(self.select_button_t3f2, QtCore.SIGNAL("clicked()"), partial(self.select_in_filterlist_from_selection, self.Filter2_QListWidget_3, self.Filter2_ComboBox_3))

        self.connect(self.save_to_eps_button, QtCore.SIGNAL("clicked()"), self.save_to_eps)

        self.connect(self.listfilter_1_1, QtCore.SIGNAL("editingFinished()"), partial(self.filter_filterlist, self.Filter1_QListWidget_1, self.listfilter_1_1))
        self.connect(self.listfilter_2_1, QtCore.SIGNAL("editingFinished()"), partial(self.filter_filterlist, self.Filter2_QListWidget_1, self.listfilter_2_1))
        self.connect(self.listfilter_1_2, QtCore.SIGNAL("editingFinished()"), partial(self.filter_filterlist, self.Filter1_QListWidget_2, self.listfilter_1_2))
        self.connect(self.listfilter_2_2, QtCore.SIGNAL("editingFinished()"), partial(self.filter_filterlist, self.Filter2_QListWidget_2, self.listfilter_2_2))
        self.connect(self.listfilter_1_3, QtCore.SIGNAL("editingFinished()"), partial(self.filter_filterlist, self.Filter1_QListWidget_3, self.listfilter_1_3))
        self.connect(self.listfilter_2_3, QtCore.SIGNAL("editingFinished()"), partial(self.filter_filterlist, self.Filter2_QListWidget_3, self.listfilter_2_3))
        self.connect(self.filtersettings1, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.filtersettings1))
        self.connect(self.filtersettings2, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.filtersettings2))
        self.connect(self.filtersettings3, QtCore.SIGNAL("clicked()"), partial(self.set_groupbox_children_visibility, self.filtersettings3))


        self.PlotChart_QPushButton.clicked.connect(self.drawPlot_all)
        self.Redraw_pushButton.clicked.connect( self.refreshPlot )

        self.custplotfigure = plt.figure()

        self.axes = self.custplotfigure.add_subplot( 111 )
        self.canvas = FigureCanvas( self.custplotfigure )

        self.mpltoolbar = NavigationToolbar( self.canvas, self.widgetPlot)
        lstActions = self.mpltoolbar.actions()
        self.mpltoolbar.removeAction( lstActions[ 7 ] )
        self.layoutplot.addWidget( self.canvas )
        self.layoutplot.addWidget( self.mpltoolbar )

        #Validator for QlineEdit that should contain only floats, any number of decimals with either point(.) or comma(,) as a decimal separater
        regexp = QtCore.QRegExp('[+-]?\\d*[\\.,]?\\d+') 
        validator = QtGui.QRegExpValidator(regexp)
        self.LineEditFactor1.setValidator(validator)
        self.LineEditFactor2.setValidator(validator)
        self.LineEditFactor3.setValidator(validator)
        self.LineEditOffset1.setValidator(validator)
        self.LineEditOffset2.setValidator(validator)
        self.LineEditOffset3.setValidator(validator)

        self.pandas_calc_1 = None
        self.pandas_calc_2 = None
        self.pandas_calc_3 = None
        if pandas_on:
            self.pandas_calc_1 = PandasCalculations(self.gridLayout_16)
            self.pandas_calc_2 = PandasCalculations(self.gridLayout_14)
            self.pandas_calc_3 = PandasCalculations(self.gridLayout_19)

        #self.custplotfigure.tight_layout()

        self.chart_settings.setChecked(False)
        self.filtersettings1.setChecked(False)
        self.filtersettings2.setChecked(False)
        self.filtersettings3.setChecked(False)
        self.set_groupbox_children_visibility(self.chart_settings)
        self.set_groupbox_children_visibility(self.filtersettings1)
        self.set_groupbox_children_visibility(self.filtersettings2)
        self.set_groupbox_children_visibility(self.filtersettings3)
        for plot_item_settings in [self.plot_settings_1, self.plot_settings_2, self.plot_settings_3]:
            plot_item_settings.setChecked(False)
            self.set_groupbox_children_visibility(plot_item_settings)

        self.show()

    def calc_frequency(self,table2):
        freqs = np.zeros(len(table2.values),dtype=float)
        for j, row in enumerate(table2):                
            if j>0:#we can not calculate frequency for first row
                try:
                    diff = (table2.values[j] - table2.values[j-1])
                    """ Get help from function datestr2num to get date and time into float"""
                    delta_time = 24*3600*(datestr2num(table2.date_time[j]) - datestr2num(table2.date_time[j-1]))#convert to seconds since numtime is days
                except:
                    pass #just skip inaccurate data values and use previous frequency
                freqs[j] = diff/delta_time
        freqs[0]=freqs[1]#assuming start frequency to get a nicer plot

        return freqs

    def change_plot_size(self):
        width = self.plot_width.text()
        height = self.plot_height.text()

        try:
            width = float(width)
        except ValueError:
            #self.layoutplot.setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Extended)
            #self.widgetPlot.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Expanding)
            self.widgetPlot.setMinimumWidth(100)
            self.widgetPlot.setMaximumWidth(16777215)
            #self.widgetPlot.adjustSize()
        else:
            #self.widgetPlot.setMinimum
            #self.widgetPlot.setFixedWidth(width)
            self.widgetPlot.setMinimumWidth(width)
            self.widgetPlot.setMaximumWidth(width)

        try:
            height = float(height)
        except ValueError:
            #self.widgetPlot.sizePolicy().setVerticalPolicy(PyQt4.QtGui.QSizePolicy.Expanding)
            self.widgetPlot.setMinimumHeight(100)
            self.widgetPlot.setMaximumHeight(16777215)
        else:
            self.widgetPlot.setMinimumHeight(height)
            self.widgetPlot.setMaximumHeight(height)

    def drawPlot_all(self):

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))#show the user this may take a long time...

        self.axes.clear()
        self.axes.legend_ = None
        My_format = [('date_time', datetime.datetime), ('values', float)] #Define (with help from function datetime) a good format for numpy array

        dbconnection = db_utils.DbConnectionManager()

        i = 0
        nop=0# nop=number of plots
        self.p=[]
        self.plabels=[]
                
        nop, i = self.drawPlot(dbconnection, nop, i, My_format, self.table_ComboBox_1, self.xcol_ComboBox_1, self.ycol_ComboBox_1, self.Filter1_ComboBox_1, self.Filter1_QListWidget_1, self.Filter2_ComboBox_1, self.Filter2_QListWidget_1, self.PlotType_comboBox_1, self.pandas_calc_1, self.checkBox_remove_mean1, self.LineEditFactor1, self.LineEditOffset1)
        nop, i = self.drawPlot(dbconnection, nop, i, My_format, self.table_ComboBox_2, self.xcol_ComboBox_2, self.ycol_ComboBox_2, self.Filter1_ComboBox_2, self.Filter1_QListWidget_2, self.Filter2_ComboBox_2, self.Filter2_QListWidget_2, self.PlotType_comboBox_2, self.pandas_calc_2, self.checkBox_remove_mean2, self.LineEditFactor2, self.LineEditOffset2)
        nop, i = self.drawPlot(dbconnection, nop, i, My_format, self.table_ComboBox_3, self.xcol_ComboBox_3, self.ycol_ComboBox_3, self.Filter1_ComboBox_3, self.Filter1_QListWidget_3, self.Filter2_ComboBox_3, self.Filter2_QListWidget_3, self.PlotType_comboBox_3, self.pandas_calc_3, self.checkBox_remove_mean3, self.LineEditFactor3, self.LineEditOffset3)

        self.xaxis_formatters = (self.axes.xaxis.get_major_formatter(), self.axes.xaxis.get_major_locator())
    
        self.axes.set_title(self.ms.settingsdict['custplot_title'])
        self.axes.set_xlabel(self.ms.settingsdict['custplot_xtitle'])
        self.axes.set_ylabel(self.ms.settingsdict['custplot_ytitle'])
    
        self.drawn = True
    
        self.refreshPlot()
    
        QtGui.QApplication.restoreOverrideCursor()  # now this long process is done and the cursor is back as normal

    def drawPlot(self, dbconnection, nop, i, My_format, table_ComboBox, xcol_ComboBox, ycol_ComboBox, Filter1_ComboBox, Filter1_QListWidget, Filter2_ComboBox, Filter2_QListWidget, PlotType_comboBox, pandas_calc, checkBox_remove_mean, LineEditFactor, LineEditOffset):
                
        if not (table_ComboBox.currentText() == '' or table_ComboBox.currentText()==' ') and not (xcol_ComboBox.currentText()== '' or xcol_ComboBox.currentText()==' ') and not (ycol_ComboBox.currentText()== '' or ycol_ComboBox.currentText()==' '): #if anything is to be plotted from tab 1
            self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()   # if user selected a time step bigger than zero than thre may be discontinuous plots
            plottable1='y'
            filter1 = unicode(Filter1_ComboBox.currentText())
            filter1list = []
            filter2list = []
            filter1list = Filter1_QListWidget.selectedItems()
            filter2 = unicode(Filter2_ComboBox.currentText())
            filter2list= Filter2_QListWidget.selectedItems()
            nop = max(len(filter1list),1)*max(len(filter2list),1)
            #self.p= [None]*nop#list for plot objects
            self.p.extend([None]*nop)#list for plot objects
            self.plabels.extend([None]*nop)# List for plot labels
            try:
                factor = float(LineEditFactor.text().replace(',','.'))
            except ValueError:
                factor = 1.0
            try:
                offset = float(LineEditOffset.text().replace(',','.'))
            except ValueError:
                offset = 0.0

            remove_mean = checkBox_remove_mean.isChecked()

            _sql = r"""SELECT %s, %s FROM %s """% (unicode(xcol_ComboBox.currentText()), unicode(ycol_ComboBox.currentText()), unicode(table_ComboBox.currentText()))
            _sql += r"""WHERE %s """ % db_utils.test_not_null_and_not_empty_string(unicode(table_ComboBox.currentText()), unicode(xcol_ComboBox.currentText()), dbconnection)
            _sql += r"""AND %s """ % db_utils.test_not_null_and_not_empty_string(unicode(table_ComboBox.currentText()), unicode(ycol_ComboBox.currentText()), dbconnection)

            while i < len(self.p):
                #Both filters empty
                if (not filter1.strip() or not filter1list) and (not filter2.strip() or not filter2list):
                    sql = _sql + r""" ORDER BY %s"""%unicode(xcol_ComboBox.currentText())
                    self.plabels[i] = unicode(ycol_ComboBox.currentText())+""", """+unicode(table_ComboBox.currentText())
                    self.createsingleplotobject(sql, i, My_format, dbconnection, PlotType_comboBox.currentText(), factor, offset, remove_mean, pandas_calc)
                    i += 1
                #Both filters in use
                elif all((filter1.strip(), filter1list, filter2.strip(), filter2list)):
                    for item1 in filter1list:
                        for item2 in filter2list:
                            sql = _sql + r""" AND %s = '%s' AND %s = '%s' ORDER BY %s"""%(filter1, unicode(item1.text()), filter2, unicode(item2.text()), unicode(xcol_ComboBox.currentText()))
                            self.plabels[i] = unicode(item1.text()) + """, """ + unicode(item2.text())
                            self.createsingleplotobject(sql, i, My_format, dbconnection, PlotType_comboBox.currentText(), factor, offset, remove_mean, pandas_calc)
                            i += 1
                #One filter in use
                else:
                    for filter, filterlist in [(filter1, filter1list), (filter2, filter2list)]:
                        if not filter.strip() or not filterlist:
                            continue
                        else:
                            for item in filterlist:
                                sql = _sql + r""" AND %s = '%s' ORDER BY %s"""%(filter, unicode(item.text()), unicode(xcol_ComboBox.currentText()))
                                self.plabels[i] = unicode(item.text())
                                self.createsingleplotobject(sql, i, My_format, dbconnection, PlotType_comboBox.currentText(), factor, offset, remove_mean, pandas_calc)
                                i += 1


        return nop, i

    def createsingleplotobject(self,sql,i,My_format,dbconnection,plottype='line', factor=1.0, offset=0.0, remove_mean=False, pandas_calc=None):
        recs = dbconnection.execute_and_fetchall(sql)
        #Transform data to a numpy.recarray
        try:
            table = np.array(recs, dtype=My_format)  #NDARRAY
            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects
            FlagTimeXY = 'time'
            myTimestring = list(table2.date_time)
            numtime=datestr2num(myTimestring)  #conv list of strings to numpy.ndarray of floats
        except Exception, e:
            utils.MessagebarAndLog.warning(log_msg=ru(QCoreApplication.translate(u'plotsqlitewindow', u'Plotting date_time failed, msg: %s'))%str(e))
            utils.MessagebarAndLog.info(log_msg=ru(QCoreApplication.translate(u'plotsqlitewindow', u"Customplot, transforming to recarray with date_time as x-axis failed, msg: %s"))%ru(str(e)))
            table = np.array(recs, dtype=[('numx', float), ('values', float)])  #NDARRAY #define a format for xy-plot (to use if not datetime on x-axis)

            table2=table.view(np.recarray)   # RECARRAY transform the 2 cols into callable objects
            FlagTimeXY = 'XY'
            numtime = list(table2.numx)

        # from version 0.2 there is a possibility to make discontinuous plot if timestep bigger than maxtstep
        if self.spnmaxtstep.value() > 0: # if user selected a time step bigger than zero than thre may be discontinuous plots
            pos = np.where(np.abs(np.diff(numtime)) >= self.spnmaxtstep.value())[0]
            numtime[pos] = np.nan
            table2.values[pos] = np.nan

        if plottype == "marker":
            MarkVar = 'o'  
        elif plottype in ("line","frequency"):
            MarkVar = '-'  
        elif plottype  == "line and cross":
            MarkVar = '+-'  
        else:
            MarkVar = 'o-'

        if FlagTimeXY == "time" and plottype == "frequency":
            table2.values[:] = self.calc_frequency(table2)[:]

        if remove_mean:
            table2.values[:] = utils.remove_mean_from_nparray(table2.values)[:]

        if any([factor != 1 and factor, offset,]):
            table2.values[:] = utils.scale_nparray(table2.values, factor, offset)[:]

        if pandas_calc and FlagTimeXY == "time":
            if pandas_calc.use_pandas():
                df = pd.DataFrame.from_records(table2, columns=[u'values'], exclude=[u'date_time'])
                df.set_index(pd.DatetimeIndex(table2.date_time, name=u'date_time'), inplace=True)
                df.columns = [u'values']

                df = pandas_calc.calculate(df)
                if df is not None:
                    table = np.array(zip(df.index, df[u'values']), dtype=My_format)
                    table2 = table.view(np.recarray)  # RECARRAY transform the 2 cols into callable objects
                    numtime = table2.date_time
                else:
                    utils.MessagebarAndLog.info(bar_msg=ru(QCoreApplication.translate(u'plotsqlitewindow', u"Pandas calculate failed.")))

        color_list = [_num[0] for _num in np.random.rand(3,1).tolist()]
        if FlagTimeXY == "time" and plottype == "step-pre":
            self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',c=color_list,label=self.plabels[i])# 'steps-pre' best for precipitation and flowmeters, optional types are 'steps', 'steps-mid', 'steps-post'
        elif FlagTimeXY == "time" and plottype == "step-post":
            self.p[i], = self.axes.plot_date(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',c=color_list,label=self.plabels[i])
        elif FlagTimeXY == "time" and plottype == "line and cross":
            self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,markersize = 6, label=self.plabels[i])
        elif FlagTimeXY == "time" and plottype == "frequency":
            try:
                self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,markersize = 6, label='frequency '+str(self.plabels[i]))
                self.plabels[i]='frequency '+str(self.plabels[i])
            except:
                self.p[i], = self.axes.plot_date(np.array([]),np.array([]),  MarkVar,markersize = 6, label='frequency '+str(self.plabels[i]))
                self.plabels[i]='frequency '+str(self.plabels[i])
        elif FlagTimeXY == "time":
            self.p[i], = self.axes.plot_date(numtime, table2.values,  MarkVar,label=self.plabels[i])
        elif FlagTimeXY == "XY" and plottype == "step-pre":
            self.p[i], = self.axes.plot(numtime, table2.values, drawstyle='steps-pre', linestyle='-', marker='None',c=color_list,label=self.plabels[i])
        elif FlagTimeXY == "XY" and plottype == "step-post":
            self.p[i], = self.axes.plot(numtime, table2.values, drawstyle='steps-post', linestyle='-', marker='None',c=color_list,label=self.plabels[i])
        elif FlagTimeXY == "XY" and plottype == "line and cross":
            self.p[i], = self.axes.plot(numtime, table2.values,  MarkVar,markersize = 6, label=self.plabels[i])
        else: 
            self.p[i], = self.axes.plot(numtime, table2.values,  MarkVar,label=self.plabels[i])

    def LastSelections(self):#set same selections as last plot

        last_selection_arg_tuples = [(self.table_ComboBox_1, self.xcol_ComboBox_1, self.ycol_ComboBox_1, 'custplot_table1', 'custplot_xcol1', 'custplot_ycol1', self.Table1Changed),
                                     (self.table_ComboBox_2, self.xcol_ComboBox_2, self.ycol_ComboBox_2, 'custplot_table2', 'custplot_xcol2', 'custplot_ycol2', self.Table2Changed),
                                     (self.table_ComboBox_3, self.xcol_ComboBox_3, self.ycol_ComboBox_3, 'custplot_table3', 'custplot_xcol3', 'custplot_ycol3', self.Table3Changed)]

        for table_combobox, xcol_combobox, ycol_combobox, custplot_table, custplot_xcol, custplot_ycol, table_changed in last_selection_arg_tuples:
            self.set_last_selection(table_combobox, xcol_combobox, ycol_combobox, custplot_table, custplot_xcol, custplot_ycol, table_changed)

        #table2
        self.tabWidget.setCurrentIndex(int(self.ms.settingsdict['custplot_tabwidget']))

        filter_tuples = [(self.Filter1_ComboBox_1, 'custplot_filter1_1', 1, 1),
                         (self.Filter2_ComboBox_1, 'custplot_filter2_1', 2, 1),
                         (self.Filter1_ComboBox_2, 'custplot_filter1_2', 1, 2),
                         (self.Filter2_ComboBox_2, 'custplot_filter2_2', 2, 2),
                         (self.Filter1_ComboBox_3, 'custplot_filter1_3', 1, 3),
                         (self.Filter2_ComboBox_3, 'custplot_filter2_3', 2, 3)]

        for filter_combobox, custplot_filter, filterno1, filterno2 in filter_tuples:
            self.set_filters(filter_combobox, custplot_filter, filterno1, filterno2)

        filter_selection_tuples = [(self.Filter1_QListWidget_1, 'custplot_filter1_1_selection'),
                                   (self.Filter2_QListWidget_1, 'custplot_filter2_1_selection'),
                                   (self.Filter1_QListWidget_2, 'custplot_filter1_2_selection'),
                                   (self.Filter2_QListWidget_2, 'custplot_filter2_2_selection'),
                                   (self.Filter1_QListWidget_3, 'custplot_filter1_3_selection'),
                                   (self.Filter2_QListWidget_3, 'custplot_filter2_3_selection')]

        for filter_qlistwidget, custplot_filter_selection in filter_selection_tuples:
            self.filter_selections(filter_qlistwidget, custplot_filter_selection)

        #plottype1
        searchindex = self.PlotType_comboBox_1.findText(self.ms.settingsdict['custplot_plottype1'])
        if searchindex >= 0:
            self.PlotType_comboBox_1.setCurrentIndex(searchindex)
        #plottype2
        searchindex = self.PlotType_comboBox_2.findText(self.ms.settingsdict['custplot_plottype2'])
        if searchindex >= 0:
            self.PlotType_comboBox_2.setCurrentIndex(searchindex)
        #plottype3
        searchindex = self.PlotType_comboBox_3.findText(self.ms.settingsdict['custplot_plottype3'])
        if searchindex >= 0:
            self.PlotType_comboBox_3.setCurrentIndex(searchindex)
        #max time step, titles, grid, legend
        self.spnmaxtstep.setValue(self.ms.settingsdict['custplot_maxtstep'])

        if self.ms.settingsdict['custplot_legend']==2:
            self.Legend_checkBox.setChecked(True)
        else:
            self.Legend_checkBox.setChecked(False)
        if self.ms.settingsdict['custplot_grid']==2:
            self.Grid_checkBox.setChecked(True)
        else:
            self.Grid_checkBox.setChecked(False)

    def set_last_selection(self, table_combobox, xcol_combobox, ycol_combobox, custplot_table, custplot_xcol, custplot_ycol, table_changed):
        searchindex = table_combobox.findText(self.ms.settingsdict[custplot_table])
        if searchindex >= 0:
            table_combobox.setCurrentIndex(searchindex)
            table_changed()
            searchindex = xcol_combobox.findText(self.ms.settingsdict[custplot_xcol])
            if searchindex >= 0:
                xcol_combobox.setCurrentIndex(searchindex)
            searchindex = ycol_combobox.findText(self.ms.settingsdict[custplot_ycol])
            if searchindex >= 0:
                ycol_combobox.setCurrentIndex(searchindex)

    def set_filters(self, filter_combobox, custplot_filter, filterno1, filterno2):
        #filtre1_1
        searchindex = filter_combobox.findText(self.ms.settingsdict[custplot_filter])
        if searchindex >= 0:
            filter_combobox.setCurrentIndex(searchindex)
            self.FilterChanged(filterno1, filterno2)

    def filter_selections(self, filter_qlistwidget, custplot_filter_selection):
        #filtre1_1_selection
        for index in xrange(filter_qlistwidget.count()):
            for item in self.ms.settingsdict[custplot_filter_selection]:
                if filter_qlistwidget.item(index).text()==item:#earlier str(item) but that caused probs for non-ascii
                     filter_qlistwidget.item(index).setSelected(True)

    def filter_filterlist(self, filterlist, lineedit):
        words = lineedit.text().split(u';')

        listcount = filterlist.count()
        if words:
            [filterlist.item(idx).setHidden(False) if any([word.lower() in filterlist.item(idx).text().lower() for word in words]) else filterlist.item(idx).setHidden(True) for idx in xrange(listcount)]
        else:
            [filterlist.item(idx).setHidden(False) for idx in xrange(listcount)]

    def LoadTablesFromDB( self, tables_columns ):    # Open the SpatiaLite file to extract info about tables
        tables = sorted([table for table in tables_columns.keys() if table not in db_utils.nonplot_tables(as_tuple=True) and not table.startswith(u'zz_')])
        for i, table_combobox in enumerate([self.table_ComboBox_1, self.table_ComboBox_2, self.table_ComboBox_3], 1):
            table_combobox.clear()
            self.clearthings(i)
            table_combobox.addItem('')
            try:
                table_combobox.addItems(tables)
            except:
                for table in tables:
                    table_combobox.addItem(table)

    def clearthings(self,tabno=1):   #clear xcol,ycol,filter1,filter2
        xcolcombobox = 'xcol_ComboBox_' + str(tabno)
        ycolcombobox = 'ycol_ComboBox_' + str(tabno)
        filter1combobox = 'Filter1_ComboBox_' + str(tabno)
        filter2combobox = 'Filter2_ComboBox_' + str(tabno)
        filter1qlistwidget = 'Filter1_QListWidget_' + str(tabno)
        filter2qlistwidget = 'Filter2_QListWidget_' + str(tabno)
        getattr(self,xcolcombobox).clear()
        getattr(self,ycolcombobox).clear()
        getattr(self,filter1combobox).clear()
        getattr(self,filter2combobox).clear()
        getattr(self,filter1qlistwidget).clear()
        getattr(self,filter2qlistwidget).clear()

    def Table1Changed(self):     #This method is called whenever table1 is changed
        # First, update combobox with columns
        self.clearthings(1)
        #self.ms.settingsdict['custplot_table1'] = self.table_ComboBox_1.currentText()
        self.PopulateComboBox('xcol_ComboBox_1', self.table_ComboBox_1.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox_1', self.table_ComboBox_1.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox_1', self.table_ComboBox_1.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox_1', self.table_ComboBox_1.currentText())  # See GeneralNote

    def Table2Changed(self):     #This method is called whenever table2 is changed
        # First, update combobox with columns
        self.clearthings(2)
        #self.ms.settingsdict['custplot_table2'] = self.table_ComboBox_2.currentText()
        self.PopulateComboBox('xcol_ComboBox_2', self.table_ComboBox_2.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox_2', self.table_ComboBox_2.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox_2', self.table_ComboBox_2.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox_2', self.table_ComboBox_2.currentText())  # See GeneralNote

    def Table3Changed(self):     #This method is called whenever table3 is changed
        # First, update combobox with columns
        self.clearthings(3)
        #self.ms.settingsdict['custplot_table2'] = self.table_ComboBox_3.currentText()
        self.PopulateComboBox('xcol_ComboBox_3', self.table_ComboBox_3.currentText())  # GeneralNote: For some reason it is not possible to send currentText with the SIGNAL-trigger
        self.PopulateComboBox('ycol_ComboBox_3', self.table_ComboBox_3.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter1_ComboBox_3', self.table_ComboBox_3.currentText())  # See GeneralNote
        self.PopulateComboBox('Filter2_ComboBox_3', self.table_ComboBox_3.currentText())  # See GeneralNote

    def PopulateComboBox(self, comboboxname='', table=None):
        """This method fills comboboxes with columns for selected tool and table"""
        columns = self.tables_columns.get(table, [])    # Load all columns into a list 'columnsä
        if len(columns)>0:    # Transfer information from list 'columns' to the combobox
            getattr(self, comboboxname).addItem('')
            try:
                getattr(self, comboboxname).addItems(columns)
            except:
                for column in columns:
                    getattr(self, comboboxname).addItem(column)

    def FilterChanged(self, filterno, tabno):
        TableCombobox = 'table_ComboBox_' + str(tabno)
        FilterCombobox = 'Filter' + str(filterno) + '_ComboBox_' + str(tabno)
        FilterQListWidget = 'Filter' + str(filterno) + '_QListWidget_' + str(tabno)

        other_filterno = {2:1, 1:2}[filterno]
        other_FilterCombobox = 'Filter' + str(other_filterno) + '_ComboBox_' + str(tabno)
        other_FilterQListWidget = 'Filter' + str(other_filterno) + '_QListWidget_' + str(tabno)

        dependent_filtering_box = getattr(self, 'dependent_filtering' + str(tabno), None)

        getattr(self,FilterQListWidget).clear()
        if not getattr(self,FilterCombobox).currentText()=='':
            self.PopulateFilterList(getattr(self,TableCombobox).currentText(), FilterQListWidget,
                                    getattr(self,FilterCombobox).currentText(),
                                    other_FilterQListWidget,
                                    getattr(self,other_FilterCombobox).currentText(),
                                    dependent_filtering_box)
        
    def Filter1_1Changed(self):
        self.FilterChanged(1,1)
    
    def Filter2_1Changed(self):
        self.FilterChanged(2,1)

    def Filter1_2Changed(self):
        self.FilterChanged(1,2)
            
    def Filter2_2Changed(self):
        self.FilterChanged(2,2)

    def Filter1_3Changed(self):
        self.FilterChanged(1,3)
        
    def Filter2_3Changed(self):
        self.FilterChanged(2,3)
                        
    def PopulateFilterList(self, table, QListWidgetname='', filtercolumn=None, other_QListWidget=None,
                           other_filtercolumn=None, dependent_filtering_box=None):

        sql = "select distinct " + unicode(filtercolumn) + " from " + table + " order by " + unicode(filtercolumn)

        if dependent_filtering_box is not None:
            dependent_filtering = dependent_filtering_box.isChecked()
        else:
            dependent_filtering = False


        if other_QListWidget is not None and other_filtercolumn and dependent_filtering:
            other_QListWidget_wid = getattr(self, other_QListWidget)
            selected = ru([item.text() for item in other_QListWidget_wid.selectedItems() if item.text()], keep_containers=True)
            if selected:
                sql = u"SELECT DISTINCT {} FROM {} WHERE {} IN ({}) ORDER BY {}".format(
                                                                                unicode(filtercolumn),
                                                                                table,
                                                                                other_filtercolumn,
                                                                                u', '.join([u"'{}'".format(item)
                                                                                            for item in selected]),
                                                                                unicode(filtercolumn),)

        ConnectionOK, list_data= db_utils.sql_load_fr_db(sql)
        for post in list_data:
            item = QtGui.QListWidgetItem(unicode(post[0]))
            getattr(self, QListWidgetname).addItem(item)

    def refreshPlot( self ):
        #If the user has not pressed "draw" before, do nothing
        if not self.drawn:
            return None

        self.storesettings()    #all custom plot related settings are stored when plotting data (or pressing "redraw")
        datemin = self.spnMinX.dateTime().toPyDateTime()
        datemax = self.spnMaxX.dateTime().toPyDateTime()
        if datemin == datemax: #xaxis-limits
            pass
        else:
            self.axes.set_xlim(min(datemin, datemax),max(datemin, datemax))            
        if self.spnMinY.value() == self.spnMaxY.value(): #yaxis-limits
            pass
        else:
            self.axes.set_ylim(min(self.spnMaxY.value(), self.spnMinY.value()),max(self.spnMaxY.value(), self.spnMinY.value()))            
        self.axes.yaxis.set_major_formatter(tick.ScalarFormatter(useOffset=False, useMathText=False))#yaxis-format
        self.axes.xaxis.set_major_formatter(self.xaxis_formatters[0])
        self.axes.xaxis.set_major_locator(self.xaxis_formatters[1])

        self.axes.grid(self.Grid_checkBox.isChecked() )#grid

        self.ms.settingsdict['custplot_title'] = self.axes.get_title()
        self.ms.settingsdict['custplot_xtitle'] = self.axes.get_xlabel()
        self.ms.settingsdict['custplot_ytitle'] = self.axes.get_ylabel()

        axes_fontsize = float(self.axes_fontsize.text())
        for label in self.axes.xaxis.get_ticklabels():
            label.set_fontsize(axes_fontsize)
            try:
                label.set_rotation(axes_fontsize)
            except:
                pass
        for label in self.axes.yaxis.get_ticklabels():
            label.set_fontsize(axes_fontsize)

        #The legend
        if self.Legend_checkBox.isChecked():
            if self.axes.legend_ is None:
                if (self.spnLegX.value() ==0 ) and (self.spnLegY.value() ==0):
                    leg = self.axes.legend(self.p, self.plabels)
                else:
                    leg = self.axes.legend(self.p, self.plabels, bbox_to_anchor=(self.spnLegX.value(),self.spnLegY.value()),loc=10)
            else:
                if (self.spnLegX.value() ==0 ) and (self.spnLegY.value() ==0):
                    leg = self.axes.legend()
                else:
                    leg = self.axes.legend(bbox_to_anchor=(self.spnLegX.value(),self.spnLegY.value()),loc=10)
            leg.draggable(state=True)
            frame = leg.get_frame()    # the matplotlib.patches.Rectangle instance surrounding the legend
            frame.set_facecolor('1')    # set the frame face color to white
            frame.set_fill(False)    # set the frame face color to white
            for t in leg.get_texts():
                t.set_fontsize(float(self.legend_fontsize.text()))  # the legend text fontsize
        else:
            self.axes.legend_ = None

        self.canvas.draw()
        #plt.close(self.custplotfigure)#this closes reference to self.custplotfigure

    def storesettings(self):
        self.ms.settingsdict['custplot_table1'] = unicode(self.table_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_xcol1'] = unicode(self.xcol_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_ycol1'] = unicode(self.ycol_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_table2'] = unicode(self.table_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_xcol2'] = unicode(self.xcol_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_ycol2'] = unicode(self.ycol_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_table3'] = unicode(self.table_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_xcol3'] = unicode(self.xcol_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_ycol3'] = unicode(self.ycol_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter1_1']=unicode(self.Filter1_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_filter2_1']=unicode(self.Filter2_ComboBox_1.currentText())
        self.ms.settingsdict['custplot_filter1_2']=unicode(self.Filter1_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_filter2_2']=unicode(self.Filter2_ComboBox_2.currentText())
        self.ms.settingsdict['custplot_filter1_3']=unicode(self.Filter1_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter2_3']=unicode(self.Filter2_ComboBox_3.currentText())
        self.ms.settingsdict['custplot_filter1_1_selection']=[]
        self.ms.settingsdict['custplot_filter2_1_selection']=[]
        self.ms.settingsdict['custplot_filter1_2_selection']=[]
        self.ms.settingsdict['custplot_filter2_2_selection']=[]
        self.ms.settingsdict['custplot_filter1_3_selection']=[]
        self.ms.settingsdict['custplot_filter2_3_selection']=[]
        for item in self.Filter1_QListWidget_1.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_1_selection'].append(unicode(item.text()))
        for item in self.Filter2_QListWidget_1.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_1_selection'].append(unicode(item.text()))
        for item in self.Filter1_QListWidget_2.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_2_selection'].append(unicode(item.text()))
        for item in self.Filter2_QListWidget_2.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_2_selection'].append(unicode(item.text()))
        for item in self.Filter1_QListWidget_3.selectedItems(): 
            self.ms.settingsdict['custplot_filter1_3_selection'].append(unicode(item.text()))
        for item in self.Filter2_QListWidget_3.selectedItems(): 
            self.ms.settingsdict['custplot_filter2_3_selection'].append(unicode(item.text()))
        self.ms.settingsdict['custplot_plottype1']=unicode(self.PlotType_comboBox_1.currentText())
        self.ms.settingsdict['custplot_plottype2']=unicode(self.PlotType_comboBox_2.currentText())
        self.ms.settingsdict['custplot_plottype3']=unicode(self.PlotType_comboBox_3.currentText())
        self.ms.settingsdict['custplot_maxtstep'] = self.spnmaxtstep.value()
        self.ms.settingsdict['custplot_legend']=self.Legend_checkBox.checkState()
        self.ms.settingsdict['custplot_grid']=self.Grid_checkBox.checkState()
        self.ms.settingsdict['custplot_title'] = unicode(self.axes.get_title())
        self.ms.settingsdict['custplot_xtitle'] = unicode(self.axes.get_xlabel())
        self.ms.settingsdict['custplot_ytitle'] = unicode(self.axes.get_ylabel())
        self.ms.settingsdict['custplot_tabwidget'] = self.tabWidget.currentIndex()
        self.ms.save_settings()

    def set_groupbox_children_visibility(self, groupbox_widget):
        children = groupbox_widget.findChildren(PyQt4.QtGui.QWidget)
        for child in children:
            child.setVisible(groupbox_widget.isChecked())

    def select_in_filterlist_from_selection(self, filter_listwidget, filter_combobox):
        current_column = ru(filter_combobox.currentText())
        if not current_column:
            return
        selected_values = utils.getselectedobjectnames(column_name=current_column)
        [filter_listwidget.item(nr).setSelected(True) for nr in xrange(filter_listwidget.count()) if ru(filter_listwidget.item(nr).text()) in selected_values]

    def save_to_eps(self):
        filename = PyQt4.QtGui.QFileDialog.getSaveFileName(parent=None, caption=ru(
            QCoreApplication.translate(u'CustomPlot', u'Choose a file name, extension sets format')), directory='')
        if not filename:
            return
        name, ext = os.path.splitext(filename)
        self.custplotfigure.savefig(filename, format=ext.lstrip(u'.'), dpi=float(self.figure_dpi.text()))


class PandasCalculations(object):
    def __init__(self, gridlayout):

        self.widget = PyQt4.QtGui.QWidget()

        #General settings
        self.rule_label = PyQt4.QtGui.QLabel(u'Resample rule')
        self.rule = PyQt4.QtGui.QLineEdit()
        for wid in [self.rule_label, self.rule]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'Steplength for resampling, ex:\n'
                           u'"10S" = 10 seconds\n'
                           u'"20T" = 20 minutes\n'
                           u'"1h" = 1 hour\n'
                           u'"24h" = 24 hours\n'
                           u'(D = calendar day, M = month end, MS = month start, W = weekly, AS = year start, A = year end, ...)\n'
                           u'No resampling if field is empty\n'
                           u'See pandas pandas.DataFrame.resample documentation for more info.')))

        self.base_label = PyQt4.QtGui.QLabel(u'Resample base')
        self.base = PyQt4.QtGui.QLineEdit()
        for wid in [self.base_label, self.base]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'The hour to start each timestep when rule "evenly subdivide 1 day" (for example Rule = 24h)\n'
                           u'Ex: 7 (= 07:00). Default is 0 (00:00)\n'
                           u'See pandas pandas.DataFrame.resample documentation for more info:\n'
                           u'For frequencies that evenly subdivide 1 day, the "origin" of the aggregated intervals.\n'
                           u'For example, for "5min" frequency, base could range from 0 through 4. Defaults to 0.')))

        self.how_label = PyQt4.QtGui.QLabel(u'Resample how')
        self.how = PyQt4.QtGui.QLineEdit()
        for wid in [self.how_label, self.how]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'How to make the resample, ex. "mean" (default), "first", "last", "sum".\n'
                           u'See pandas pandas.DataFrame.resample documentation for more info\n'
                           u'(though "how" is not explained a lot)')))

        #Moving average:
        self.window_label = PyQt4.QtGui.QLabel(u'Rolling mean window')
        self.window = PyQt4.QtGui.QLineEdit(u'')
        self.center_label = PyQt4.QtGui.QLabel(u'Rolling mean center')
        self.center = PyQt4.QtGui.QLineEdit(u'')
        for wid in [self.window_label, self.window]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'The number of timesteps in each moving average (rolling mean) mean\n'
                           u'The result is stored at the center timestep of each mean.\n'
                           u'See Pandas pandas.rolling_mean documentation for more info.\n'
                           u'No rolling mean if field is empty.')))

        for wid in [self.center_label, self.center]:
            wid.setToolTip(ru(QCoreApplication.translate(u'PandasCalculations',
                           u'1/True (default) to store the rolling mean at the center timestep.\n'
                           u'0/False to store the rolling mean at the last timestep.\n'
                           u'See Pandas pandas.rolling_mean documentation for more info.\n'
                           u'center=True if field is empty.')))


        for lineedit in [self.rule, self.base, self.how, self.window, self.center]:
            #lineedit.sizeHint()setFixedWidth(122)
            lineedit.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Preferred)

        maximumwidth = 0
        for label in [self.rule_label, self.base_label, self.how_label, self.window_label, self.center_label]:
            testlabel = PyQt4.QtGui.QLabel()
            testlabel.setText(label.text())
            maximumwidth = max(maximumwidth, testlabel.sizeHint().width())
        testlabel = None
        for label in [self.rule_label, self.base_label, self.how_label, self.window_label, self.center_label]:
            label.setFixedWidth(maximumwidth)
            #label.setMinimumWidth(maximumwidth)
            label.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Fixed)

        hline = horizontal_line()
        hline.sizePolicy().setHorizontalPolicy(PyQt4.QtGui.QSizePolicy.Fixed)
        gridlayout.addWidget(hline)
        for col1, col2 in [(self.rule_label, self.rule),
                           (self.base_label, self.base),
                           (self.how_label, self.how),
                           (self.window_label, self.window),
                           (self.center_label, self.center)]:
            current_row = gridlayout.rowCount()

            try:
                col1.setMaximumHeight(27)
                col2.setMaximumHeight(27)
            except:
                pass

            gridlayout.addWidget(col1, current_row, 0)
            gridlayout.addWidget(col2, current_row, 1)

    def use_pandas(self):
        if self.rule.text() or self.window.text():
            return True
        else:
            return False

    def calculate(self, df):
        #Resample
        rule = self.rule.text()
        base = self.base.text() if self.base.text() else 0
        how = self.how.text() if self.how.text() else u'mean'
        if rule:
            try:
                base = int(base)
            except ValueError:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'PandasCalculations', u'Resample base must be an integer')))
            else:
				try:#new api for pandas >=0.18
					df = getattr(df.resample(rule,base=int(base)),how)()
				except:#old pandas
					df = df.resample(rule, how=how, base=int(base))

        #Rolling mean
        window = self.window.text()
        if window:
            try:
                window = int(window)
            except ValueError:
                utils.MessagebarAndLog.critical(bar_msg=ru(QCoreApplication.translate(u'PandasCalculations', u'Rolling mean window must be an integer')))
            else:
                if self.center.text() in (u'0', u'False'):
                    center=False
                else:
                    center=True
                df = pd.rolling_mean(df, window=window, center=center)
        return df


def horizontal_line():
    line = PyQt4.QtGui.QFrame()
    line.setGeometry(PyQt4.QtCore.QRect(320, 150, 118, 3))
    line.setFrameShape(PyQt4.QtGui.QFrame.HLine)
    line.setFrameShadow(PyQt4.QtGui.QFrame.Sunken)
    return line
