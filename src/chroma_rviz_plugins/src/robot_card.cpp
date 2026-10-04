#include "chroma_rviz_plugins/robot_card.hpp"

#include "chroma_rviz_plugins/common/theme.hpp"

namespace chroma_rviz_plugins
{

    RobotCard::RobotCard(QWidget* parent) : QFrame(parent)
    {
        this->setAttribute(Qt::WA_StyledBackground, true);
        this->setStyleSheet(
            QString("RobotCard { background-color: %1; border-radius: 6px; border: 1px solid %2; margin: 2px; }")
                .arg(theme::kSlatePanel, theme::kSlateBorder));

        QVBoxLayout* main_layout = new QVBoxLayout(this);
        main_layout->setContentsMargins(8, 8, 8, 8);
        main_layout->setSpacing(2);

        QHBoxLayout* header_layout = new QHBoxLayout();
        id_label_ = new QLabel("UNKNOWN");
        id_label_->setStyleSheet(QString("font-weight: bold; font-size: 13px; color: %1;").arg(theme::kEmerald));
        type_label_ = new QLabel("Type: UNKNOWN");
        type_label_->setStyleSheet(QString("font-size: 9px; color: %1;").arg(theme::kTextMutedL));
        type_label_->setAlignment(Qt::AlignRight | Qt::AlignBottom);

        header_layout->addWidget(id_label_);
        header_layout->addWidget(type_label_);
        main_layout->addLayout(header_layout);

        QFrame* line = new QFrame();
        line->setFrameShape(QFrame::HLine);
        line->setStyleSheet(QString("background-color: %1;").arg(theme::kSlateBorder));
        main_layout->addWidget(line);

        caps_layout_ = new QVBoxLayout();
        caps_layout_->setSpacing(4);
        main_layout->addLayout(caps_layout_);
    }

    void RobotCard::ensureCapabilityWidgetsExist(const std::string& cap_name)
    {
        if (cap_bars_.find(cap_name) != cap_bars_.end())
        {
            return;
        }

        QHBoxLayout* row = new QHBoxLayout();
        row->setContentsMargins(0, 0, 0, 0);

        QLabel* lbl = new QLabel(QString::fromStdString(cap_name));
        lbl->setStyleSheet(QString("font-size: 9px; font-weight: bold; color: %1;").arg(theme::kTextMuted));
        lbl->setFixedWidth(55);

        QProgressBar* bar = new QProgressBar();
        bar->setRange(0, 100);
        bar->setFixedHeight(8);
        bar->setTextVisible(false);

        QLabel* val_lbl = new QLabel("100%");
        val_lbl->setStyleSheet(QString("font-size: 10px; color: %1;").arg(theme::kTextMutedL));
        val_lbl->setFixedWidth(30);
        val_lbl->setAlignment(Qt::AlignRight | Qt::AlignVCenter);

        row->addWidget(lbl);
        row->addWidget(bar);
        row->addWidget(val_lbl);

        caps_layout_->addLayout(row);
        cap_bars_[cap_name] = bar;
        cap_vals_[cap_name] = val_lbl;
    }

    void RobotCard::updateData(const chroma_interfaces::msg::SwarmStatus& msg)
    {
        id_label_->setText(QString::fromStdString(msg.robot_id));
        type_label_->setText(QString::fromStdString(msg.robot_type));

        for (const auto& cap : msg.capabilities)
        {
            std::string cap_name = cap.type;
            int percentage = static_cast<int>(cap.value * 100.0);

            ensureCapabilityWidgetsExist(cap_name);

            cap_bars_[cap_name]->setValue(percentage);
            cap_vals_[cap_name]->setText(QString::number(percentage) + "%");

            QString bar_style = QString(
                                    "QProgressBar { background-color: %1; border: none; border-radius: 4px; } "
                                    "QProgressBar::chunk { border-radius: 4px; ")
                                    .arg(theme::kSlateBorder);

            if (cap.is_degraded)
            {
                bar_style += QString("background-color: %1; }").arg(theme::kRed);
            }
            else if (percentage < 60)
            {
                bar_style += QString("background-color: %1; }").arg(theme::kAmber);
            }
            else
            {
                bar_style += QString("background-color: %1; }").arg(theme::kEmerald);
            }

            cap_bars_[cap_name]->setStyleSheet(bar_style);
        }
    }

}  // namespace chroma_rviz_plugins