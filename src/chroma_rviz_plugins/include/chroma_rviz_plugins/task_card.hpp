#pragma once

#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <string>

namespace chroma_rviz_plugins
{
    struct TaskData
    {
        std::string id;
        std::string type = "UNKNOWN";
        std::string robot = "UNASSIGNED";
        std::string status = "PENDING";
        std::string requirements = "";
    };

    class TaskCard : public QFrame
    {
        Q_OBJECT
    public:
        explicit TaskCard(QWidget* parent = nullptr);
        void updateData(const TaskData& data);
        void setAborting();

    Q_SIGNALS:
        void abortRequested(std::string task_id);

    private Q_SLOTS:
        void onAbortClicked();

    private:
        // UI Widgets
        QLabel* id_label_;
        QLabel* type_label_;
        QLabel* robot_label_;
        QLabel* status_label_;
        QLabel* req_label_;
        QPushButton* abort_btn_;

        // State
        std::string current_task_id_;
    };

}  // namespace chroma_rviz_plugins