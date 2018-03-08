/****************************************************************************
* MeshLab                                                           o o     *
* An extendible mesh processor                                    o     o   *
*                                                                _   O  _   *
* Copyright(C) 2005, 2009                                          \/)\/    *
* Visual Computing Lab                                            /\/|      *
* ISTI - Italian National Research Council                           |      *
*                                                                    \      *
* All rights reserved.                                                      *
*                                                                           *
* This program is free software; you can redistribute it and/or modify      *
* it under the terms of the GNU General Public License as published by      *
* the Free Software Foundation; either version 2 of the License, or         *
* (at your option) any later version.                                       *
*                                                                           *
* This program is distributed in the hope that it will be useful,           *
* but WITHOUT ANY WARRANTY; without even the implied warranty of            *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             *
* GNU General Public License (http://www.gnu.org/licenses/gpl.txt)          *
* for more details.                                                         *
*                                                                           *
****************************************************************************/

/* A class to represent the ui for the pickpoints plugin
 *
 * @author Oscar Barney
 */

#include <QFileDialog>
#include <math.h>
#include <vector>

#include <common/meshmodel.h>
#include <meshlab/stdpardialog.h>

#include "editpickpoints.h"
#include "pickpointsDialog.h"

#include <vcg/space/index/grid_static_ptr.h>
#include <vcg/complex/algorithms/closest.h>

#include <QGLWidget>

using namespace vcg;

#define AVNER_PP

#ifdef AVNER_PP
// /mnt/avner/softwarelib/OpenCV-2.4.3/modules/calib3d/include/opencv2/calib3d/calib3d.hpp
#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/calib3d/calib3d.hpp"
#include "opencv2/highgui/highgui.hpp"
 
#include <iostream>
#include <string>

#define ADD_HUGIN

#ifdef ADD_HUGIN
#include <panodata/Panorama.h>
#include <panotools/PanoToolsInterface.h>
#include "../../meshlab/mainwindow.h"
#include "../../meshlab/imagelistmodel.h"
#else
#endif


// /mnt/avner/softwarelib/boost/boost_1_59_0/boost/filesystem.hpp
#include <boost/filesystem.hpp>
#include <QScrollArea>

std::vector<cv::Point2f> Generate2DPoints();
std::vector<cv::Point3f> Generate3DPoints();


// Try2
#include "../../meshlab/imageviewer.h"
ImageViewer* imageviewer2;

// Try1
std::vector<std::string> textures2;
QLabel topLevelLabel;
QScrollArea scrollArea;
bool firstTime = false;

namespace
{
    bool findOtherVertexInAdjacentFaceWithSameMaterial(CMeshO::FaceType* face,
        const int materialIndex,
        CMeshO::FaceType*& otherFace,
        int& otherVertexIndex)
    {
    
        qDebug() << "Beg findOtherVertexInAdjacentFaceWithSameMaterial";
        qDebug() << "face2: " << (CMeshO::FaceType*)face;
        for (int edgeIndex = 0; edgeIndex < 3; edgeIndex++)
        {
            qDebug() << "edgeIndex: " << edgeIndex;
            otherFace = face->FFp(edgeIndex);
            qDebug() << "otherFace: " << (void*)otherFace;

            bool cond0 = (otherFace != NULL);
            qDebug() << "cond0: " << cond0;

            bool cond1 = ((void*)otherFace != (void*)face);
            qDebug() << "cond1: " << cond1;

            bool cond2 = ((void*)otherFace == (void*)face);
            qDebug() << "cond2: " << cond2;

            if (cond1 && cond1)
            // if(otherFace != NULL)
            {
                int otherMaterialIndex = otherFace->WT(0).n();
                if (materialIndex == otherMaterialIndex)
                {
                    // found the matching face
                    qDebug() << "edgeIndex: " << edgeIndex;

                    // FFi(i): the index of edge that corresponds to i-th edge of f in the pointed face
                    int otherEdgeIndex = face->FFi(edgeIndex);
                    qDebug() << "otherEdgeIndex: " << otherEdgeIndex;
                    otherVertexIndex = (otherEdgeIndex + 2) % 3;
                    qDebug() << "otherVertexIndex: " << otherVertexIndex;

                    qDebug() << "otherFace->WT(0) u,v: " << otherFace->WT(0).u() << ", " << otherFace->WT(0).v();
                    qDebug() << "otherFace->WT(1) u,v: " << otherFace->WT(1).u() << ", " << otherFace->WT(1).v();
                    qDebug() << "otherFace->WT(2) u,v: " << otherFace->WT(2).u() << ", " << otherFace->WT(2).v();

                    qDebug() << "otherFace->P(0) x,y,z: " << otherFace->P(0).X() << ", " << otherFace->P(0).Y() << ", " << otherFace->P(0).Z();
                    qDebug() << "otherFace->P(1) x,y,z: " << otherFace->P(1).X() << ", " << otherFace->P(1).Y() << ", " << otherFace->P(1).Z();
                    qDebug() << "otherFace->P(2) x,y,z: " << otherFace->P(2).X() << ", " << otherFace->P(2).Y() << ", " << otherFace->P(2).Z();

                    return true;
                }
            }
        }
        return false;
    }

    bool calcPointAttributes2(CMeshO::FaceType* face,
        const int materialIndex,
        const Point3m& addedPoint3d,
        ObjTexCoord2& addedPoint_texCoords)
    {
        qDebug() << "Beg calcPointAttributes2";
        qDebug() << "face1: " << (CMeshO::FaceType*)face;
        // TBD - calc u,v of added point
        // use ~/avner/constructionOverlay/tmp/calcTransformationMat.py
        //
        qDebug() << "face->WT(0) u,v: " << face->WT(0).u() << ", " << face->WT(0).v();
        qDebug() << "face->WT(1) u,v: " << face->WT(1).u() << ", " << face->WT(1).v();
        qDebug() << "face->WT(2) u,v: " << face->WT(2).u() << ", " << face->WT(2).v();

        qDebug() << "face->P(0) x,y,z: " << face->P(0).X() << ", " << face->P(0).Y() << ", " << face->P(0).Z();
        qDebug() << "face->P(1) x,y,z: " << face->P(1).X() << ", " << face->P(1).Y() << ", " << face->P(1).Z();
        qDebug() << "face->P(2) x,y,z: " << face->P(2).X() << ", " << face->P(2).Y() << ", " << face->P(2).Z();

        /////////////////////////////
        // Find the 4th point
        // we need 4 3d points, and their equivalent 2d points, in order to computer the transformation matrix
        // the transformation matrix is then used to project from the selected 3d point to 2d 
        /////////////////////////////

        CMeshO::FaceType* otherFace;
        int otherVertexIndex;
        if (findOtherVertexInAdjacentFaceWithSameMaterial(face, materialIndex, otherFace, otherVertexIndex))
        {
            qDebug() << "otherFace1: " << (void*)otherFace;
            qDebug() << "otherVertexIndex1: " << otherVertexIndex;
            // x,y,z
            qDebug() << "otherFace->P(otherVertexIndex) x,y,z: " << otherFace->P(otherVertexIndex).X()
                     << ", " << otherFace->P(otherVertexIndex).Y()
                     << ", " << otherFace->P(otherVertexIndex).Z();
            // u,v
            qDebug() << "otherFace->WT(otherVertexIndex) u,v: " << otherFace->WT(otherVertexIndex).u()
                     << ", " << otherFace->WT(otherVertexIndex).v();

            /////////////////////////////
            // Find the transformation matrix
            /////////////////////////////

            // https://github.com/daviddoria/Examples/blob/master/c%2B%2B/OpenCV/SolvePNP/SolvePNP.cxx

            std::vector<cv::Point2f> imagePoints;
            imagePoints.push_back(cv::Point2f(face->WT(0).u(), face->WT(0).v()));
            imagePoints.push_back(cv::Point2f(face->WT(1).u(), face->WT(1).v()));
            imagePoints.push_back(cv::Point2f(face->WT(2).u(), face->WT(2).v()));
            imagePoints.push_back(cv::Point2f(otherFace->WT(otherVertexIndex).u(), otherFace->WT(otherVertexIndex).v()));

            std::vector<cv::Point3f> objectPoints;
            objectPoints.push_back(cv::Point3f(face->P(0).X(), face->P(0).Y(), face->P(0).Z()));
            objectPoints.push_back(cv::Point3f(face->P(1).X(), face->P(1).Y(), face->P(1).Z()));
            objectPoints.push_back(cv::Point3f(face->P(2).X(), face->P(2).Y(), face->P(2).Z()));
            objectPoints.push_back(cv::Point3f(otherFace->P(otherVertexIndex).X(),
                otherFace->P(otherVertexIndex).Y(),
                otherFace->P(otherVertexIndex).Z()));

            cv::Mat cameraMatrix(3, 3, cv::DataType<double>::type);
            cv::setIdentity(cameraMatrix);

            float fx = 1.0;
            float h = 10000.0;
            float w = 10000.0;

            // test.at<cv::Vec2f>[y][x][0] = 1.0
            double val1 = fx * w;
            std::cout << "val1: " << val1 << std::endl;

            cameraMatrix.at<double>(0, 0) = val1;
            cameraMatrix.at<double>(0, 2) = 0.5 * (w - 1);
            cameraMatrix.at<double>(1, 1) = fx * w;
            cameraMatrix.at<double>(1, 2) = 0.5 * (h - 1);
            cameraMatrix.at<double>(2, 2) = 1.0;

            std::cout << "cameraMatrix: " << cameraMatrix << std::endl;
            // TBD populate cameraMatrix
            // K = np.float64([[fx*w, 0, 0.5*(w-1)],
            //                 [0, fx*w, 0.5*(h-1)],
            //                 [0.0,0.0,      1.0]])

            cv::Mat distCoeffs(4, 1, cv::DataType<double>::type);
            distCoeffs.at<double>(0) = 0;
            distCoeffs.at<double>(1) = 0;
            distCoeffs.at<double>(2) = 0;
            distCoeffs.at<double>(3) = 0;

            cv::Mat rvec(3, 1, cv::DataType<double>::type);
            cv::Mat tvec(3, 1, cv::DataType<double>::type);

            cv::solvePnP(objectPoints, imagePoints, cameraMatrix, distCoeffs, rvec, tvec);

            std::vector<cv::Point3f> points3d_new;
            qDebug() << "point3d_new x,y,z: " << addedPoint3d[0] << " " << addedPoint3d[1] << " " << addedPoint3d[2];
            points3d_new.push_back(cv::Point3f(addedPoint3d[0], addedPoint3d[1], addedPoint3d[2]));

            std::vector<cv::Point2f> points2d_new;
            cv::projectPoints(points3d_new, rvec, tvec, cameraMatrix, distCoeffs, points2d_new);
            std::cout << "added point: " << points3d_new[0]
                      << " Projected to " << points2d_new << std::endl;

            cv::Point2f point2d_new = points2d_new[0];
            std::cout << "point2d_new: " << point2d_new.x << " " << point2d_new.y << std::endl;
            addedPoint_texCoords.u = point2d_new.x;
            addedPoint_texCoords.v = point2d_new.y;
        }
        return true;
    }

#ifdef AVNER_ADD_IMAGE_VIEWER

    bool mapPointFromPanoramaToImages(const int materialIndex,
                                      const QPointF& qPointF,
                                      std::list<std::string>& filenames,
                                      std::list<QPointF>& qPointFs)
{
    qDebug() << "Beg mapPointFromPanoramaToImages()";
    qDebug() << "qPointF2: " << qPointF;

#ifdef ADD_HUGIN

        std::string textureName = textures2[materialIndex];
        // room1/wall1/wall_fused.jpg
        qDebug() << "textureName0: " << textureName.c_str();

        // room1/wall1/wall_fused.jpg -> room1/wall1/
        // "/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/" + room1/wall1/ + "wall.pto" -> "room1/wall1/wall.pto"

        boost::filesystem::path p(textureName.c_str());
        boost::filesystem::path dir = p.parent_path();
        std::string dir1 = dir.string();
        qDebug() << "dir: " << dir1.c_str();

        std::string panoFilename1;
        // panoFilename1 = std::string("/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/") +
        //                std::string(dir1.c_str()) +
        //                std::string("/wall.pto");

        panoFilename1 = std::string("/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/") +
                       std::string(dir1.c_str()) +
                       std::string("/wall.pto");
        
        qDebug() << "panoFilename1: " << panoFilename1.c_str();

        // // RemoveME:
        // return true;

    std::string panoFilename;
    panoFilename = panoFilename1;
    
    std::cout << "panoFilename: " << panoFilename << std::endl;
    qDebug() << "foo13";

    HuginBase::Panorama pano2;
    std::ifstream prjfile(panoFilename);
    if (!prjfile.good())
    {
        std::cerr << "could not open script : " << panoFilename << std::endl;
        return 1;
    }

    
    pano2.setFilePrefix(hugin_utils::getPathPrefix(panoFilename));

    AppBase::DocumentData::ReadWriteError err = pano2.readData(prjfile);
    if (err != AppBase::DocumentData::SUCCESSFUL)
    {
        std::cerr << "error while parsing panos tool script: " << panoFilename << std::endl;
        std::cerr << "AppBase::DocumentData::ReadWriteError code: " << err << std::endl;
        return false;
    }

    int left = pano2.getOptions().getROI().left();
    int right = pano2.getOptions().getROI().right();
    int top = pano2.getOptions().getROI().top();
    int bottom = pano2.getOptions().getROI().bottom();
    std::cout << "ROI (left, right, top, bottom) " << left
              << " " << right
              << " " << top
              << " " << bottom
              << std::endl ;

    std::cout << "pano2.getNrOfImages(): " << pano2.getNrOfImages() << std::endl;

    filenames.clear();
    qPointFs.clear();
    int numThumbnails = 0;
    
    for(size_t imageIndex=0; imageIndex<pano2.getNrOfImages(); imageIndex++)
    {
        std::string fileName(pano2.getImage(imageIndex).getFilename());
        std::cout << "fileName: " << fileName << std::endl;

        // project qPointF to image. check if it falls inside the image
        HuginBase::PTools::Transform trafo;
        trafo.createTransform(pano2.getSrcImage(imageIndex), pano2.getOptions());

        double xin2 = qPointF.x() + left;
        double yin2 = qPointF.y() + top;
        double xout, yout;
        trafo.transformImgCoord(xout, yout, xin2, yin2);

        QPointF qPointFout(xout, yout);
        std::cout << "xout, yout: " << xout
                  << " " << yout << std::endl;

        if (pano2.getImage(imageIndex).isInside(vigra::Point2D(int(xout), int (yout))))
        { 
            std::cout << "Inside" << std::endl;

            // TBD
            // add (xout, yout) into the thumbnail info, so it could be drawn on imageViewer
            // when the thumbnail is selected ???
            
            // Add to list of filenames
            filenames.push_back(fileName);
            qPointFs.push_back(qPointFout);
            numThumbnails++;
            
        }
        else
        {
            std::cout << "Outside" << std::endl;
        }
        
    };

    {
        std::stringstream ss;
        std::list<std::string>::iterator it; // same as: const int* it
        for (it = filenames.begin(); it != filenames.end(); ++it) ss << ' ' << *it;
        std::cout << "filenames: " << ss.str() << std::endl;
    }

    {
        std::stringstream ss;
        std::list<QPointF>::iterator it; // same as: const int* it
        for (it = qPointFs.begin(); it != qPointFs.end(); ++it)
        {
            QPointF qPointF = *it;
            ss << ' ' << qPointF.x() << ", " << qPointF.y();
        }
        std::cout << "qPointFs: " << ss.str() << std::endl;
    }
    
#else
#endif
    
    
    return true;
}
#else
#endif
    
}

#else
#endif
 


class GetClosestFace
{

	typedef GridStaticPtr<CMeshO::FaceType, CMeshO::ScalarType > MetroMeshGrid;
	typedef tri::FaceTmark<CMeshO> MarkerFace;

public:

	GetClosestFace() {}

	void init(CMeshO *_m)
	{
		m = _m;
		if (m)
		{
			unifGrid.Set(m->face.begin(), m->face.end());
			markerFunctor.SetMesh(m);
			dist_upper_bound = m->bbox.Diag() / 10.0f;
		}
	}

	CMeshO *m;

	MetroMeshGrid unifGrid;

	MarkerFace markerFunctor;

	Scalarm dist_upper_bound;

	CMeshO::FaceType * getFace(Point3m &p)
	{
		assert(m);
		// the results
		Point3m closestPt;
		Scalarm dist = dist_upper_bound;
		const CMeshO::CoordType &startPt = p;

		// compute distance between startPt and the mesh S2
		CMeshO::FaceType   *nearestF = 0;
		vcg::face::PointDistanceBaseFunctor<CMeshO::ScalarType> PDistFunct;
		dist = dist_upper_bound;

		nearestF = unifGrid.GetClosest(PDistFunct, markerFunctor, startPt, dist_upper_bound, dist, closestPt);

		if (dist == dist_upper_bound) qDebug() << "Dist is = upper bound";

		return nearestF;
	}
};

PickedPointTreeWidgetItem::PickedPointTreeWidgetItem(
	Point3m &intputPoint, CMeshO::FaceType::NormalType &faceNormal,
	QString name, bool _active) : QTreeWidgetItem(1001)
{
	//name
	setName(name);

	active = _active;
	//would set the checkbox but qt doesnt allow a way to do this in the constructor

	//set point and normal
	setPointAndNormal(intputPoint, faceNormal);
}

void PickedPointTreeWidgetItem::setName(QString name) {
	setText(0, name);
}

QString PickedPointTreeWidgetItem::getName() {
	return text(0);
}

void PickedPointTreeWidgetItem::setPointAndNormal(Point3m &intputPoint, CMeshO::FaceType::NormalType &faceNormal)
{
	point[0] = intputPoint[0];
	point[1] = intputPoint[1];
	point[2] = intputPoint[2];

	normal[0] = faceNormal[0];
	normal[1] = faceNormal[1];
	normal[2] = faceNormal[2];

	QString tempString;
	//x
	tempString.setNum(point[0]);
	setText(1, tempString);
	//y
	tempString.setNum(point[1]);
	setText(2, tempString);
	//z
	tempString.setNum(point[2]);
	setText(3, tempString);
}

Point3m PickedPointTreeWidgetItem::getPoint() {
	return point;
}

Point3m PickedPointTreeWidgetItem::getNormal() {
	return normal;
}

void PickedPointTreeWidgetItem::clearPoint() {
	point.SetZero();

	//x
	setText(1, "");
	//y
	setText(2, "");
	//z
	setText(3, "");

	setActive(false);
}

bool PickedPointTreeWidgetItem::isActive()
{
	return active;
}

void PickedPointTreeWidgetItem::setActive(bool value)
{
	active = value;

	//stupid way QT makes you get a widget associated with this item
	QTreeWidget * treeWidget = this->treeWidget();
	assert(treeWidget);
	QWidget *widget = treeWidget->itemWidget(this, 4);
	assert(widget);
	QCheckBox *checkBox = qobject_cast<QCheckBox *>(widget);
	assert(checkBox);
	checkBox->setChecked(value);
}

void PickedPointTreeWidgetItem::toggleActive(bool value)
{
	active = value;
}

PickPointsDialog::PickPointsDialog(EditPickPointsPlugin *plugin,
	QWidget *parent) : QDockWidget(parent)
{
	parentPlugin = plugin;

	//qt standard setup step
	PickPointsDialog::ui.setupUi(this);

	//setup borrowed from alighnDialog.cpp
	this->setWidget(ui.frame);
	this->setFeatures(QDockWidget::AllDockWidgetFeatures);
	this->setAllowedAreas(Qt::LeftDockWidgetArea);
	QPoint p = parent->mapToGlobal(QPoint(0, 0));
	this->setFloating(true);
	this->setGeometry(p.x() + (parent->width() - width()), p.y() + 40, width(), height());

	//now stuff specific to pick points
	QStringList headerNames;
	headerNames << "Point Name" << "X" << "Y" << "Z" << "active";

	ui.pickedPointsTreeWidget->setHeaderLabels(headerNames);

	//init some variables

	//set to nothing for now
	lastPointToMove = 0;
	itemToMove = 0;
	meshModel = 0;
	_glArea = 0;

	//start at 0
	pointCounter = 0;

	//start with no template
	setTemplateName("");

	currentMode = ADD_POINT;

	recordPointForUndo = false;

	getClosestFace = new GetClosestFace();

	//signals and slots
	connect(ui.removePointButton, SIGNAL(clicked()), this, SLOT(removeHighlightedPoint()));

	//rename when rename button clicked
	connect(ui.renamePointButton, SIGNAL(clicked()), this, SLOT(renameHighlightedPoint()));

	//rename on double click of point
	connect(ui.pickedPointsTreeWidget, SIGNAL(itemDoubleClicked(QTreeWidgetItem *, int)),
		this, SLOT(renameHighlightedPoint()));

	connect(ui.clearPointButton, SIGNAL(clicked()), this, SLOT(clearHighlightedPoint()));
	connect(ui.pickPointModeRadioButton, SIGNAL(toggled(bool)), this, SLOT(togglePickMode(bool)));
	connect(ui.movePointRadioButton, SIGNAL(toggled(bool)), this, SLOT(toggleMoveMode(bool)));
	connect(ui.selectPointRadioButton, SIGNAL(toggled(bool)), this, SLOT(toggleSelectMode(bool)));
	connect(ui.saveButton, SIGNAL(clicked()), this, SLOT(savePointsToFile()));
	connect(ui.loadPointsButton, SIGNAL(clicked()), this, SLOT(askUserForFileAndLoadPoints()));
	connect(ui.removeAllPointsButton, SIGNAL(clicked()), this, SLOT(clearPointsButtonClicked()));
	connect(ui.saveTemplateButton, SIGNAL(clicked()), this, SLOT(savePointTemplate()));
	connect(ui.loadTemplateButton, SIGNAL(clicked()), this, SLOT(askUserForFileAndloadTemplate()));
	connect(ui.clearTemplateButton, SIGNAL(clicked()), this, SLOT(clearTemplateButtonClicked()));
	connect(ui.addPointToTemplateButton, SIGNAL(clicked()), this, SLOT(addPointToTemplate()));
	connect(ui.undoButton, SIGNAL(clicked()), this, SLOT(undo()));
	connect(ui.pickedPointsTreeWidget, SIGNAL(itemClicked(QTreeWidgetItem *, int)), this,
		SLOT(redrawPoints()));

	connect(ui.showNormalCheckBox, SIGNAL(clicked()), this, SLOT(redrawPoints()));
	connect(ui.pinRadioButton, SIGNAL(clicked()), this, SLOT(redrawPoints()));
	connect(ui.lineRadioButton, SIGNAL(clicked()), this, SLOT(redrawPoints()));
}

PickPointsDialog::~PickPointsDialog()
{
	delete getClosestFace;
}

void PickPointsDialog::addMoveSelectPoint(Point3m point, CMeshO::FaceType::NormalType faceNormal)
{
	if (currentMode == ADD_POINT)
	{
		QTreeWidgetItem *item = 0;
		item = ui.pickedPointsTreeWidget->currentItem();

		PickedPointTreeWidgetItem *treeItem = 0;
		if (NULL != item)
		{
			treeItem = dynamic_cast<PickedPointTreeWidgetItem *>(item);
		}

		//if we are in template mode or if the highlighted point is not set
		if ((templateLoaded && NULL != treeItem) || (NULL != treeItem && !treeItem->isActive()))
		{
			treeItem->setPointAndNormal(point, faceNormal);
			treeItem->setActive(true);

			item = ui.pickedPointsTreeWidget->itemBelow(treeItem);
			if (NULL != item) {
				//set the next item to be selected
				ui.pickedPointsTreeWidget->setCurrentItem(item);
			}
			else
			{
				//if we just picked the last point go into move mode
				toggleMoveMode(true);
			}
		}
		else
		{
			//use a number as the default name
			QString name;
			name.setNum(pointCounter);
			pointCounter++;

			addTreeWidgetItemForPoint(point, name, faceNormal, true);
		}
	}

	if (currentMode == MOVE_POINT)
	{
		//test to see if there is actually a highlighted item
		if (NULL != itemToMove) {
			//for undo
			if (recordPointForUndo)
			{
				lastPointToMove = itemToMove;
				lastPointPosition = lastPointToMove->getPoint();
				lastPointNormal = lastPointToMove->getNormal();
				recordPointForUndo = false;
			}

			//now change the point
			itemToMove->setPointAndNormal(point, faceNormal);
			itemToMove->setActive(true);
			ui.pickedPointsTreeWidget->setCurrentItem(itemToMove);
		}
	}

	if (currentMode == SELECT_POINT)
	{
		ui.pickedPointsTreeWidget->setCurrentItem(itemToMove);
	}
}

void PickPointsDialog::recordNextPointForUndo()
{
	recordPointForUndo = true;
}

void PickPointsDialog::selectOrMoveThisPoint(Point3m point) {

    // TBD: move addImageWindow to end of this function
    
	qDebug() << "point is: " << point[0] << " " << point[1] << " " << point[2];

	//the item closest to the given point
	PickedPointTreeWidgetItem *closestItem = 0;

	//the smallest distance from the given point to one in the list
	//so far....
	Scalarm minDistanceSoFar = std::numeric_limits<Scalarm>::max();

	for (int i = 0; i < pickedPointTreeWidgetItemVector.size(); i++) {
		PickedPointTreeWidgetItem *item =
			pickedPointTreeWidgetItemVector.at(i);

		Point3m tempPoint = item->getPoint();

		//qDebug() << "tempPoint is: " << tempPoint[0] << " " << tempPoint[1] << " " << tempPoint[2];

		Scalarm temp = std::sqrt(std::pow(point[0] - tempPoint[0], 2) +
			std::pow(point[1] - tempPoint[1], 2) +
			std::pow(point[2] - tempPoint[2], 2));
		//qDebug() << "distance is: " << temp;

		if ( minDistanceSoFar > temp) {
			minDistanceSoFar = temp;
			closestItem = item;
		}
	}

	//if we found an itme
	if (NULL != closestItem) {
		itemToMove = closestItem;
		//qDebug() << "Try to move: " << closestItem->getName();
	}




#ifdef AVNER_PP
   //avner added - should be done in addPoint??
   meshModel->cm.face.EnableFFAdjacency();
   // vcg::tri::UpdateTopology<CMeshO>::FaceFace(meshModel);
   meshModel->updateDataMask(MeshModel::MM_FACEFACETOPO);
   tri::UpdateTopology<CMeshO>::FaceFaceFromTexCoord(meshModel->cm);
   
	CMeshO::FaceType *face = 0;
	if (NULL != meshModel)
	{
		face = getClosestFace->getFace(point);
		if (NULL == face)
      {
			qDebug() << "no face found for point.";
      }
      else
      {
			qDebug() << "face: " << face;
			qDebug() << "face material index0: " << face->WT(0).n();
			qDebug() << "face material index1: " << face->WT(1).n();
			qDebug() << "face material index2: " << face->WT(2).n();
			// qDebug() << "face->WT(0) u,v: " << face->WT(0).u() << ", " << face->WT(0).v();
			// qDebug() << "face->WT(1) u,v: " << face->WT(1).u() << ", " << face->WT(1).v();
			// qDebug() << "face->WT(2) u,v: " << face->WT(2).u() << ", " << face->WT(2).v();

         ObjTexCoord2 addedPoint_texCoords;
         const int materialIndex = face->WT(0).n();
         qDebug() << "textures2.size(): " << textures2.size();

         if ((0 <= materialIndex) && (materialIndex < textures2.size()))
         {
             std::string textureName = textures2[materialIndex];
             qDebug() << "textureName: " << textureName.c_str();

             calcPointAttributes2(face, materialIndex, point, addedPoint_texCoords);
         }

         qDebug() << "materialIndex: " << materialIndex;
         qDebug() << "addedPoint_texCoords (u,v): " << addedPoint_texCoords.u << ", " << addedPoint_texCoords.v;

         addImageWindow(textures2, materialIndex, addedPoint_texCoords);
         
      }
   }   
#else
#endif
   
}

void PickPointsDialog::redrawPoints()
{
	//parentPlugin->drawPickedPoints(pickedPointTreeWidgetItemVector, meshModel->cm.bbox);
	assert(_glArea);
	_glArea->update();
}

bool PickPointsDialog::showNormal()
{
	return ui.showNormalCheckBox->isChecked();
}

bool PickPointsDialog::drawNormalAsPin()
{
	return ui.pinRadioButton->isChecked();
}

void PickPointsDialog::updateThumbnails(std::list<std::string> filenames, std::list<QPointF>& qPointFs)
{
    qDebug() << "Beg updateThumbnails()";

    {
        std::stringstream ss;
        std::list<std::string>::iterator it; // same as: const int* it
        for (it = filenames.begin(); it != filenames.end(); ++it) ss << ' ' << *it;
        std::cout << "filenames: " << ss.str() << std::endl;
    }

    {
        const char* className0 = parentPlugin->metaObject()->className();
        qDebug("className0: %s", className0);
    }

    foreach (QWidget *widget, QApplication::topLevelWidgets()) {
        const char* className0 = widget->metaObject()->className();
        if(std::string(className0) == std::string("MainWindow"))
        {
            qDebug("className000: %s", className0);

            // https://justcheckingonall.wordpress.com/2013/11/27/get-mainwindow-qt/
            QSplitter *selectedPointViewerSplitter = ((MainWindow*)widget)->m_selectedPointViewerSplitter;
            // QString selectedPointViewerSplitterPtrStr = QString("0x%1").arg((quintptr)selectedPointViewerSplitter, 
            //                                                 QT_POINTER_SIZE * 2, 16, QChar('0'));
            // qDebug() << "selectedPointViewerSplitterPtrStr: " << selectedPointViewerSplitterPtrStr;

            
            int numWidgetsInSplitter = selectedPointViewerSplitter->count();
            // qDebug("numWidgetsInSplitter: %d", numWidgetsInSplitter);

            for (int i = 0; i < numWidgetsInSplitter; i++)
            {
                const char* className0 = selectedPointViewerSplitter->widget(i)->metaObject()->className();
                qDebug("className1111111111: %s", className0);
            }

            QListView* imageList0 = (QListView*)selectedPointViewerSplitter->widget(0);
            std::list<QString> filenames2;
            std::list<QPointF> qPointFs2;
            // for (const std::string &s : filenames, const QPointF &qPointF : qPointFs)
            // {
            //     QString a1 = QString::fromStdString(s);
            //     filenames2.push_back(a1);
            //     // qPointFs2.push_back(QPointF(1,2));
            //     qPointFs2.push_back(qPointF);
            // }

            auto iter = filenames.begin();
            auto iterPointsF = qPointFs.begin();

            // Add sanity check that filenames, qPointFs have the same size
            while (iter != filenames.end())
            {
                QString a1 = QString::fromStdString(*iter);
                filenames2.push_back(a1);
                // qPointFs2.push_back(QPointF(1,2));
                qPointFs2.push_back(*iterPointsF);

                ++iter;
                ++iterPointsF;
            }

            imageList0->setModel(new ImageListModel(filenames2, qPointFs2, imageList0));

            // We connect to the signal emitted when the selection is changed
            // to update the imageViewer.
            ImageViewer *imageViewer0 =  (ImageViewer*)selectedPointViewerSplitter->widget(1);
            QObject::connect(imageList0->selectionModel(), &QItemSelectionModel::selectionChanged, [imageList0, imageViewer0] {
                    QModelIndex selectedIndex = imageList0->selectionModel()->selectedIndexes().first();
                    QString filename = selectedIndex.data(Qt::DisplayRole).value<QString>();
                    qDebug() << "filename: " << filename;

                    QPointF qPointF = selectedIndex.data(ImageListModel::PointRole).value<QPointF>();
                    qDebug() << "qPointF: " << qPointF;

                    
                    imageViewer0->loadFile(filename);
                    int imageWidth;
                    int imageHeight;
                    imageViewer0->drawMetadata(qPointF, imageWidth, imageHeight);
                    
                });
            imageList0->setCurrentIndex(imageList0->model()->index(0, 0));
 
            
        }
    }
}

bool PickPointsDialog::addImageWindow(const std::vector<std::string>& textures2,
                                      const int materialIndex,
                                      const ObjTexCoord2& addedPoint_texCoords)
{
    qDebug() << "Beg PickPointsDialog::addImageWindow()";

    //////////////////////////////////////////////
    // Get imageWidth, imageHeight of the stitched image
    //////////////////////////////////////////////

    std::string textureName = textures2[materialIndex];
    qDebug() << "textureName0: " << textureName.c_str();

    QString imageFileName;
    // imageFileName = QString(textureName.c_str());
    // imageFileName = QString("/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/") + QString(textureName.c_str());
    imageFileName = QString("/home/avner/avner/constructionOverlay/data/3543_W18_shimi/mainHouse/room1/") + QString(textureName.c_str());
    // imageFileName = QString(textureName.c_str());
    
    qDebug() << "imageFileName: " << imageFileName;

    imageviewer2 = new ImageViewer;

    if (imageviewer2->loadFile(imageFileName))
    {
        qDebug() << "Loaded the file: " << imageFileName;
    }
    else
    {
        qDebug() << "Failed to load the file: " << imageFileName;
    }

    // Get imageWidth, imageHeight of the stitched image
    QPointF qPointF(addedPoint_texCoords.u, addedPoint_texCoords.v);
    int imageWidth;
    int imageHeight;
    imageviewer2->drawMetadata(qPointF, imageWidth, imageHeight);

    qDebug() << "imageWidth: " << imageWidth;
    qDebug() << "imageHeight: " << imageHeight;

    // imageviewer2->show();


    ////////////////////////////////////////////
    // Overlay rectangle and dot on the image
    ////////////////////////////////////////////

    // Map qPointF2 from panorama to the images
    std::list<std::string> filenames;
    std::list<QPointF> qPointFs;
    QPointF qPointF2(qPointF.x() * imageWidth, (1.0 - qPointF.y()) * imageHeight);
    if (!mapPointFromPanoramaToImages(materialIndex, qPointF2, filenames, qPointFs))
    {
        std::cerr << "Failed to map point from panorama to images" << std::endl;
        return false;
    }
    // // RemoveME:
    // return true;

    if (filenames.size() > 0)
    {
        updateThumbnails(filenames, qPointFs);
    }

}

void PickPointsDialog::addPoint(Point3m& point, QString& name, bool present)
{
    qDebug() << "Beg PickPointsDialog::addPoint()";

    // TBD: move addImageWindow from here


    
    //bool result = GLPickTri<CMeshO>::PickNearestFace(currentMousePosition.x(),gla->height()-currentMousePosition.y(),
	//	mm.cm, face);

    meshModel->cm.face.EnableFFAdjacency();
    // vcg::tri::UpdateTopology<CMeshO>::FaceFace(meshModel);
    meshModel->updateDataMask(MeshModel::MM_FACEFACETOPO);
    tri::UpdateTopology<CMeshO>::FaceFaceFromTexCoord(meshModel->cm);
    
	CMeshO::FaceType *face = 0;

	qDebug() << "point: " << point[0] << " " << point[1] << " " << point[2];
	qDebug() << "name: " << name;
	qDebug() << "present: " << present;

	//now look for the  normal
	if (NULL != meshModel && present)
	{
		//need to update the mask
		meshModel->updateDataMask(MeshModel::MM_FACEMARK);

		face = getClosestFace->getFace(point);
		if (NULL == face)
      {
			qDebug() << "no face found for point: " << name;
      }
      else
      {
			qDebug() << "face: " << face;
			qDebug() << "face material index0: " << face->WT(0).n();
			qDebug() << "face material index1: " << face->WT(1).n();
			qDebug() << "face material index2: " << face->WT(2).n();
			// qDebug() << "face->WT(0) u,v: " << face->WT(0).u() << ", " << face->WT(0).v();
			// qDebug() << "face->WT(1) u,v: " << face->WT(1).u() << ", " << face->WT(1).v();
			// qDebug() << "face->WT(2) u,v: " << face->WT(2).u() << ", " << face->WT(2).v();

#ifdef AVNER_PP
         ObjTexCoord2 addedPoint_texCoords;
         const int materialIndex = face->WT(0).n();
         qDebug() << "textures2.size(): " << textures2.size();

         if ((0 <= materialIndex) && (materialIndex < textures2.size()))
         {
             std::string textureName = textures2[materialIndex];
             qDebug() << "textureName: " << textureName.c_str();

             calcPointAttributes2(face, materialIndex, point, addedPoint_texCoords);
         }

         qDebug() << "materialIndex: " << materialIndex;
         qDebug() << "addedPoint_texCoords (u,v): " << addedPoint_texCoords.u << ", " << addedPoint_texCoords.v;

         addImageWindow(textures2, materialIndex, addedPoint_texCoords);
#else
#endif
         
      }
	}
	qDebug() << "foo1";

	//if we find a face add its normal. else add a default one
	if (NULL != face)
   {
       qDebug() << "foo2";
       addTreeWidgetItemForPoint(point, name, face->N(), present);
   }
	else
	{
       qDebug() << "foo3";
       Point3m faceNormal;
       addTreeWidgetItemForPoint(point, name, faceNormal, present);
	}
}

PickedPointTreeWidgetItem * PickPointsDialog::addTreeWidgetItemForPoint(Point3m &point, QString &name, CMeshO::FaceType::NormalType &faceNormal, bool present)
{
	PickedPointTreeWidgetItem *widgetItem =
		new PickedPointTreeWidgetItem(point, faceNormal, name, present);

	pickedPointTreeWidgetItemVector.push_back(widgetItem);

	ui.pickedPointsTreeWidget->addTopLevelItem(widgetItem);
	//select the newest item
	ui.pickedPointsTreeWidget->setCurrentItem(widgetItem);

	//add a checkbox to the widget item's 5th column (QT makes us add it in this strange way)
	TreeCheckBox *checkBox = new TreeCheckBox(ui.pickedPointsTreeWidget, widgetItem, this);
	ui.pickedPointsTreeWidget->setItemWidget(widgetItem, 4, checkBox);

	//set the box to show the proper check
	checkBox->setChecked(present);

	//now connect the box to its slot that chanches the checked value of the 
	//PickedPointTreeWidgetItem and draws all the points.  dont do this before
	//set checked or you will have all points that should be drawn, not drawn
	connect(checkBox, SIGNAL(toggled(bool)), checkBox, SLOT(toggleAndDraw(bool)));

	return widgetItem;
}

void PickPointsDialog::clearPoints(bool clearOnlyXYZ) {
	if (clearOnlyXYZ) {
		//when using templates just clear the points that were picked but not the names
		for (int i = 0; i < pickedPointTreeWidgetItemVector.size(); i++) {
			pickedPointTreeWidgetItemVector.at(i)->clearPoint();
		}
		//if the size is greater than 0 set the first point to be selected
		if (pickedPointTreeWidgetItemVector.size() > 0) {
			ui.pickedPointsTreeWidget->setCurrentItem(
				pickedPointTreeWidgetItemVector.at(0));
		}
	}
	else {
		pickedPointTreeWidgetItemVector.clear();
		ui.pickedPointsTreeWidget->clear();
		pointCounter = 0;
	}

	//draw without any points that may have been cleared
  //parentPlugin->drawPickedPoints(pickedPointTreeWidgetItemVector, meshModel->cm.bbox,painter);
	assert(_glArea);
	_glArea->update();

	//set to pick mode
	togglePickMode(true);
}

void PickPointsDialog::clearTemplate()
{
	//always clear the points
	clearPoints(false);

	setTemplateName("");
}

void PickPointsDialog::setTemplateName(QString name)
{
	templateName = name;
	if ("" == templateName)
	{
		ui.templateNameLabel->setText("No Template Loaded");
		templateLoaded = false;
	}
	else
	{
		ui.templateNameLabel->setText(templateName);
		templateLoaded = true;
	}
}

void PickPointsDialog::loadPickPointsTemplate(QString filename)
{
	//clear the points tree
	clearPoints(false);

	std::vector<QString> pointNameVector;

	PickPointsTemplate::load(filename, &pointNameVector);

	for (int i = 0; i < pointNameVector.size(); i++) {
		Point3m point;
		Point3m faceNormal;
		PickedPointTreeWidgetItem *widgetItem =
			addTreeWidgetItemForPoint(point, pointNameVector.at(i), faceNormal, false);
		widgetItem->clearPoint();

	}

	//select the first item in the list if it exists
	if (pickedPointTreeWidgetItemVector.size() > 0) {
		ui.pickedPointsTreeWidget->setCurrentItem(pickedPointTreeWidgetItemVector.at(0));
	}

	setTemplateName(QFileInfo(filename).fileName());
	templateWorkingDirectory = filename;
}

std::vector<PickedPointTreeWidgetItem*>& PickPointsDialog::getPickedPointTreeWidgetItemVector() {
	return pickedPointTreeWidgetItemVector;
}

PickPointsDialog::Mode PickPointsDialog::getMode() {
	return currentMode;
}

void PickPointsDialog::setCurrentMeshModel(MeshModel *newMeshModel, QGLWidget *gla) {
	meshModel = newMeshModel;
	assert(meshModel);
	_glArea = gla;
	assert(_glArea);

	//make sure undo is cleared
	lastPointToMove = 0;

	//clear any points that are still here
	clearPoints(false);

	//also clear the template
	clearTemplate();

	//make sure we start in pick mode
	togglePickMode(true);

	meshModel->updateDataMask(MeshModel::MM_FACEMARK);
	//set up the 
	getClosestFace->init(&(meshModel->cm));

   textures2 = meshModel->cm.textures;
       
	//Load the points from meta data if they are there
	if (vcg::tri::HasPerMeshAttribute(newMeshModel->cm, PickedPoints::Key))
	{
		CMeshO::PerMeshAttributeHandle<PickedPoints*> ppHandle =
			vcg::tri::Allocator<CMeshO>::GetPerMeshAttribute<PickedPoints*>(newMeshModel->cm, PickedPoints::Key);

		PickedPoints *pickedPoints = ppHandle();

		if (NULL != pickedPoints) {

			const QString &name = pickedPoints->getTemplateName();
			setTemplateName(name);

			std::vector<PickedPoint*>& pickedPointVector = pickedPoints->getPickedPointVector();

			PickedPoint *point;
			for (size_t i = 0; i < pickedPointVector.size(); i++) {
				point = pickedPointVector.at(i);

				addPoint(point->point, point->name, point->present);
			}

			redrawPoints();
		}
		else {
			qDebug() << "problem with cast!!";
		}

	}
	else {

		QString filename = PickedPoints::getSuggestedPickedPointsFileName(*meshModel);

		qDebug() << "suggested filename: " << filename;

		QFile file(filename);

		if (file.exists()) {
			loadPoints(filename);

		}
		else
		{

			//try loading the default template if there are not saved points already
			tryLoadingDefaultTemplate();

		}
	}
}

//loads the default template if there is one
void PickPointsDialog::tryLoadingDefaultTemplate()
{
	QString filename = PickPointsTemplate::getDefaultTemplateFileName();
	QFile file(filename);

	if (file.exists()) {
		loadPickPointsTemplate(filename);
	}

	//clear all the garbage out of the names
	clearPoints(true);
}

void PickPointsDialog::removeHighlightedPoint() {
	//get highlighted point
	QTreeWidgetItem *item = ui.pickedPointsTreeWidget->currentItem();

	//test to see if there is actually a highlighted item
	if (NULL != item) {
		PickedPointTreeWidgetItem* pickedItem =
			dynamic_cast<PickedPointTreeWidgetItem *>(item);


		//remove the point completely
		std::vector<PickedPointTreeWidgetItem*>::iterator iterator;
		iterator = std::find(pickedPointTreeWidgetItemVector.begin(),
			pickedPointTreeWidgetItemVector.end(),
			pickedItem);
		//remove item from vector
		pickedPointTreeWidgetItemVector.erase(iterator);

		//free memory used by widget
		delete pickedItem;

		//redraw without deleted point
		redrawPoints();
	}
	else
	{
		qDebug("no item picked");
	}
}

void PickPointsDialog::renameHighlightedPoint() {
	//get highlighted point
	QTreeWidgetItem *item = ui.pickedPointsTreeWidget->currentItem();

	//test to see if there is actually a highlighted item
	if (NULL != item) {
		PickedPointTreeWidgetItem* pickedItem =
			dynamic_cast<PickedPointTreeWidgetItem *>(item);

		QString name = pickedItem->getName();
		//qDebug("Rename \n");
		//qDebug() << name;

		const QString newName = "newName";

		RichParameterSet parameterSet;
		parameterSet.addParam(new RichString(newName, name, "New Name", "Enter the new name"));

		GenericParamDialog getNameDialog(this, &parameterSet);
		getNameDialog.setWindowModality(Qt::WindowModal);
		getNameDialog.hide();

		//display dialog
		int result = getNameDialog.exec();
		if (result == QDialog::Accepted) {
			name = parameterSet.getString(newName);
			//qDebug("New name os \n");
			//qDebug() << name;

			pickedItem->setName(name);

			//redraw with new point name
			redrawPoints();
		}
	}
}

void PickPointsDialog::clearHighlightedPoint()
{
	//get highlighted point
	QTreeWidgetItem *item = ui.pickedPointsTreeWidget->currentItem();

	//test to see if there is actually a highlighted item
	if (NULL != item) {
		PickedPointTreeWidgetItem* pickedItem =
			dynamic_cast<PickedPointTreeWidgetItem *>(item);

		pickedItem->clearPoint();

		//redraw without deleted point
		redrawPoints();
	}
	else
	{
		qDebug("no item picked");
	}
}

void PickPointsDialog::togglePickMode(bool checked) {
	if (checked) {
		QApplication::setOverrideCursor(QCursor(Qt::ArrowCursor));

		//qDebug() << "pick mode";
		currentMode = ADD_POINT;
		//make sure radio button reflects this change
		ui.pickPointModeRadioButton->setChecked(true);
	}
}

void PickPointsDialog::toggleMoveMode(bool checked)
{
	if (checked)
	{
		QApplication::setOverrideCursor(QCursor(Qt::ClosedHandCursor));

		//qDebug() << "move mode";
		currentMode = MOVE_POINT;
		//make sure the radio button reflects this change
		ui.movePointRadioButton->setChecked(true);
	}
}

void PickPointsDialog::toggleSelectMode(bool checked)
{
	if (checked)
	{
		QApplication::setOverrideCursor(QCursor(Qt::PointingHandCursor));

		//qDebug() << "select mode";
		currentMode = SELECT_POINT;
		//make radio button reflect the change
		ui.selectPointRadioButton->setChecked(true);
	}
}

PickedPoints * PickPointsDialog::getPickedPoints()
{
	PickedPoints *pickedPoints = new PickedPoints();
	//add all the points
	for (int i = 0; i < pickedPointTreeWidgetItemVector.size(); i++) {
		PickedPointTreeWidgetItem *item =
			pickedPointTreeWidgetItemVector.at(i);
		pickedPoints->addPoint(item->getName(), item->getPoint(), item->isActive());
	}

	pickedPoints->setTemplateName(templateName);

	return pickedPoints;
}

void PickPointsDialog::loadPoints(QString filename) {
	//clear the points tree and template in case it was loaded
	clearTemplate();

	//get the points from file
	PickedPoints pickedPoints;
	pickedPoints.open(filename);

	const QString &name = pickedPoints.getTemplateName();
	setTemplateName(name);

	std::vector<PickedPoint*>& points = pickedPoints.getPickedPointVector();

	for (size_t i = 0; i < points.size(); i++) {
		PickedPoint *pickedPoint = points.at(i);

		addPoint(pickedPoint->point, pickedPoint->name, pickedPoint->present);
	}

	//redraw with new point name
	redrawPoints();
}

void PickPointsDialog::savePointsToFile()
{

	PickedPoints *pickedPoints = getPickedPoints();

	//save to a file if so desired and there are some points to save
	if (pickedPointTreeWidgetItemVector.size() > 0) {

		QString suggestion(".");
		if (NULL != meshModel) {
			suggestion = PickedPoints::getSuggestedPickedPointsFileName(*meshModel);
		}
		QString filename = QFileDialog::getSaveFileName(this, tr("Save File"), suggestion, "*" + PickedPoints::fileExtension);

		if ("" != filename)
		{
			pickedPoints->save(filename, QString(meshModel->shortName()));
			savePointsToMetaData();
		}
	}
}

void PickPointsDialog::savePointsToMetaData()
{
	//save the points to the metadata
	if (NULL != meshModel) {
		CMeshO::PerMeshAttributeHandle<PickedPoints*> ppHandle = vcg::tri::Allocator<CMeshO>::GetPerMeshAttribute<PickedPoints*>(meshModel->cm, PickedPoints::Key);
		ppHandle() = getPickedPoints();

		//qDebug() << "saved points";
	}
}

void PickPointsDialog::askUserForFileAndLoadPoints()
{
	QString suggestion(".");
	if (NULL != meshModel)
		suggestion = PickedPoints::getSuggestedPickedPointsFileName(*meshModel);

	QString filename = QFileDialog::getOpenFileName(this, tr("Load File"), suggestion, "*" + PickedPoints::fileExtension);

	if ("" != filename)	loadPoints(filename);
}

void PickPointsDialog::savePointTemplate() {
	std::vector<QString> pointNameVector;

	//add all the points
	for (int i = 0; i < pickedPointTreeWidgetItemVector.size(); i++) {
		PickedPointTreeWidgetItem *item =
			pickedPointTreeWidgetItemVector.at(i);

		pointNameVector.push_back(item->getName());
	}

	//default if for the filename to be that of the default template
	QString filename = PickPointsTemplate::getDefaultTemplateFileName();

	if (!ui.defaultTemplateCheckBox->isChecked())
	{
		filename = QFileDialog::getSaveFileName(this, tr("Save File"), templateWorkingDirectory, "*" + PickPointsTemplate::fileExtension);

		//if the user pushes cancel dont do anything
		if ("" == filename) return;
		else templateWorkingDirectory = filename;
	}


	//add the extension if the user forgot it
	if (!filename.endsWith(PickPointsTemplate::fileExtension))
		filename = filename + PickPointsTemplate::fileExtension;

	PickPointsTemplate::save(filename, &pointNameVector);
	setTemplateName(QFileInfo(filename).fileName());

	if (ui.defaultTemplateCheckBox->isChecked())
	{
		QMessageBox::information(this, "MeshLab", "Default Template Saved!",
			QMessageBox::Ok);
	}
}

void PickPointsDialog::askUserForFileAndloadTemplate()
{
	QString filename = QFileDialog::getOpenFileName(this, tr("Load File"), templateWorkingDirectory, "*" + PickPointsTemplate::fileExtension);
	if ("" != filename) loadPickPointsTemplate(filename);
}

void PickPointsDialog::clearPointsButtonClicked()
{

	QMessageBox messageBox(QMessageBox::Question, "Pick Points", "Are you sure you want to clear all points?",
		QMessageBox::Yes | QMessageBox::No, this);
	int returnValue = messageBox.exec();

	if (returnValue == QMessageBox::Yes)
	{
		//if the template is loaded clear only xyz values
		clearPoints(templateLoaded);
	}
}

void PickPointsDialog::clearTemplateButtonClicked() {

	QMessageBox messageBox(QMessageBox::Question, "Pick Points", "Are you sure you want to clear the template and any picked points?",
		QMessageBox::Yes | QMessageBox::No, this);
	int returnValue = messageBox.exec();

	if (returnValue == QMessageBox::Yes)
	{
		clearTemplate();
	}
}

void PickPointsDialog::addPointToTemplate()
{
	//
	if (!templateLoaded)
		setTemplateName("new Template");

	Point3m point;
	Point3m faceNormal;
	QString name("new point");
	PickedPointTreeWidgetItem *widgetItem =
		addTreeWidgetItemForPoint(point, name, faceNormal, false);
	widgetItem->clearPoint();

}

void PickPointsDialog::undo()
{
	if (NULL != lastPointToMove)
	{
		Point3m tempPoint = lastPointToMove->getPoint();
		Point3m tempNormal = lastPointToMove->getNormal();

		lastPointToMove->setPointAndNormal(lastPointPosition, lastPointNormal);

		//set things so you can undo back if need be
		lastPointPosition = tempPoint;
		lastPointNormal = tempNormal;

		redrawPoints();
	}
}
