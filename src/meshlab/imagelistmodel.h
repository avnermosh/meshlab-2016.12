///////////////////////  
// imagelistmodel.h ///  
#ifndef IMAGELISTMODEL_H  
#define IMAGELISTMODEL_H  

#include <QAbstractListModel>
#include <QPixmap>
#include <QPointF>


struct PixmapPair
{
    QString _file;
    QPointF _qPointF;
    QPixmap _small;
    QPixmap _large;
};

class ImageListModel : public QAbstractListModel
{
        Q_OBJECT
    public:
        // QAbstractItemModel retrieve different information (like text, color, ...)
        // from same index using roles. We can define custom ones, however to avoid  
        // clash with predefined roles, ours must start at Qt::UserRole. 
        // All number below this one are reserved for qt internals.
        enum Roles
        {
         LargePixmapRole = Qt::UserRole + 1,
         PointRole = Qt::UserRole + 2
        };

        explicit ImageListModel(std::list<QString> files,
                                std::list<QPointF> qPointFs,
                                QObject *parent = 0);
        virtual ~ImageListModel();

        // QAbstractItemModel interface ===========================
    public:
        int rowCount(const QModelIndex &parent) const;
        QVariant data(const QModelIndex &index, int role) const;
        // ========================================================

    private:
        QList<PixmapPair*> _data;
};

#endif // IMAGELISTMODEL_H
