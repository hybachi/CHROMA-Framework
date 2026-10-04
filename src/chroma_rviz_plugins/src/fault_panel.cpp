#include "chroma_rviz_plugins/fault_panel.hpp"

#include <QString>
#include <pluginlib/class_list_macros.hpp>

#include "chroma_rviz_plugins/common/ros_node_helper.hpp"
#include "chroma_rviz_plugins/common/theme.hpp"

namespace chroma_rviz_plugins
{
    FaultPanel::FaultPanel(QWidget* parent) : rviz_common::Panel(parent)
    {
        QVBoxLayout* layout = new QVBoxLayout(this);

        layout->addWidget(new QLabel("Target Robot ID:"));
        robot_dropdown_ = new QComboBox();
        layout->addWidget(robot_dropdown_);

        layout->addWidget(new QLabel("Fault Type:"));
        fault_dropdown_ = new QComboBox();
        fault_dropdown_->addItem("mobility_penalty");
        fault_dropdown_->addItem("mobility_failure");
        fault_dropdown_->addItem("vision_penalty");
        fault_dropdown_->addItem("vision_failure");
        fault_dropdown_->setEditable(true);
        layout->addWidget(fault_dropdown_);

        inject_btn_ = new QPushButton("Inject Fault");
        layout->addWidget(inject_btn_);

        clear_btn_ = new QPushButton("Clear All Faults");
        layout->addWidget(clear_btn_);

        status_label_ = new QLabel("Ready.");
        status_label_->setStyleSheet(QString("font-size: 10px; color: %1; margin-top: 5px;").arg(theme::kTextMuted));
        layout->addWidget(status_label_);

        connect(inject_btn_, SIGNAL(clicked()), this, SLOT(onInjectClicked()));
        connect(clear_btn_, SIGNAL(clicked()), this, SLOT(onClearClicked()));
    }

    FaultPanel::~FaultPanel() = default;

    void FaultPanel::onInitialize()
    {
        node_ = common::getRosNode(this->getDisplayContext());

        status_sub_ = node_->create_subscription<chroma_interfaces::msg::SwarmStatus>(
            "/swarm/status", rclcpp::QoS(10).transient_local(),
            std::bind(&FaultPanel::statusCallback, this, std::placeholders::_1));
    }

    void FaultPanel::statusCallback(const chroma_interfaces::msg::SwarmStatus::SharedPtr msg)
    {
        std::string rid = msg->robot_id;
        if (known_robots_.find(rid) == known_robots_.end())
        {
            known_robots_.insert(rid);
            QMetaObject::invokeMethod(this, [this, rid]() { robot_dropdown_->addItem(QString::fromStdString(rid)); });
        }
    }

    void FaultPanel::reportError(const QString& message)
    {
        status_label_->setText(message);
        status_label_->setStyleSheet(QString("font-size: 10px; color: %1; font-weight: bold;").arg(theme::kAmber));
    }

    void FaultPanel::ensurePublisherExists(const std::string& robot_id)
    {
        if (fault_pubs_.find(robot_id) == fault_pubs_.end())
        {
            std::string topic_name = "/" + robot_id + "/inject_fault";
            fault_pubs_[robot_id] = node_->create_publisher<std_msgs::msg::String>(topic_name, 10);
        }
    }

    void FaultPanel::onInjectClicked()
    {
        std::string robot_id = robot_dropdown_->currentText().trimmed().toStdString();
        std::string fault_type = fault_dropdown_->currentText().trimmed().toStdString();

        if (robot_id.empty())
        {
            reportError("Error: No Robot ID selected.");
            return;
        }

        ensurePublisherExists(robot_id);

        auto msg = std_msgs::msg::String();
        msg.data = fault_type;
        fault_pubs_[robot_id]->publish(msg);

        status_label_->setText(
            QString("Injected '%1' into %2").arg(QString::fromStdString(fault_type), QString::fromStdString(robot_id)));
        status_label_->setStyleSheet(QString("font-size: 10px; color: %1; font-weight: bold;").arg(theme::kRed));
    }

    void FaultPanel::onClearClicked()
    {
        std::string robot_id = robot_dropdown_->currentText().trimmed().toStdString();

        if (robot_id.empty())
        {
            reportError("Error: No Robot ID selected.");
            return;
        }

        ensurePublisherExists(robot_id);

        auto msg = std_msgs::msg::String();
        msg.data = "reset";
        fault_pubs_[robot_id]->publish(msg);

        status_label_->setText(QString("Cleared faults for %1").arg(QString::fromStdString(robot_id)));
        status_label_->setStyleSheet(QString("font-size: 10px; color: %1; font-weight: bold;").arg(theme::kEmerald));
    }

}  // namespace chroma_rviz_plugins

PLUGINLIB_EXPORT_CLASS(chroma_rviz_plugins::FaultPanel, rviz_common::Panel)