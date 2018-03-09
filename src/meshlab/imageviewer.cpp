/****************************************************************************
**
** Copyright (C) 2016 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the examples of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:BSD$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** BSD License Usage
** Alternatively, you may use this file under the terms of the BSD license
** as follows:
**
** "Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**   * Redistributions of source code must retain the above copyright
**     notice, this list of conditions and the following disclaimer.
**   * Redistributions in binary form must reproduce the above copyright
**     notice, this list of conditions and the following disclaimer in
**     the documentation and/or other materials provided with the
**     distribution.
**   * Neither the name of The Qt Company Ltd nor the names of its
**     contributors may be used to endorse or promote products derived
**     from this software without specific prior written permission.
**
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
** "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
** LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
** A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
** OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
** SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
** LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
** DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
** THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
** OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
**
** $QT_END_LICENSE$
**
****************************************************************************/

#include <QtWidgets>
#ifndef QT_NO_PRINTER
#include <QPrintDialog>
#endif

#include "imageviewer.h"

//! [0]

#include <iostream>
#include <fstream>


#define ADD_HUGIN
#ifdef ADD_HUGIN
#include <panodata/Panorama.h>
#include <panotools/PanoToolsInterface.h>
#else
#endif
 


ImageViewer::ImageViewer()
   : imageLabel(new QLabel)
   , scrollArea(new QScrollArea)
   , scaleFactor(1)
{
    imageLabel->setBackgroundRole(QPalette::Base);
    imageLabel->setSizePolicy(QSizePolicy::Ignored, QSizePolicy::Ignored);
    imageLabel->setScaledContents(true);

    scrollArea->setBackgroundRole(QPalette::Dark);
    scrollArea->setWidget(imageLabel);
    scrollArea->setVisible(false);
    setCentralWidget(scrollArea);

    createActions();

    resize(QGuiApplication::primaryScreen()->availableSize() * 3 / 5);
}

//! [0]
//! [2]

bool ImageViewer::loadFile(const QString &fileName)
{
    QImageReader reader(fileName);
    reader.setAutoTransform(true);
    const QImage newImage = reader.read();
    if (newImage.isNull()) {
        QMessageBox::information(this, QGuiApplication::applicationDisplayName(),
                                 tr("Cannot load %1: %2")
                                 .arg(QDir::toNativeSeparators(fileName), reader.errorString()));
        return false;
    }
//! [2]

    setImage(newImage);

    setWindowFilePath(fileName);

    const QString message = tr("Opened \"%1\", %2x%3, Depth: %4")
        .arg(QDir::toNativeSeparators(fileName)).arg(image.width()).arg(image.height()).arg(image.depth());
    statusBar()->showMessage(message);

#ifdef AVNER_ADD_IMAGE_WINDOW2

    ////////////////////////////////////////////
    // Overlay rectangle and dot on the image
    ////////////////////////////////////////////

    // drawMetadata();
    
    ////////////////////////////////////////////
    // show the entire image
    ////////////////////////////////////////////

    // scaleImage(0.5);
    // scaleImage(0.03);
#else
#endif
    
    return true;
}




bool ImageViewer::drawMetadata(const QPointF& qPointF, int& imageWidth, int& imageHeight)
{
    QPainter painter(&image);
    QPen pen;

    // imageLabel->pixmap()
    //     QSize size = imageLabel->pixmap()->size();
    //     size.scale(rect.size(), Qt::KeepAspectRatio);
    //     painter.setViewport(rect.x(), rect.y(), size.width(), size.height());
    qDebug() << "qPointF: " << qPointF;
    imageHeight = imageLabel->pixmap()->size().height();
    imageWidth = imageLabel->pixmap()->size().width();

    qDebug() << "image height: " << imageHeight;
    qDebug() << "image width: " << imageWidth;
    
    QPointF qPointF2(qPointF.x(), qPointF.y());
    qDebug() << "qPointF2: " << qPointF2;

    QPointF qPointF2_yFlipped(qPointF.x(), imageHeight - qPointF.y());
    qDebug() << "qPointF2_yFlipped: " << qPointF2_yFlipped;
        
    // Draw blue dot
    pen.setWidth(20);
    pen.setColor(Qt::red);
    painter.setPen(pen);
    painter.drawPoint(35,25);

    // Draw red rectangle
    // qreal rectWidth = 80.0;
    // qreal rectHeight = 60.0;
    // qreal x0 = 10.0;
    // qreal y0 = 20.0;

    qreal rectWidth = 20.0;
    qreal rectHeight = 20.0;
    qreal x0 = qPointF2_yFlipped.x() - (rectWidth/2);
    // flip y
    qreal y0_flipped = imageHeight - (qPointF2_yFlipped.y() - (rectHeight/2));

    QRectF rectangle(x0, y0_flipped, rectWidth, rectHeight);
    
    // pen.setWidth(5);
    pen.setWidth(50);
    pen.setColor(Qt::blue);
    painter.setPen(pen);
    painter.drawRect(rectangle);

    painter.end();

    
    painter.drawPixmap(0, 0, *imageLabel->pixmap());

    imageLabel->setPixmap(QPixmap::fromImage(image));

    return true;
}


void ImageViewer::setImage(const QImage &newImage)
{
    qDebug() << "BEG ImageViewer::setImage";
    
    image = newImage;
    imageLabel->setPixmap(QPixmap::fromImage(image));
//! [4]
    scaleFactor = 1.0;

    scrollArea->setVisible(true);
#if defined(QT_PRINTSUPPORT_LIB)
    printAct->setEnabled(true);
#endif
    fitToWindowAct->setEnabled(true);
    fitToWindowAct->setChecked(true);
    preserveAspectRatioAct->setEnabled(true);
    preserveAspectRatioAct->setChecked(true);
    updateActions();

    if (!fitToWindowAct->isChecked())
    {
        imageLabel->adjustSize();
    }
    else
    {
        fitToWindow();
    }

    // scaleImage();
}

//! [4]

bool ImageViewer::saveFile(const QString &fileName)
{
    QImageWriter writer(fileName);

    if (!writer.write(image)) {
        QMessageBox::information(this, QGuiApplication::applicationDisplayName(),
                                 tr("Cannot write %1: %2")
                                 .arg(QDir::toNativeSeparators(fileName)), writer.errorString());
        return false;
    }
    const QString message = tr("Wrote \"%1\"").arg(QDir::toNativeSeparators(fileName));
    statusBar()->showMessage(message);
    return true;
}

//! [1]

static void initializeImageFileDialog(QFileDialog &dialog, QFileDialog::AcceptMode acceptMode)
{
    static bool firstDialog = true;

    if (firstDialog) {
        firstDialog = false;
        const QStringList picturesLocations = QStandardPaths::standardLocations(QStandardPaths::PicturesLocation);
        dialog.setDirectory(picturesLocations.isEmpty() ? QDir::currentPath() : picturesLocations.last());
    }

    QStringList mimeTypeFilters;
    const QByteArrayList supportedMimeTypes = acceptMode == QFileDialog::AcceptOpen
        ? QImageReader::supportedMimeTypes() : QImageWriter::supportedMimeTypes();
    foreach (const QByteArray &mimeTypeName, supportedMimeTypes)
        mimeTypeFilters.append(mimeTypeName);
    mimeTypeFilters.sort();
    dialog.setMimeTypeFilters(mimeTypeFilters);
    dialog.selectMimeTypeFilter("image/jpeg");
    if (acceptMode == QFileDialog::AcceptSave)
        dialog.setDefaultSuffix("jpg");
}

void ImageViewer::open()
{
    QFileDialog dialog(this, tr("Open File"));
    initializeImageFileDialog(dialog, QFileDialog::AcceptOpen);

    while (dialog.exec() == QDialog::Accepted && !loadFile(dialog.selectedFiles().first())) {}
}
//! [1]

void ImageViewer::saveAs()
{
    QFileDialog dialog(this, tr("Save File As"));
    initializeImageFileDialog(dialog, QFileDialog::AcceptSave);

    while (dialog.exec() == QDialog::Accepted && !saveFile(dialog.selectedFiles().first())) {}
}

//! [5]
#if defined(QT_PRINTSUPPORT_LIB)
void ImageViewer::print()
//! [5] //! [6]
{
    Q_ASSERT(imageLabel->pixmap());
#if !defined(QT_NO_PRINTER) && !defined(QT_NO_PRINTDIALOG)
//! [6] //! [7]
    QPrintDialog dialog(&printer, this);
//! [7] //! [8]
    if (dialog.exec()) {
        QPainter painter(&printer);
        QRect rect = painter.viewport();
        QSize size = imageLabel->pixmap()->size();
        size.scale(rect.size(), Qt::KeepAspectRatio);
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height());
        painter.setWindow(imageLabel->pixmap()->rect());
        painter.drawPixmap(0, 0, *imageLabel->pixmap());
    }
#endif
}
//! [8]
#endif

void ImageViewer::copy()
{
#ifndef QT_NO_CLIPBOARD
    QGuiApplication::clipboard()->setImage(image);
#endif // !QT_NO_CLIPBOARD
}

#ifndef QT_NO_CLIPBOARD
static QImage clipboardImage()
{
    if (const QMimeData *mimeData = QGuiApplication::clipboard()->mimeData()) {
        if (mimeData->hasImage()) {
            const QImage image = qvariant_cast<QImage>(mimeData->imageData());
            if (!image.isNull())
                return image;
        }
    }
    return QImage();
}
#endif // !QT_NO_CLIPBOARD

void ImageViewer::paste()
{
#ifndef QT_NO_CLIPBOARD
    const QImage newImage = clipboardImage();
    if (newImage.isNull()) {
        statusBar()->showMessage(tr("No image in clipboard"));
    } else {
        setImage(newImage);
        setWindowFilePath(QString());
        const QString message = tr("Obtained image from clipboard, %1x%2, Depth: %3")
            .arg(newImage.width()).arg(newImage.height()).arg(newImage.depth());
        statusBar()->showMessage(message);
    }
#endif // !QT_NO_CLIPBOARD
}

//! [9]
void ImageViewer::zoomIn()
//! [9] //! [10]
{
    scaleImage(1.25);
}

void ImageViewer::zoomOut()
{
    scaleImage(0.8);
}

//! [10] //! [11]
void ImageViewer::normalSize()
//! [11] //! [12]
{
    imageLabel->adjustSize();
    scaleFactor = 1.0;
}
//! [12]

void ImageViewer::preserveAspectRatio()
{
   bool preserveAspectRatio = preserveAspectRatioAct->isChecked();
}

void ImageViewer::resizeEvent(QResizeEvent* event)
{
    qDebug() << "BEG ImageViewer::resizeEvent";
   QMainWindow::resizeEvent(event);
   fitToWindow();
   // Your code here.
}

//! [13]
void ImageViewer::fitToWindow()
//! [13] //! [14]
{
    // qDebug() << "BEG ImageViewer::fitToWindow";
    bool fitToWindow = fitToWindowAct->isChecked();
    qDebug() << "fitToWindow: " << fitToWindow;
    
    bool preserveAspectRatio = preserveAspectRatioAct->isChecked();

        // 4032 / 3024 = 1.33333333333
        int imageWidth1 = imageLabel->width();
        int imageHeight1 = imageLabel->height();
        float imageAspectRatio1 = (float)imageWidth1 / imageHeight1;
        qDebug() << "imageWidth1: " << imageWidth1;
        qDebug() << "imageHeight1: " << imageHeight1;
        qDebug() << "imageAspectRatio1: " << imageAspectRatio1;

        const QPixmap* qPixmap = imageLabel->pixmap();
        qDebug() << "qPixmap: " << qPixmap;
        if(!qPixmap)
        {
            return;
        }
            
        int imageHeight2 = imageLabel->pixmap()->size().height();
        int imageWidth2 = imageLabel->pixmap()->size().width();
        float imageAspectRatio2 = (float)imageWidth2 / imageHeight2;
        qDebug() << "imageHeight2: " << imageHeight2;
        qDebug() << "imageWidth2: " << imageWidth2;
        qDebug() << "imageAspectRatio2: " << imageAspectRatio2;

        int imageViewerWidth = this->width();
        int imageViewerHeight = this->height();
        float imageViewerAspectRatio = (float)imageViewerWidth / imageViewerHeight;
        qDebug() << "imageViewerWidth: " << imageViewerWidth;
        qDebug() << "imageViewerHeight: " << imageViewerHeight;
        qDebug() << "imageViewerAspectRatio: " << imageViewerAspectRatio;

    if(preserveAspectRatio)
    {

        int imageWidthNew;
        int imageHeightNew;
        if(imageViewerAspectRatio > imageAspectRatio2)
        {
            imageHeightNew = imageViewerHeight;
            imageWidthNew = imageHeightNew * imageAspectRatio2;
        }
        else
        {
            imageWidthNew = imageViewerWidth;
            imageHeightNew = imageWidthNew / imageAspectRatio2;
        }
        
        // scrollArea->resize(imageWidthNew, imageHeightNew);
        imageLabel->resize(imageWidthNew, imageHeightNew);
    }
    else
    {
        scrollArea->setWidgetResizable(fitToWindow);
    }

    
    if (!fitToWindow)
    {
        normalSize();
    }
    
    updateActions();
}
//! [14]


//! [15]
void ImageViewer::about()
//! [15] //! [16]
{
    QMessageBox::about(this, tr("About Image Viewer"),
            tr("<p>The <b>Image Viewer</b> example shows how to combine QLabel "
               "and QScrollArea to display an image. QLabel is typically used "
               "for displaying a text, but it can also display an image. "
               "QScrollArea provides a scrolling view around another widget. "
               "If the child widget exceeds the size of the frame, QScrollArea "
               "automatically provides scroll bars. </p><p>The example "
               "demonstrates how QLabel's ability to scale its contents "
               "(QLabel::scaledContents), and QScrollArea's ability to "
               "automatically resize its contents "
               "(QScrollArea::widgetResizable), can be used to implement "
               "zooming and scaling features. </p><p>In addition the example "
               "shows how to use QPainter to print an image.</p>"));
}
//! [16]

//! [17]
void ImageViewer::createActions()
//! [17] //! [18]
{
    QMenu *fileMenu = menuBar()->addMenu(tr("&File"));

    QAction *openAct = fileMenu->addAction(tr("&Open..."), this, &ImageViewer::open);
    openAct->setShortcut(QKeySequence::Open);

    saveAsAct = fileMenu->addAction(tr("&Save As..."), this, &ImageViewer::saveAs);
    saveAsAct->setEnabled(false);

#if defined(QT_PRINTSUPPORT_LIB)
    printAct = fileMenu->addAction(tr("&Print..."), this, &ImageViewer::print);
    printAct->setShortcut(QKeySequence::Print);
    printAct->setEnabled(false);
#endif

    fileMenu->addSeparator();

    QAction *exitAct = fileMenu->addAction(tr("E&xit"), this, &QWidget::close);
    exitAct->setShortcut(tr("Ctrl+Q"));

    QMenu *editMenu = menuBar()->addMenu(tr("&Edit"));

    copyAct = editMenu->addAction(tr("&Copy"), this, &ImageViewer::copy);
    copyAct->setShortcut(QKeySequence::Copy);
    copyAct->setEnabled(false);

    QAction *pasteAct = editMenu->addAction(tr("&Paste"), this, &ImageViewer::paste);
    pasteAct->setShortcut(QKeySequence::Paste);

    QMenu *viewMenu = menuBar()->addMenu(tr("&View"));

    zoomInAct = viewMenu->addAction(tr("Zoom &In (25%)"), this, &ImageViewer::zoomIn);
    zoomInAct->setShortcut(QKeySequence::ZoomIn);
    zoomInAct->setEnabled(false);

    zoomOutAct = viewMenu->addAction(tr("Zoom &Out (25%)"), this, &ImageViewer::zoomOut);
    zoomOutAct->setShortcut(QKeySequence::ZoomOut);
    zoomOutAct->setEnabled(false);

    normalSizeAct = viewMenu->addAction(tr("&Normal Size"), this, &ImageViewer::normalSize);
    normalSizeAct->setShortcut(tr("Ctrl+S"));
    normalSizeAct->setEnabled(false);

    viewMenu->addSeparator();

    preserveAspectRatioAct = viewMenu->addAction(tr("&Preserve aspect ratio"), this, &ImageViewer::preserveAspectRatio);
    preserveAspectRatioAct->setEnabled(true);
    preserveAspectRatioAct->setCheckable(true);
    
    fitToWindowAct = viewMenu->addAction(tr("&Fit to Window"), this, &ImageViewer::fitToWindow);
    // fitToWindowAct->setEnabled(false);
    fitToWindowAct->setEnabled(true);
    fitToWindowAct->setCheckable(true);
    fitToWindowAct->setShortcut(tr("Ctrl+F"));

    QMenu *helpMenu = menuBar()->addMenu(tr("&Help"));

    helpMenu->addAction(tr("&About"), this, &ImageViewer::about);
    helpMenu->addAction(tr("About &Qt"), &QApplication::aboutQt);
}
//! [18]

//! [21]
void ImageViewer::updateActions()
//! [21] //! [22]
{
    // qDebug() << "BEG ImageViewer::updateActions";
    
    saveAsAct->setEnabled(!image.isNull());
    copyAct->setEnabled(!image.isNull());
    zoomInAct->setEnabled(!fitToWindowAct->isChecked());
    zoomOutAct->setEnabled(!fitToWindowAct->isChecked());
    normalSizeAct->setEnabled(!fitToWindowAct->isChecked());
}
//! [22]

//! [23]
void ImageViewer::scaleImage(double factor)
//! [23] //! [24]
{
    // qDebug() << "BEG ImageViewer::scaleImage";
    Q_ASSERT(imageLabel->pixmap());
    scaleFactor *= factor;
    imageLabel->resize(scaleFactor * imageLabel->pixmap()->size());
    qDebug() << "scaleFactor: " << scaleFactor;
    qDebug() << "imageLabel->pixmap()->size(): " << imageLabel->pixmap()->size();

    adjustScrollBar(scrollArea->horizontalScrollBar(), factor);
    adjustScrollBar(scrollArea->verticalScrollBar(), factor);

    zoomInAct->setEnabled(scaleFactor < 3.0);

    
    // zoomOutAct->setEnabled(scaleFactor > 0.333);
    zoomOutAct->setEnabled(scaleFactor > 0.033);
}
//! [24]

//! [25]
void ImageViewer::adjustScrollBar(QScrollBar *scrollBar, double factor)
//! [25] //! [26]
{
    // qDebug() << "BEG ImageViewer::adjustScrollBar";
    scrollBar->setValue(int(factor * scrollBar->value()
                            + ((factor - 1) * scrollBar->pageStep()/2)));
}
//! [26]
