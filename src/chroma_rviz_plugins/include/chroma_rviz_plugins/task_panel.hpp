#pragma once

#include <QTimer>
#include <QVBoxLayout>
#include <chroma_interfaces/msg/task.hpp>
#include <chroma_interfaces/msg/task_allocation.hpp>
#include <map>
#include <mutex>
#include <rclcpp/rclcpp.hpp>
#include <rviz_common/panel.hpp>
#include <string>
#include <visualization_msgs/msg/marker_array.hpp>

#include "chroma_rviz_plugins/task_card.hpp"

namespace chroma_rviz_plugins
{
    class TaskPanel : public rviz_common::Panel
    {
        Q_OBJECT
    public:
        explicit TaskPanel(QWidget* parent = nullptr);
        ~TaskPanel() override;
        void onInitialize() override;

    protected Q_SLOTS:
        void updateUI();
        void handleAbort(std::string task_id);

    private:
        void taskCallback(const chroma_interfaces::msg::Task::SharedPtr msg);
        void allocationCallback(const chroma_interfaces::msg::TaskAllocation::SharedPtr msg);
        void cleanupTask(const std::string& task_id);

        // UI Widgets
        QVBoxLayout* scroll_layout_;
        QTimer* update_timer_;

        // ROS Handles
        rclcpp::Node::SharedPtr node_;
        rclcpp::Subscription<chroma_interfaces::msg::Task>::SharedPtr task_sub_;
        rclcpp::Subscription<chroma_interfaces::msg::TaskAllocation>::SharedPtr alloc_sub_;
        rclcpp::Publisher<chroma_interfaces::msg::TaskAllocation>::SharedPtr alloc_pub_;
        rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;

        // State
        std::map<std::string, TaskData> active_tasks_;
        std::map<std::string, TaskCard*> task_cards_;
        std::mutex task_mutex_;
    };

}  // namespace chroma_rviz_plugins