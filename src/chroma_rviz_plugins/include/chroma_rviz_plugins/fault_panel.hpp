#pragma once

#include <QComboBox>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <chroma_interfaces/msg/swarm_status.hpp>
#include <map>
#include <rclcpp/rclcpp.hpp>
#include <rviz_common/panel.hpp>
#include <set>
#include <std_msgs/msg/string.hpp>
#include <string>

namespace chroma_rviz_plugins
{
    class FaultPanel : public rviz_common::Panel
    {
        Q_OBJECT
    public:
        explicit FaultPanel(QWidget* parent = nullptr);
        ~FaultPanel() override;
        void onInitialize() override;

    protected Q_SLOTS:
        void onInjectClicked();
        void onClearClicked();

    private:
        void statusCallback(const chroma_interfaces::msg::SwarmStatus::SharedPtr msg);
        void ensurePublisherExists(const std::string& robot_id);
        void reportError(const QString& message);

        // UI Widgets
        QComboBox* robot_dropdown_;
        QComboBox* fault_dropdown_;
        QPushButton* inject_btn_;
        QPushButton* clear_btn_;
        QLabel* status_label_;

        // ROS Handles
        rclcpp::Node::SharedPtr node_;
        std::map<std::string, rclcpp::Publisher<std_msgs::msg::String>::SharedPtr> fault_pubs_;
        rclcpp::Subscription<chroma_interfaces::msg::SwarmStatus>::SharedPtr status_sub_;

        // State
        std::set<std::string> known_robots_;
    };

}  // namespace chroma_rviz_plugins