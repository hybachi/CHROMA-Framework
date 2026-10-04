#pragma once

#include <QFrame>
#include <QLabel>
#include <QProgressBar>
#include <QVBoxLayout>
#include <chroma_interfaces/msg/swarm_status.hpp>
#include <map>
#include <string>

namespace chroma_rviz_plugins
{
    class RobotCard : public QFrame
    {
        Q_OBJECT
    public:
        explicit RobotCard(QWidget* parent = nullptr);
        void updateData(const chroma_interfaces::msg::SwarmStatus& msg);

    private:
        void ensureCapabilityWidgetsExist(const std::string& cap_name);

        // UI Widgets
        QLabel* id_label_;
        QLabel* type_label_;
        QVBoxLayout* caps_layout_;

        // State Mappings
        std::map<std::string, QProgressBar*> cap_bars_;
        std::map<std::string, QLabel*> cap_vals_;
    };

}  // namespace chroma_rviz_plugins