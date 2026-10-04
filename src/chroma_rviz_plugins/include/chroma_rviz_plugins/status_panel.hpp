#pragma once

#include <QTimer>
#include <QVBoxLayout>
#include <chroma_interfaces/msg/swarm_status.hpp>
#include <map>
#include <mutex>
#include <rclcpp/rclcpp.hpp>
#include <rviz_common/panel.hpp>
#include <string>

#include "chroma_rviz_plugins/robot_card.hpp"

namespace chroma_rviz_plugins
{
    class StatusPanel : public rviz_common::Panel
    {
        Q_OBJECT
    public:
        explicit StatusPanel(QWidget* parent = nullptr);
        ~StatusPanel() override;
        void onInitialize() override;

    protected Q_SLOTS:
        void updateUI();

    private:
        void statusCallback(const chroma_interfaces::msg::SwarmStatus::SharedPtr msg);

        // UI Widgets
        QVBoxLayout* scroll_layout_;
        QTimer* update_timer_;

        // ROS Handles
        rclcpp::Node::SharedPtr node_;
        rclcpp::Subscription<chroma_interfaces::msg::SwarmStatus>::SharedPtr status_sub_;

        // State
        std::map<std::string, RobotCard*> robot_cards_;
        std::map<std::string, chroma_interfaces::msg::SwarmStatus> latest_statuses_;
        std::mutex status_mutex_;
    };

}  // namespace chroma_rviz_plugins