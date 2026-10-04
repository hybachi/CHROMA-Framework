#pragma once

#include <QScrollArea>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>

namespace chroma_rviz_plugins::common
{
    inline QVBoxLayout* makeScrollableCardLayout(QWidget* parent_widget, QVBoxLayout* parent_layout)
    {
        QScrollArea* scroll_area = new QScrollArea(parent_widget);
        scroll_area->setWidgetResizable(true);
        scroll_area->setFrameShape(QFrame::NoFrame);

        QWidget* scroll_content = new QWidget();
        QVBoxLayout* scroll_layout = new QVBoxLayout(scroll_content);
        scroll_layout->setAlignment(Qt::AlignTop);
        scroll_layout->setContentsMargins(4, 4, 4, 4);

        scroll_area->setWidget(scroll_content);
        parent_layout->addWidget(scroll_area);
        return scroll_layout;
    }

    template <typename Receiver>
    inline QTimer* makeUpdateTimer(Receiver* receiver, const char* slot, int interval_ms = 500)
    {
        QTimer* timer = new QTimer(receiver);
        QObject::connect(timer, SIGNAL(timeout()), receiver, slot);
        timer->start(interval_ms);
        return timer;
    }

}  // namespace chroma_rviz_plugins::common