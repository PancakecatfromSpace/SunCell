# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'supply_UI_1oDrIPZ.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDial, QDialog, QGridLayout,
    QHBoxLayout, QLCDNumber, QLabel, QLayout,
    QLineEdit, QPushButton, QScrollBar, QSizePolicy,
    QSlider, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(908, 758)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.labels = QHBoxLayout()
        self.labels.setObjectName(u"labels")
        self.voltage_label = QLabel(Dialog)
        self.voltage_label.setObjectName(u"voltage_label")
        font = QFont()
        font.setPointSize(15)
        self.voltage_label.setFont(font)

        self.labels.addWidget(self.voltage_label)

        self.power_label = QLabel(Dialog)
        self.power_label.setObjectName(u"power_label")
        self.power_label.setFont(font)

        self.labels.addWidget(self.power_label)

        self.current_label = QLabel(Dialog)
        self.current_label.setObjectName(u"current_label")
        self.current_label.setFont(font)

        self.labels.addWidget(self.current_label)


        self.gridLayout.addLayout(self.labels, 0, 0, 1, 1)

        self.display = QHBoxLayout()
        self.display.setObjectName(u"display")
        self.display.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.display.setContentsMargins(-1, 0, -1, 0)
        self.voltage_display = QLCDNumber(Dialog)
        self.voltage_display.setObjectName(u"voltage_display")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.voltage_display.sizePolicy().hasHeightForWidth())
        self.voltage_display.setSizePolicy(sizePolicy)
        self.voltage_display.setMinimumSize(QSize(150, 50))
        self.voltage_display.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.voltage_display.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.voltage_display.setSmallDecimalPoint(False)
        self.voltage_display.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.display.addWidget(self.voltage_display)

        self.current_display = QLCDNumber(Dialog)
        self.current_display.setObjectName(u"current_display")
        self.current_display.setMinimumSize(QSize(150, 50))

        self.display.addWidget(self.current_display)

        self.power_display = QLCDNumber(Dialog)
        self.power_display.setObjectName(u"power_display")
        sizePolicy.setHeightForWidth(self.power_display.sizePolicy().hasHeightForWidth())
        self.power_display.setSizePolicy(sizePolicy)
        self.power_display.setMinimumSize(QSize(150, 50))

        self.display.addWidget(self.power_display)


        self.gridLayout.addLayout(self.display, 1, 0, 1, 1)

        self.option_tabs = QTabWidget(Dialog)
        self.option_tabs.setObjectName(u"option_tabs")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.option_tabs.sizePolicy().hasHeightForWidth())
        self.option_tabs.setSizePolicy(sizePolicy1)
        self.connection = QWidget()
        self.connection.setObjectName(u"connection")
        self.gridLayout_3 = QGridLayout(self.connection)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.port_label = QLabel(self.connection)
        self.port_label.setObjectName(u"port_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.port_label.sizePolicy().hasHeightForWidth())
        self.port_label.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.port_label, 1, 1, 1, 1)

        self.port_field = QLineEdit(self.connection)
        self.port_field.setObjectName(u"port_field")

        self.gridLayout_3.addWidget(self.port_field, 3, 1, 1, 1)

        self.ip_address_label = QLabel(self.connection)
        self.ip_address_label.setObjectName(u"ip_address_label")
        sizePolicy2.setHeightForWidth(self.ip_address_label.sizePolicy().hasHeightForWidth())
        self.ip_address_label.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.ip_address_label, 1, 0, 1, 1)

        self.connect_button = QPushButton(self.connection)
        self.connect_button.setObjectName(u"connect_button")
        self.connect_button.setMinimumSize(QSize(0, 50))

        self.gridLayout_3.addWidget(self.connect_button, 4, 0, 1, 2)

        self.ip_address_field = QLineEdit(self.connection)
        self.ip_address_field.setObjectName(u"ip_address_field")

        self.gridLayout_3.addWidget(self.ip_address_field, 3, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 5, 0, 1, 2)

        self.option_tabs.addTab(self.connection, "")
        self.manuel = QWidget()
        self.manuel.setObjectName(u"manuel")
        self.gridLayout_2 = QGridLayout(self.manuel)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.voltage_dial = QDial(self.manuel)
        self.voltage_dial.setObjectName(u"voltage_dial")
        self.voltage_dial.setMinimumSize(QSize(0, 150))
        self.voltage_dial.setSingleStep(1)
        self.voltage_dial.setWrapping(False)
        self.voltage_dial.setNotchesVisible(True)

        self.gridLayout_2.addWidget(self.voltage_dial, 0, 0, 1, 1)

        self.current_dial = QDial(self.manuel)
        self.current_dial.setObjectName(u"current_dial")
        self.current_dial.setMinimumSize(QSize(0, 150))
        self.current_dial.setWrapping(False)
        self.current_dial.setNotchesVisible(True)

        self.gridLayout_2.addWidget(self.current_dial, 0, 1, 1, 1)

        self.power_dial = QDial(self.manuel)
        self.power_dial.setObjectName(u"power_dial")
        self.power_dial.setMinimumSize(QSize(0, 150))
        self.power_dial.setWrapping(False)
        self.power_dial.setNotchesVisible(True)

        self.gridLayout_2.addWidget(self.power_dial, 0, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.apply_button = QPushButton(self.manuel)
        self.apply_button.setObjectName(u"apply_button")
        sizePolicy.setHeightForWidth(self.apply_button.sizePolicy().hasHeightForWidth())
        self.apply_button.setSizePolicy(sizePolicy)
        self.apply_button.setMinimumSize(QSize(0, 50))
        self.apply_button.setMaximumSize(QSize(16777215, 150))

        self.horizontalLayout.addWidget(self.apply_button)

        self.on_botton = QPushButton(self.manuel)
        self.on_botton.setObjectName(u"on_botton")
        sizePolicy.setHeightForWidth(self.on_botton.sizePolicy().hasHeightForWidth())
        self.on_botton.setSizePolicy(sizePolicy)
        self.on_botton.setMaximumSize(QSize(16777215, 150))
        self.on_botton.setCheckable(True)

        self.horizontalLayout.addWidget(self.on_botton)


        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 3)

        self.input_field_current = QLineEdit(self.manuel)
        self.input_field_current.setObjectName(u"input_field_current")

        self.gridLayout_2.addWidget(self.input_field_current, 1, 1, 1, 1)

        self.input_field_voltage = QLineEdit(self.manuel)
        self.input_field_voltage.setObjectName(u"input_field_voltage")

        self.gridLayout_2.addWidget(self.input_field_voltage, 1, 0, 1, 1)

        self.input_field_power = QLineEdit(self.manuel)
        self.input_field_power.setObjectName(u"input_field_power")

        self.gridLayout_2.addWidget(self.input_field_power, 1, 2, 1, 1)

        self.option_tabs.addTab(self.manuel, "")
        self.ui_curve = QWidget()
        self.ui_curve.setObjectName(u"ui_curve")
        self.horizontalLayout_2 = QHBoxLayout(self.ui_curve)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.layout_sliders = QVBoxLayout()
        self.layout_sliders.setObjectName(u"layout_sliders")
        self.layout_sliders.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.label_parralel_cells = QLabel(self.ui_curve)
        self.label_parralel_cells.setObjectName(u"label_parralel_cells")

        self.layout_sliders.addWidget(self.label_parralel_cells)

        self.layout_cells_parralel = QHBoxLayout()
        self.layout_cells_parralel.setObjectName(u"layout_cells_parralel")
        self.cells_parralel_input_slider = QSlider(self.ui_curve)
        self.cells_parralel_input_slider.setObjectName(u"cells_parralel_input_slider")
        self.cells_parralel_input_slider.setMinimumSize(QSize(250, 0))
        self.cells_parralel_input_slider.setMouseTracking(True)
        self.cells_parralel_input_slider.setTabletTracking(True)
        self.cells_parralel_input_slider.setMinimum(1)
        self.cells_parralel_input_slider.setOrientation(Qt.Orientation.Horizontal)

        self.layout_cells_parralel.addWidget(self.cells_parralel_input_slider)

        self.cells_parralel_input_field = QLineEdit(self.ui_curve)
        self.cells_parralel_input_field.setObjectName(u"cells_parralel_input_field")
        self.cells_parralel_input_field.setMinimumSize(QSize(100, 0))
        self.cells_parralel_input_field.setMaximumSize(QSize(200, 16777215))

        self.layout_cells_parralel.addWidget(self.cells_parralel_input_field)


        self.layout_sliders.addLayout(self.layout_cells_parralel)

        self.label_series_cells = QLabel(self.ui_curve)
        self.label_series_cells.setObjectName(u"label_series_cells")

        self.layout_sliders.addWidget(self.label_series_cells)

        self.layout_cells_series = QHBoxLayout()
        self.layout_cells_series.setObjectName(u"layout_cells_series")
        self.cells_series_input_slider = QSlider(self.ui_curve)
        self.cells_series_input_slider.setObjectName(u"cells_series_input_slider")
        self.cells_series_input_slider.setMinimumSize(QSize(250, 0))
        self.cells_series_input_slider.setMinimum(1)
        self.cells_series_input_slider.setOrientation(Qt.Orientation.Horizontal)

        self.layout_cells_series.addWidget(self.cells_series_input_slider)

        self.cells_series_input_field = QLineEdit(self.ui_curve)
        self.cells_series_input_field.setObjectName(u"cells_series_input_field")
        self.cells_series_input_field.setMinimumSize(QSize(100, 0))
        self.cells_series_input_field.setMaximumSize(QSize(200, 16777215))

        self.layout_cells_series.addWidget(self.cells_series_input_field)


        self.layout_sliders.addLayout(self.layout_cells_series)

        self.label_saturation_current = QLabel(self.ui_curve)
        self.label_saturation_current.setObjectName(u"label_saturation_current")

        self.layout_sliders.addWidget(self.label_saturation_current)

        self.layout_saturation_current = QHBoxLayout()
        self.layout_saturation_current.setObjectName(u"layout_saturation_current")
        self.saturation_current_input_slider = QSlider(self.ui_curve)
        self.saturation_current_input_slider.setObjectName(u"saturation_current_input_slider")
        self.saturation_current_input_slider.setMinimumSize(QSize(250, 0))
        self.saturation_current_input_slider.setMinimum(100)
        self.saturation_current_input_slider.setMaximum(999)
        self.saturation_current_input_slider.setValue(100)
        self.saturation_current_input_slider.setOrientation(Qt.Orientation.Horizontal)

        self.layout_saturation_current.addWidget(self.saturation_current_input_slider)

        self.saturation_current_input_field = QLineEdit(self.ui_curve)
        self.saturation_current_input_field.setObjectName(u"saturation_current_input_field")
        self.saturation_current_input_field.setMinimumSize(QSize(100, 0))
        self.saturation_current_input_field.setMaximumSize(QSize(200, 16777215))

        self.layout_saturation_current.addWidget(self.saturation_current_input_field)


        self.layout_sliders.addLayout(self.layout_saturation_current)

        self.label_diode_factor = QLabel(self.ui_curve)
        self.label_diode_factor.setObjectName(u"label_diode_factor")

        self.layout_sliders.addWidget(self.label_diode_factor)

        self.layout_diodefactor = QHBoxLayout()
        self.layout_diodefactor.setObjectName(u"layout_diodefactor")
        self.diodefactor_input_slider = QSlider(self.ui_curve)
        self.diodefactor_input_slider.setObjectName(u"diodefactor_input_slider")
        self.diodefactor_input_slider.setMinimumSize(QSize(250, 0))
        self.diodefactor_input_slider.setMinimum(10)
        self.diodefactor_input_slider.setMaximum(99)
        self.diodefactor_input_slider.setOrientation(Qt.Orientation.Horizontal)

        self.layout_diodefactor.addWidget(self.diodefactor_input_slider)

        self.diodefactor_input_field = QLineEdit(self.ui_curve)
        self.diodefactor_input_field.setObjectName(u"diodefactor_input_field")
        self.diodefactor_input_field.setMinimumSize(QSize(100, 0))
        self.diodefactor_input_field.setMaximumSize(QSize(200, 16777215))

        self.layout_diodefactor.addWidget(self.diodefactor_input_field)


        self.layout_sliders.addLayout(self.layout_diodefactor)

        self.label_thermalvoltage = QLabel(self.ui_curve)
        self.label_thermalvoltage.setObjectName(u"label_thermalvoltage")

        self.layout_sliders.addWidget(self.label_thermalvoltage)

        self.layout_themalvoltage = QHBoxLayout()
        self.layout_themalvoltage.setObjectName(u"layout_themalvoltage")
        self.thermalvoltage_input_slider = QSlider(self.ui_curve)
        self.thermalvoltage_input_slider.setObjectName(u"thermalvoltage_input_slider")
        self.thermalvoltage_input_slider.setMinimumSize(QSize(250, 0))
        self.thermalvoltage_input_slider.setMinimum(100)
        self.thermalvoltage_input_slider.setMaximum(999)
        self.thermalvoltage_input_slider.setOrientation(Qt.Orientation.Horizontal)

        self.layout_themalvoltage.addWidget(self.thermalvoltage_input_slider)

        self.thermalvoltage_input_field = QLineEdit(self.ui_curve)
        self.thermalvoltage_input_field.setObjectName(u"thermalvoltage_input_field")
        self.thermalvoltage_input_field.setMinimumSize(QSize(100, 0))
        self.thermalvoltage_input_field.setMaximumSize(QSize(200, 16777215))

        self.layout_themalvoltage.addWidget(self.thermalvoltage_input_field)


        self.layout_sliders.addLayout(self.layout_themalvoltage)

        self.label_photo_current_coefficient = QLabel(self.ui_curve)
        self.label_photo_current_coefficient.setObjectName(u"label_photo_current_coefficient")

        self.layout_sliders.addWidget(self.label_photo_current_coefficient)

        self.layout_photo_current_coefficient = QHBoxLayout()
        self.layout_photo_current_coefficient.setObjectName(u"layout_photo_current_coefficient")
        self.photo_current_coefficient_input_slider = QSlider(self.ui_curve)
        self.photo_current_coefficient_input_slider.setObjectName(u"photo_current_coefficient_input_slider")
        self.photo_current_coefficient_input_slider.setMinimumSize(QSize(250, 0))
        self.photo_current_coefficient_input_slider.setMinimum(100)
        self.photo_current_coefficient_input_slider.setMaximum(999)
        self.photo_current_coefficient_input_slider.setOrientation(Qt.Orientation.Horizontal)

        self.layout_photo_current_coefficient.addWidget(self.photo_current_coefficient_input_slider)

        self.photo_current_coefficient_input_field = QLineEdit(self.ui_curve)
        self.photo_current_coefficient_input_field.setObjectName(u"photo_current_coefficient_input_field")
        self.photo_current_coefficient_input_field.setMinimumSize(QSize(100, 0))
        self.photo_current_coefficient_input_field.setMaximumSize(QSize(200, 16777215))

        self.layout_photo_current_coefficient.addWidget(self.photo_current_coefficient_input_field)


        self.layout_sliders.addLayout(self.layout_photo_current_coefficient)

        self.reset_diode_modell = QPushButton(self.ui_curve)
        self.reset_diode_modell.setObjectName(u"reset_diode_modell")

        self.layout_sliders.addWidget(self.reset_diode_modell)


        self.horizontalLayout_2.addLayout(self.layout_sliders)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.plot_3d_preview = QWidget(self.ui_curve)
        self.plot_3d_preview.setObjectName(u"plot_3d_preview")
        self.plot_3d_preview.setMinimumSize(QSize(500, 250))

        self.verticalLayout.addWidget(self.plot_3d_preview)

        self.turnbar_3d_preview = QScrollBar(self.ui_curve)
        self.turnbar_3d_preview.setObjectName(u"turnbar_3d_preview")
        self.turnbar_3d_preview.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.turnbar_3d_preview)

        self.apply_3d_preview_button = QPushButton(self.ui_curve)
        self.apply_3d_preview_button.setObjectName(u"apply_3d_preview_button")
        sizePolicy.setHeightForWidth(self.apply_3d_preview_button.sizePolicy().hasHeightForWidth())
        self.apply_3d_preview_button.setSizePolicy(sizePolicy)
        self.apply_3d_preview_button.setMinimumSize(QSize(0, 50))
        self.apply_3d_preview_button.setMaximumSize(QSize(16777215, 150))

        self.verticalLayout.addWidget(self.apply_3d_preview_button)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.option_tabs.addTab(self.ui_curve, "")
        self.curve_control = QWidget()
        self.curve_control.setObjectName(u"curve_control")
        self.horizontalLayout_4 = QHBoxLayout(self.curve_control)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.irradiance_label = QLabel(self.curve_control)
        self.irradiance_label.setObjectName(u"irradiance_label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.irradiance_label.sizePolicy().hasHeightForWidth())
        self.irradiance_label.setSizePolicy(sizePolicy3)
        self.irradiance_label.setMinimumSize(QSize(0, 50))
        self.irradiance_label.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_3.addWidget(self.irradiance_label)

        self.irradiance_dial = QDial(self.curve_control)
        self.irradiance_dial.setObjectName(u"irradiance_dial")
        self.irradiance_dial.setMaximum(100)
        self.irradiance_dial.setSingleStep(1)
        self.irradiance_dial.setInvertedAppearance(False)
        self.irradiance_dial.setInvertedControls(False)
        self.irradiance_dial.setNotchesVisible(True)

        self.verticalLayout_3.addWidget(self.irradiance_dial)

        self.irradiance_input_field = QLineEdit(self.curve_control)
        self.irradiance_input_field.setObjectName(u"irradiance_input_field")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.irradiance_input_field.sizePolicy().hasHeightForWidth())
        self.irradiance_input_field.setSizePolicy(sizePolicy4)

        self.verticalLayout_3.addWidget(self.irradiance_input_field)

        self.curve_on_off = QPushButton(self.curve_control)
        self.curve_on_off.setObjectName(u"curve_on_off")
        sizePolicy.setHeightForWidth(self.curve_on_off.sizePolicy().hasHeightForWidth())
        self.curve_on_off.setSizePolicy(sizePolicy)
        self.curve_on_off.setMaximumSize(QSize(16777215, 150))
        self.curve_on_off.setCheckable(True)

        self.verticalLayout_3.addWidget(self.curve_on_off)


        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.curve_view_layout = QVBoxLayout()
        self.curve_view_layout.setObjectName(u"curve_view_layout")
        self.placeholder_3d_view = QWidget(self.curve_control)
        self.placeholder_3d_view.setObjectName(u"placeholder_3d_view")

        self.curve_view_layout.addWidget(self.placeholder_3d_view)

        self.horizontalScrollBar_3 = QScrollBar(self.curve_control)
        self.horizontalScrollBar_3.setObjectName(u"horizontalScrollBar_3")
        self.horizontalScrollBar_3.setOrientation(Qt.Orientation.Horizontal)

        self.curve_view_layout.addWidget(self.horizontalScrollBar_3)

        self.placeholder_2d_view = QWidget(self.curve_control)
        self.placeholder_2d_view.setObjectName(u"placeholder_2d_view")

        self.curve_view_layout.addWidget(self.placeholder_2d_view)

        self.import_button = QPushButton(self.curve_control)
        self.import_button.setObjectName(u"import_button")

        self.curve_view_layout.addWidget(self.import_button)


        self.horizontalLayout_4.addLayout(self.curve_view_layout)

        self.option_tabs.addTab(self.curve_control, "")

        self.gridLayout.addWidget(self.option_tabs, 2, 0, 1, 1)


        self.retranslateUi(Dialog)

        self.option_tabs.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.voltage_label.setText(QCoreApplication.translate("Dialog", u"Voltage", None))
        self.power_label.setText(QCoreApplication.translate("Dialog", u"Current", None))
        self.current_label.setText(QCoreApplication.translate("Dialog", u"Power", None))
        self.port_label.setText(QCoreApplication.translate("Dialog", u"Port:", None))
        self.port_field.setInputMask(QCoreApplication.translate("Dialog", u"0000", None))
        self.ip_address_label.setText(QCoreApplication.translate("Dialog", u"IP Address:", None))
        self.connect_button.setText(QCoreApplication.translate("Dialog", u"Connect", None))
        self.ip_address_field.setInputMask(QCoreApplication.translate("Dialog", u"000.000.000.000", None))
        self.option_tabs.setTabText(self.option_tabs.indexOf(self.connection), QCoreApplication.translate("Dialog", u"Connection", None))
        self.apply_button.setText(QCoreApplication.translate("Dialog", u"Apply", None))
        self.on_botton.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.input_field_current.setInputMask(QCoreApplication.translate("Dialog", u"00.0", None))
        self.input_field_current.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.input_field_voltage.setInputMask(QCoreApplication.translate("Dialog", u"00.0", None))
        self.input_field_voltage.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.input_field_power.setInputMask(QCoreApplication.translate("Dialog", u"00.0", None))
        self.input_field_power.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.option_tabs.setTabText(self.option_tabs.indexOf(self.manuel), QCoreApplication.translate("Dialog", u"Manuel", None))
        self.label_parralel_cells.setText(QCoreApplication.translate("Dialog", u"cell_p (solar cells in parralel):", None))
        self.cells_parralel_input_field.setInputMask(QCoreApplication.translate("Dialog", u"0000", None))
        self.label_series_cells.setText(QCoreApplication.translate("Dialog", u"cell_s (solar cells in series):", None))
        self.cells_series_input_field.setInputMask(QCoreApplication.translate("Dialog", u"0000", None))
        self.label_saturation_current.setText(QCoreApplication.translate("Dialog", u"I_s (saturation current):", None))
        self.saturation_current_input_field.setInputMask(QCoreApplication.translate("Dialog", u"0.00", None))
        self.label_diode_factor.setText(QCoreApplication.translate("Dialog", u"m (diodefactor):", None))
        self.diodefactor_input_field.setInputMask(QCoreApplication.translate("Dialog", u"0.0", None))
        self.label_thermalvoltage.setText(QCoreApplication.translate("Dialog", u"U_T (Thermalvoltage):", None))
        self.thermalvoltage_input_field.setInputMask(QCoreApplication.translate("Dialog", u"00.0", None))
        self.label_photo_current_coefficient.setText(QCoreApplication.translate("Dialog", u"c_0 (photo current coefficient):", None))
        self.photo_current_coefficient_input_field.setInputMask(QCoreApplication.translate("Dialog", u"0.00", None))
        self.reset_diode_modell.setText(QCoreApplication.translate("Dialog", u"Reset", None))
        self.apply_3d_preview_button.setText(QCoreApplication.translate("Dialog", u"Apply", None))
        self.option_tabs.setTabText(self.option_tabs.indexOf(self.ui_curve), QCoreApplication.translate("Dialog", u"Diode Model", None))
        self.irradiance_label.setText(QCoreApplication.translate("Dialog", u"Irradiance E:", None))
        self.irradiance_input_field.setInputMask(QCoreApplication.translate("Dialog", u"0000", None))
        self.curve_on_off.setText(QCoreApplication.translate("Dialog", u"On", None))
        self.import_button.setText(QCoreApplication.translate("Dialog", u"Import", None))
        self.option_tabs.setTabText(self.option_tabs.indexOf(self.curve_control), QCoreApplication.translate("Dialog", u"Curve control", None))
    # retranslateUi

