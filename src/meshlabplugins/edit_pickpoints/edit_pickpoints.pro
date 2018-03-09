include (../../shared.pri)

#				../../meshlab/avner_imageviewer.h \
DEFINES += QT_NO_PRINTER

HEADERS      += edit_pickpoints_factory.h \
				editpickpoints.h \
				pickpointsDialog.h \
				pickedPoints.h \
				pickPointsTemplate.h \
				../../meshlab/stdpardialog.h \
				../../meshlab/imageviewer.h \


# ../../meshlab/avner_imageviewer.cpp \

SOURCES      += edit_pickpoints_factory.cpp \
				editpickpoints.cpp \
				pickpointsDialog.cpp \
				pickedPoints.cpp \
				pickPointsTemplate.cpp \
				../../meshlab/stdpardialog.cpp \
				../../meshlab/imageviewer.cpp \

RESOURCES    += editpickpoints.qrc

FORMS        += pickpointsDialog.ui


# Avner

HUGIN_INC_PATH = -I/home/avner/Downloads/hugin-2018.0.0/mybuild/src -I/home/avner/Downloads/hugin-2018.0.0/src/hugin_base -I/home/avner/Downloads/hugin-2018.0.0/src/celeste -I/home/avner/Downloads/hugin-2018.0.0/mybuild/src/celeste -I/home/avner/Downloads/hugin-2018.0.0/src -I/home/avner/anaconda3/include -I/usr/include/OpenEXR -I/usr/local/include -I/home/avner/anaconda3/include/python3.6m

INCLUDEPATH +=	/mnt/avner/softwarelib/OpenCV-2.4.3/modules/calib3d/include \
		/mnt/avner/softwarelib/OpenCV-2.4.3/modules/core/include \
		/mnt/avner/softwarelib/OpenCV-2.4.3/modules/imgproc/include \
		/mnt/avner/softwarelib/OpenCV-2.4.3/modules/features2d/include \
		/mnt/avner/softwarelib/OpenCV-2.4.3/modules/flann/include \
		/mnt/avner/softwarelib/OpenCV-2.4.3/modules/highgui/include \
                /mnt/avner/softwarelib/boost/boost_1_65_1/localBuild/usr/local/include/ \
                /home/avner/Downloads/hugin-2018.0.0/mybuild/src /home/avner/Downloads/hugin-2018.0.0/src/hugin_base /home/avner/Downloads/hugin-2018.0.0/src/celeste /home/avner/Downloads/hugin-2018.0.0/mybuild/src/celeste /home/avner/Downloads/hugin-2018.0.0/src /home/avner/anaconda3/include /usr/include/OpenEXR /usr/local/include /home/avner/anaconda3/include/python3.6m

# LIBS += -lkyotocabinet
# LIBPATH +=  /../../external/kyotocabinet-1.2.34
# linux-g++:LIBS += ../../external/lib/linux-g++/libmpirxx.a ../../external/lib/linux-g++/libmpir.a
`
# LIBS += -lopencv_features2d -lopencv_flann -lopencv_calib3d
# LIBPATH += /mnt/avner/softwarelib/OpenCV-2.4.3/build/lib

HUGIN_LIBS = -rdynamic /home/avner/Downloads/hugin-2018.0.0/mybuild/src/hugin_base/libhuginbase.so.0.0 /usr/lib/x86_64-linux-gnu/libpano13.so /home/avner/Downloads/hugin-2018.0.0/mybuild/src/foreign/levmar/libhuginlevmar.a -lGLEW -lboost_filesystem -lboost_system /usr/local/lib/libvigraimpex.so -lImath -lIlmImf -lIex -lHalf -lIlmThread /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/x86_64-linux-gnu/libtiff.so /usr/lib/x86_64-linux-gnu/libpng.so /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/x86_64-linux-gnu/libz.so /usr/local/lib/libexiv2.so -llcms2 -pthread -lX11 /usr/lib/x86_64-linux-gnu/libpano13.so -lboost_filesystem -lboost_system -lGLU -lGL -lGLEW /usr/lib/x86_64-linux-gnu/libsqlite3.so /usr/local/lib/libvigraimpex.so /usr/lib/x86_64-linux-gnu/libtiff.so /usr/local/lib/libexiv2.so -llcms2 -Wl,-rpath,/home/avner/Downloads/hugin-2018.0.0/mybuild/src/hugin_base:/usr/lib/x86_64-linux-gnu:/usr/local/lib:

LIBS += /usr/lib/x86_64-linux-gnu/libopencv_features2d.so.2.4 \
	/usr/lib/x86_64-linux-gnu/libopencv_flann.so.2.4 \
	/usr/lib/x86_64-linux-gnu/libopencv_calib3d.so.2.4 \
        -L /mnt/avner/softwarelib/boost/boost_1_65_1/localBuild/usr/local/lib -lboost_system \
        -rdynamic /home/avner/Downloads/hugin-2018.0.0/mybuild/src/hugin_base/libhuginbase.so.0.0 /usr/lib/x86_64-linux-gnu/libpano13.so /home/avner/Downloads/hugin-2018.0.0/mybuild/src/foreign/levmar/libhuginlevmar.a -lGLEW -lboost_filesystem -lboost_system /usr/local/lib/libvigraimpex.so -lImath -lIlmImf -lIex -lHalf -lIlmThread /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/x86_64-linux-gnu/libtiff.so /usr/lib/x86_64-linux-gnu/libpng.so /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/x86_64-linux-gnu/libz.so /usr/local/lib/libexiv2.so -llcms2 -pthread -lX11 /usr/lib/x86_64-linux-gnu/libpano13.so -lboost_filesystem -lboost_system -lGLU -lGL -lGLEW /usr/lib/x86_64-linux-gnu/libsqlite3.so /usr/local/lib/libvigraimpex.so /usr/lib/x86_64-linux-gnu/libtiff.so /usr/local/lib/libexiv2.so -llcms2 -Wl,-rpath,/home/avner/Downloads/hugin-2018.0.0/mybuild/src/hugin_base:/usr/lib/x86_64-linux-gnu:/usr/local/lib:

TARGET        = edit_pickpoints

CONFIG += debug
