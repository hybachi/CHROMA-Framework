#include "chroma_rviz_plugins/task_card.hpp"

#include <QHBoxLayout>
#include <QVBoxLayout>

#include "chroma_rviz_plugins/common/constants.hpp"
#include "chroma_rviz_plugins/common/theme.hpp"

namespace chroma_rviz_plugins
{

    TaskCard::TaskCard(QWidget* parent) : QFrame(parent)
    {
        this->setStyleSheet(
            QString("TaskCard { background-color: %1; border-radius: 6px; border: 1px solid %2; margin: 2px; }")
                .arg(theme::kSlateCard, theme::kSlateBorderL));

        QVBoxLayout* main_layout = new QVBoxLayout(this);
        main_layout->setContentsMargins(6, 6, 6, 6);
        main_layout->setSpacing(2);

        QHBoxLayout* top_row = new QHBoxLayout();
        id_label_ = new QLabel("TASK_XXXX");
        id_label_->setStyleSheet(QString("font-weight: bold; font-size: 12px; color: %1;").arg(theme::kTextDark));

        status_label_ = new QLabel(constants::STATUS_PENDING);
        status_label_->setStyleSheet(QString("font-weight: bold; font-size: 11px; color: %1;").arg(theme::kTextMuted));
        status_label_->setAlignment(Qt::AlignRight | Qt::AlignVCenter);

        abort_btn_ = new QPushButton("X");
        abort_btn_->setFixedSize(20, 20);
        abort_btn_->setStyleSheet(
            QString("background-color: %1; color: white; font-weight: bold; border-radius: 4px; border: none;")
                .arg(theme::kRed));
        abort_btn_->setToolTip("Abort Task");

        top_row->addWidget(id_label_);
        top_row->addWidget(status_label_);
        top_row->addWidget(abort_btn_);
        main_layout->addLayout(top_row);

        QHBoxLayout* bot_row = new QHBoxLayout();
        type_label_ = new QLabel("Type: UNKNOWN");
        type_label_->setStyleSheet(QString("font-size: 10px; color: %1;").arg(theme::kTextMutedD));

        robot_label_ = new QLabel("Robot: UNASSIGNED");
        robot_label_->setStyleSheet(QString("font-size: 10px; font-weight: bold; color: %1;").arg(theme::kTextMutedD));
        robot_label_->setAlignment(Qt::AlignRight | Qt::AlignVCenter);

        bot_row->addWidget(type_label_);
        bot_row->addWidget(robot_label_);
        main_layout->addLayout(bot_row);

        req_label_ = new QLabel("Req: None");
        req_label_->setStyleSheet(QString("font-size: 9px; color: %1; font-style: italic;").arg(theme::kTextMutedL));
        main_layout->addWidget(req_label_);

        connect(abort_btn_, SIGNAL(clicked()), this, SLOT(onAbortClicked()));
    }

    void TaskCard::onAbortClicked()
    {
        Q_EMIT abortRequested(current_task_id_);
    }

    void TaskCard::setAborting()
    {
        abort_btn_->setEnabled(false);
        abort_btn_->setStyleSheet(
            QString("background-color: %1; color: white; font-weight: bold; border-radius: 4px; border: none;")
                .arg(theme::kTextMutedL));
        status_label_->setText("ABORTING...");
        status_label_->setStyleSheet(QString("font-weight: bold; font-size: 11px; color: %1;").arg(theme::kRed));
    }

    void TaskCard::updateData(const TaskData& data)
    {
        if (!abort_btn_->isEnabled())
        {
            return;
        }

        current_task_id_ = data.id;
        id_label_->setText(QString::fromStdString(data.id));
        type_label_->setText(QString::fromStdString(data.type));
        robot_label_->setText(QString::fromStdString(data.robot));
        status_label_->setText(QString::fromStdString(data.status));
        req_label_->setText(QString::fromStdString("Req: " + data.requirements));

        QString color_hex = theme::kAmber;
        if (data.status == constants::STATUS_COMPLETED)
        {
            color_hex = theme::kEmerald;
        }
        else if (data.status == constants::STATUS_ABORTED || data.status == constants::STATUS_FAILED)
        {
            color_hex = theme::kRed;
        }
        else if (data.status == constants::STATUS_ASSIGNED)
        {
            color_hex = theme::kBlue;
        }

        status_label_->setStyleSheet(QString("font-weight: bold; font-size: 11px; color: %1;").arg(color_hex));
    }

}  // namespace chroma_rviz_plugins