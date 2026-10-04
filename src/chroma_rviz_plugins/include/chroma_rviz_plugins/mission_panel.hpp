#pragma once

#include <QComboBox>
#include <QLabel>
#include <QPushButton>
#include <chroma_interfaces/msg/task.hpp>
#include <geometry_msgs/msg/point_stamped.hpp>
#include <map>
#include <rclcpp/rclcpp.hpp>
#include <rviz_common/panel.hpp>
#include <string>
#include <vector>
#include <visualization_msgs/msg/marker_array.hpp>

namespace chroma_rviz_plugins
{
    struct TaskConfig
    {
        std::string name;
        std::vector<std::string>
            requires;
        float min_score;
        std::string marker_type;
    };

    class MissionPanel : public rviz_common::Panel
    {
        Q_OBJECT

    public:
        explicit MissionPanel(QWidget* parent = nullptr);
        ~MissionPanel() override;

        void onInitialize() override;

    protected Q_SLOTS:
        void onPublishClicked();
        void onClearClicked();
        void updateUI();

    private:
        void loadTaskConfigs();
        void pointCallback(const geometry_msgs::msg::PointStamped::SharedPtr msg);

        void publishPendingMarkers();
        void publishConfirmedTaskMarker(const std::string& task_id);
        void clearPendingMarkers();

        void buildSearchMarkers(visualization_msgs::msg::MarkerArray& array, const std::string& ns,
                                const rclcpp::Time& now);
        void buildDeliveryMarkers(visualization_msgs::msg::MarkerArray& array, const std::string& ns,
                                  const rclcpp::Time& now);

        // UI Widgets
        QComboBox* task_type_dropdown_;
        QLabel* req_label_;
        QLabel* status_label_;
        QPushButton* publish_btn_;
        QPushButton* clear_btn_;

        // ROS Handles
        rclcpp::Node::SharedPtr node_;
        rclcpp::Subscription<geometry_msgs::msg::PointStamped>::SharedPtr point_sub_;
        rclcpp::Publisher<chroma_interfaces::msg::Task>::SharedPtr task_pub_;
        rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;

        // State
        std::vector<geometry_msgs::msg::Point> clicked_points_;
        std::map<std::string, TaskConfig> task_configs_;
    };

}  // namespace chroma_rviz_plugins