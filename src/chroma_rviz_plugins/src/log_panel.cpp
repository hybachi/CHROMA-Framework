#include "chroma_rviz_plugins/log_panel.hpp"

#include <QScrollBar>
#include <QString>
#include <pluginlib/class_list_macros.hpp>

#include "chroma_rviz_plugins/common/ros_node_helper.hpp"
#include "chroma_rviz_plugins/common/theme.hpp"

namespace chroma_rviz_plugins
{

    LogPanel::LogPanel(QWidget* parent) : rviz_common::Panel(parent)
    {
        QVBoxLayout* layout = new QVBoxLayout(this);
        layout->setContentsMargins(4, 4, 4, 4);

        QHBoxLayout* controls_layout = new QHBoxLayout();

        cb_info_ = new QCheckBox("INFO");
        cb_info_->setChecked(true);
        cb_warn_ = new QCheckBox("WARN");
        cb_warn_->setChecked(true);
        cb_error_ = new QCheckBox("ERROR");
        cb_error_->setChecked(true);

        controls_layout->addWidget(cb_info_);
        controls_layout->addWidget(cb_warn_);
        controls_layout->addWidget(cb_error_);
        controls_layout->addStretch();

        clear_btn_ = new QPushButton("Clear");
        controls_layout->addWidget(clear_btn_);

        layout->addLayout(controls_layout);

        text_edit_ = new QTextEdit();
        text_edit_->setReadOnly(true);

        text_edit_->setStyleSheet(
            QString("QTextEdit { background-color: %1; color: %2; font-family: 'Courier New', monospace; "
                    "font-size: 11px; border: 1px solid %3; border-radius: 4px; }")
                .arg(theme::kSlateBg, theme::kTextLight, theme::kSlateBorder));

        layout->addWidget(text_edit_);

        connect(clear_btn_, SIGNAL(clicked()), this, SLOT(onClearClicked()));
    }

    LogPanel::~LogPanel() = default;

    void LogPanel::onInitialize()
    {
        node_ = common::getRosNode(this->getDisplayContext());

        log_sub_ = node_->create_subscription<rcl_interfaces::msg::Log>(
            "/rosout", 100, std::bind(&LogPanel::logCallback, this, std::placeholders::_1));
    }

    void LogPanel::logCallback(const rcl_interfaces::msg::Log::SharedPtr msg)
    {
        std::string node_name = msg->name;
        if (node_name.find("rviz") != std::string::npos || node_name.find("gazebo") != std::string::npos ||
            node_name.find("transform") != std::string::npos)
        {
            return;
        }

        QString color;
        QString level;
        int msg_level = msg->level;

        switch (msg_level)
        {
            case rcl_interfaces::msg::Log::DEBUG:
                return;
            case rcl_interfaces::msg::Log::INFO:
                color = theme::kSkyBlue;
                level = "[INFO]";
                break;
            case rcl_interfaces::msg::Log::WARN:
                color = theme::kAmber;
                level = "[WARN]";
                break;
            case rcl_interfaces::msg::Log::ERROR:
            case rcl_interfaces::msg::Log::FATAL:
                color = theme::kRed;
                level = "[ERROR]";
                break;
            default:
                color = theme::kTextLight;
                level = "[LOG]";
        }

        QString formatted_msg =
            QString("<span style='color:%1;'>%2 [%3]: %4</span>")
                .arg(color, level, QString::fromStdString(node_name), QString::fromStdString(msg->msg));

        QMetaObject::invokeMethod(this,
                                  [this, msg_level, formatted_msg]()
                                  {
                                      bool show_log = false;
                                      if (msg_level == rcl_interfaces::msg::Log::INFO && cb_info_->isChecked())
                                      {
                                          show_log = true;
                                      }
                                      else if (msg_level == rcl_interfaces::msg::Log::WARN && cb_warn_->isChecked())
                                      {
                                          show_log = true;
                                      }
                                      else if ((msg_level == rcl_interfaces::msg::Log::ERROR ||
                                                msg_level == rcl_interfaces::msg::Log::FATAL) &&
                                               cb_error_->isChecked())
                                      {
                                          show_log = true;
                                      }

                                      if (show_log)
                                      {
                                          text_edit_->append(formatted_msg);
                                          QScrollBar* sb = text_edit_->verticalScrollBar();
                                          sb->setValue(sb->maximum());
                                      }
                                  });
    }

    void LogPanel::onClearClicked()
    {
        text_edit_->clear();
    }

}  // namespace chroma_rviz_plugins

PLUGINLIB_EXPORT_CLASS(chroma_rviz_plugins::LogPanel, rviz_common::Panel)