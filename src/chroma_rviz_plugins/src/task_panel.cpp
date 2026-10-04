#include "chroma_rviz_plugins/task_panel.hpp"

#include <pluginlib/class_list_macros.hpp>

#include "chroma_rviz_plugins/common/constants.hpp"
#include "chroma_rviz_plugins/common/marker_factory.hpp"
#include "chroma_rviz_plugins/common/panel_widgets.hpp"
#include "chroma_rviz_plugins/common/ros_node_helper.hpp"

namespace chroma_rviz_plugins
{

    TaskPanel::TaskPanel(QWidget* parent) : rviz_common::Panel(parent)
    {
        QVBoxLayout* layout = new QVBoxLayout(this);
        layout->setContentsMargins(0, 0, 0, 0);
        scroll_layout_ = common::makeScrollableCardLayout(this, layout);
        update_timer_ = common::makeUpdateTimer(this, SLOT(updateUI()));
    }

    TaskPanel::~TaskPanel() = default;

    void TaskPanel::onInitialize()
    {
        node_ = common::getRosNode(this->getDisplayContext());

        task_sub_ = node_->create_subscription<chroma_interfaces::msg::Task>(
            "/mission/tasks", 10, std::bind(&TaskPanel::taskCallback, this, std::placeholders::_1));

        alloc_sub_ = node_->create_subscription<chroma_interfaces::msg::TaskAllocation>(
            "/swarm/allocation", 10, std::bind(&TaskPanel::allocationCallback, this, std::placeholders::_1));

        alloc_pub_ = node_->create_publisher<chroma_interfaces::msg::TaskAllocation>("/swarm/allocation", 10);
        marker_pub_ = node_->create_publisher<visualization_msgs::msg::MarkerArray>("/mission/markers", 10);
    }

    void TaskPanel::taskCallback(const chroma_interfaces::msg::Task::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(task_mutex_);

        std::string reqs = "[";
        for (size_t i = 0; i < msg->required_capabilities.size(); i++)
        {
            reqs += msg->required_capabilities[i];
            if (i < msg->required_capabilities.size() - 1)
            {
                reqs += ", ";
            }
        }
        reqs += "]";

        if (active_tasks_.find(msg->task_id) == active_tasks_.end())
        {
            TaskData td;
            td.id = msg->task_id;
            td.type = msg->type;
            td.requirements = reqs;
            active_tasks_[msg->task_id] = td;
        }
        else
        {
            active_tasks_[msg->task_id].type = msg->type;
            active_tasks_[msg->task_id].requirements = reqs;
        }
    }

    void TaskPanel::allocationCallback(const chroma_interfaces::msg::TaskAllocation::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(task_mutex_);

        if (msg->status == constants::STATUS_CANCELLED)
        {
            return;
        }

        if (active_tasks_.find(msg->task_id) == active_tasks_.end())
        {
            TaskData td;
            td.id = msg->task_id;
            active_tasks_[msg->task_id] = td;
        }

        active_tasks_[msg->task_id].robot = msg->robot_id;
        active_tasks_[msg->task_id].status = msg->status;

        if (msg->status == constants::STATUS_COMPLETED || msg->status == constants::STATUS_FAILED ||
            msg->status == constants::STATUS_ABORTED)
        {
            QTimer::singleShot(5000, [this, id = msg->task_id]() { cleanupTask(id); });
        }
    }

    void TaskPanel::handleAbort(std::string task_id)
    {
        if (task_cards_.find(task_id) != task_cards_.end())
        {
            task_cards_[task_id]->setAborting();
        }

        auto cancel_msg = chroma_interfaces::msg::TaskAllocation();
        cancel_msg.task_id = task_id;
        cancel_msg.robot_id = "OPERATOR";
        cancel_msg.status = constants::STATUS_CANCELLED;
        alloc_pub_->publish(cancel_msg);

        QTimer::singleShot(1500, [this, task_id]() { cleanupTask(task_id); });
    }

    void TaskPanel::cleanupTask(const std::string& task_id)
    {
        std::lock_guard<std::mutex> lock(task_mutex_);

        visualization_msgs::msg::MarkerArray marker_array;
        marker_array.markers.push_back(common::makeDeleteAll("task_" + task_id));
        marker_pub_->publish(marker_array);

        if (task_cards_.find(task_id) != task_cards_.end())
        {
            TaskCard* card = task_cards_[task_id];
            scroll_layout_->removeWidget(card);
            delete card;
            task_cards_.erase(task_id);
        }
        active_tasks_.erase(task_id);
    }

    void TaskPanel::updateUI()
    {
        std::lock_guard<std::mutex> lock(task_mutex_);

        for (const auto& pair : active_tasks_)
        {
            const std::string& tid = pair.first;
            const TaskData& data = pair.second;

            if (task_cards_.find(tid) == task_cards_.end())
            {
                TaskCard* new_card = new TaskCard();
                connect(new_card, SIGNAL(abortRequested(std::string)), this, SLOT(handleAbort(std::string)));
                scroll_layout_->addWidget(new_card);
                task_cards_[tid] = new_card;
            }

            task_cards_[tid]->updateData(data);
        }
    }

}  // namespace chroma_rviz_plugins

PLUGINLIB_EXPORT_CLASS(chroma_rviz_plugins::TaskPanel, rviz_common::Panel)