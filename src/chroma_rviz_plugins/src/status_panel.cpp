#include "chroma_rviz_plugins/status_panel.hpp"

#include <pluginlib/class_list_macros.hpp>

#include "chroma_rviz_plugins/common/panel_widgets.hpp"
#include "chroma_rviz_plugins/common/ros_node_helper.hpp"

namespace chroma_rviz_plugins
{

    StatusPanel::StatusPanel(QWidget* parent) : rviz_common::Panel(parent)
    {
        QVBoxLayout* layout = new QVBoxLayout(this);
        layout->setContentsMargins(0, 0, 0, 0);
        scroll_layout_ = common::makeScrollableCardLayout(this, layout);
        update_timer_ = common::makeUpdateTimer(this, SLOT(updateUI()));
    }

    StatusPanel::~StatusPanel() = default;

    void StatusPanel::onInitialize()
    {
        node_ = common::getRosNode(this->getDisplayContext());

        status_sub_ = node_->create_subscription<chroma_interfaces::msg::SwarmStatus>(
            "/swarm/status", rclcpp::QoS(10).transient_local(),
            std::bind(&StatusPanel::statusCallback, this, std::placeholders::_1));
    }

    void StatusPanel::statusCallback(const chroma_interfaces::msg::SwarmStatus::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(status_mutex_);
        latest_statuses_[msg->robot_id] = *msg;
    }

    void StatusPanel::updateUI()
    {
        std::lock_guard<std::mutex> lock(status_mutex_);

        for (const auto& pair : latest_statuses_)
        {
            const std::string& rid = pair.first;
            const auto& status_msg = pair.second;

            if (robot_cards_.find(rid) == robot_cards_.end())
            {
                RobotCard* new_card = new RobotCard();
                scroll_layout_->addWidget(new_card);
                robot_cards_[rid] = new_card;
            }

            robot_cards_[rid]->updateData(status_msg);
        }
    }

}  // namespace chroma_rviz_plugins

PLUGINLIB_EXPORT_CLASS(chroma_rviz_plugins::StatusPanel, rviz_common::Panel)