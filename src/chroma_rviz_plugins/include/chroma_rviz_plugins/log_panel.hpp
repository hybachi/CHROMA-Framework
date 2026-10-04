#pragma once

#include <QCheckBox>
#include <QHBoxLayout>
#include <QPushButton>
#include <QTextEdit>
#include <QVBoxLayout>
#include <rcl_interfaces/msg/log.hpp>
#include <rclcpp/rclcpp.hpp>
#include <rviz_common/panel.hpp>
#include <string>

namespace chroma_rviz_plugins
{
    class LogPanel : public rviz_common::Panel
    {
        Q_OBJECT
    public:
        explicit LogPanel(QWidget* parent = nullptr);
        ~LogPanel() override;
        void onInitialize() override;

    protected Q_SLOTS:
        void onClearClicked();

    private:
        void logCallback(const rcl_interfaces::msg::Log::SharedPtr msg);

        // UI Widgets
        QTextEdit* text_edit_;
        QPushButton* clear_btn_;
        QCheckBox* cb_info_;
        QCheckBox* cb_warn_;
        QCheckBox* cb_error_;

        // ROS Handles
        rclcpp::Node::SharedPtr node_;
        rclcpp::Subscription<rcl_interfaces::msg::Log>::SharedPtr log_sub_;
    };

}  // namespace chroma_rviz_plugins