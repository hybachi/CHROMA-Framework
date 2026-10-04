#include "chroma_rviz_plugins/mission_panel.hpp"

#include <yaml-cpp/yaml.h>

#include <QVBoxLayout>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <cstdlib>
#include <ctime>
#include <pluginlib/class_list_macros.hpp>

#include "chroma_rviz_plugins/common/marker_factory.hpp"
#include "chroma_rviz_plugins/common/ros_node_helper.hpp"
#include "chroma_rviz_plugins/common/theme.hpp"

namespace chroma_rviz_plugins
{

    MissionPanel::MissionPanel(QWidget* parent) : rviz_common::Panel(parent)
    {
        std::srand(std::time(nullptr));

        QVBoxLayout* layout = new QVBoxLayout;

        task_type_dropdown_ = new QComboBox();
        layout->addWidget(new QLabel("Select Task Type:"));
        layout->addWidget(task_type_dropdown_);

        req_label_ = new QLabel("Requires: []");
        req_label_->setStyleSheet(
            QString("font-size: 10px; color: %1; font-style: italic; margin-bottom: 8px;").arg(theme::kTextMuted));
        layout->addWidget(req_label_);

        status_label_ = new QLabel("Points captured: 0/2\nUse 'Publish Point' tool on the map.");
        layout->addWidget(status_label_);

        publish_btn_ = new QPushButton("Publish Mission");
        publish_btn_->setEnabled(false);
        layout->addWidget(publish_btn_);

        clear_btn_ = new QPushButton("Clear Points");
        layout->addWidget(clear_btn_);

        setLayout(layout);

        connect(publish_btn_, SIGNAL(clicked()), this, SLOT(onPublishClicked()));
        connect(clear_btn_, SIGNAL(clicked()), this, SLOT(onClearClicked()));
        connect(task_type_dropdown_, SIGNAL(currentIndexChanged(int)), this, SLOT(updateUI()));
    }

    MissionPanel::~MissionPanel() = default;

    void MissionPanel::loadTaskConfigs()
    {
        try
        {
            std::string pkg_share = ament_index_cpp::get_package_share_directory("chroma_bringup");
            YAML::Node config = YAML::LoadFile(pkg_share + "/config/task_types.yaml");

            if (config["tasks"])
            {
                for (YAML::const_iterator it = config["tasks"].begin(); it != config["tasks"].end(); ++it)
                {
                    TaskConfig tc;
                    tc.name = it->first.as<std::string>();
                    tc.min_score = it->second["min_score"].as<float>();
                    tc.marker_type = it->second["marker_type"].as<std::string>();

                    if (it->second["requires"])
                    {
                        for (const auto& req : it->second["requires"])
                        {
                            tc.
                                requires
                                .push_back(req.as<std::string>());
                        }
                    }

                    task_configs_[tc.name] = tc;
                    task_type_dropdown_->addItem(QString::fromStdString(tc.name));
                }
            }
        }
        catch (const std::exception& e)
        {
            // Fallback if YAML is missing
            task_type_dropdown_->addItem("SEARCH");
            task_type_dropdown_->addItem("DELIVERY");

            task_configs_["SEARCH"] = {"SEARCH", {"PERCEPTION", "MOBILITY"}, 0.4f, "box"};
            task_configs_["DELIVERY"] = {"DELIVERY", {"PAYLOAD", "MOBILITY"}, 0.4f, "line"};
        }
    }

    void MissionPanel::onInitialize()
    {
        node_ = common::getRosNode(this->getDisplayContext());

        loadTaskConfigs();

        point_sub_ = node_->create_subscription<geometry_msgs::msg::PointStamped>(
            "/clicked_point", 10, std::bind(&MissionPanel::pointCallback, this, std::placeholders::_1));

        task_pub_ = node_->create_publisher<chroma_interfaces::msg::Task>("/mission/tasks", 10);
        marker_pub_ = node_->create_publisher<visualization_msgs::msg::MarkerArray>("/mission/markers", 10);

        updateUI();
    }

    void MissionPanel::pointCallback(const geometry_msgs::msg::PointStamped::SharedPtr msg)
    {
        if (clicked_points_.size() < 2)
        {
            clicked_points_.push_back(msg->point);
            updateUI();
            publishPendingMarkers();
        }
    }

    void MissionPanel::onClearClicked()
    {
        clearPendingMarkers();
        clicked_points_.clear();
        updateUI();
        status_label_->setText("Points captured: 0/2\nUse 'Publish Point' tool on the map.");
    }

    void MissionPanel::onPublishClicked()
    {
        if (clicked_points_.size() < 2)
        {
            return;
        }

        std::string task_type = task_type_dropdown_->currentText().toStdString();
        TaskConfig cfg = task_configs_[task_type];

        auto task_msg = chroma_interfaces::msg::Task();
        task_msg.task_id = "TASK_" + std::to_string(std::rand() % 10000);
        task_msg.type = task_type;
        task_msg.priority = 1.0;
        task_msg.location = clicked_points_[0];
        task_msg.target_area.push_back(clicked_points_[1]);
        task_msg.required_capabilities = cfg.
                                             requires;
        task_msg.min_capability_score = cfg.min_score;

        task_pub_->publish(task_msg);

        publishConfirmedTaskMarker(task_msg.task_id);

        clearPendingMarkers();
        clicked_points_.clear();

        status_label_->setText(
            QString("Mission %1 Published!\nWaiting for new points...").arg(QString::fromStdString(task_msg.task_id)));
        publish_btn_->setEnabled(false);
    }

    void MissionPanel::updateUI()
    {
        status_label_->setText(QString("Points captured: %1/2").arg(clicked_points_.size()));
        publish_btn_->setEnabled(clicked_points_.size() == 2);

        std::string task_type = task_type_dropdown_->currentText().toStdString();
        TaskConfig cfg = task_configs_[task_type];

        std::string req_str = "Requires: [";
        for (size_t i = 0; i < cfg.requires.size(); ++i)
        {
            req_str += cfg.
                           requires[
                               i];
            if (i < cfg.requires.size() - 1)
                req_str += ", ";
        }
        req_str += "]";

        req_label_->setText(QString::fromStdString(req_str));

        if (!clicked_points_.empty())
        {
            publishPendingMarkers();
        }
    }

    void MissionPanel::clearPendingMarkers()
    {
        visualization_msgs::msg::MarkerArray marker_array;
        marker_array.markers.push_back(common::makeDeleteAll("pending_task"));
        marker_pub_->publish(marker_array);
    }

    void MissionPanel::buildSearchMarkers(visualization_msgs::msg::MarkerArray& array, const std::string& ns,
                                          const rclcpp::Time& now)
    {
        geometry_msgs::msg::Point mid_pt;
        mid_pt.x = (clicked_points_[0].x + clicked_points_[1].x) / 2.0;
        mid_pt.y = (clicked_points_[0].y + clicked_points_[1].y) / 2.0;
        mid_pt.z = 0.3;

        geometry_msgs::msg::Point box_pos = mid_pt;
        box_pos.z = 0.01;
        float w = std::abs(clicked_points_[0].x - clicked_points_[1].x);
        float h = std::abs(clicked_points_[0].y - clicked_points_[1].y);

        theme::Color box_color = theme::kMarkerPending;
        box_color.a = 0.2f;

        array.markers.push_back(common::makeCube(box_pos, ns, 3, w, h, 0.01, box_color, now));
    }

    void MissionPanel::buildDeliveryMarkers(visualization_msgs::msg::MarkerArray& array, const std::string& ns,
                                            const rclcpp::Time& now)
    {
        array.markers.push_back(
            common::makeLine(clicked_points_[0], clicked_points_[1], ns, 3, theme::kMarkerPending, 0.04, now));

        geometry_msgs::msg::Point label_a_pos = clicked_points_[0];
        label_a_pos.z = 0.15;
        geometry_msgs::msg::Point label_b_pos = clicked_points_[1];
        label_b_pos.z = 0.15;

        array.markers.push_back(common::makeTextLabel(label_a_pos, ns, 4, "A", theme::kMarkerText, 0.15, now));
        array.markers.push_back(common::makeTextLabel(label_b_pos, ns, 5, "B", theme::kMarkerText, 0.15, now));
    }

    void MissionPanel::publishPendingMarkers()
    {
        visualization_msgs::msg::MarkerArray array;
        auto now = node_->now();
        std::string ns = "pending_task";

        for (size_t i = 0; i < clicked_points_.size(); i++)
        {
            auto pos = clicked_points_[i];
            pos.z = 0.05;

            array.markers.push_back(common::makeSphere(pos, ns, i, theme::kMarkerPending, 0.1, now));

            auto label_pos = pos;
            label_pos.x += (i == 0) ? 0.30 : -0.30;
            QString coord_str = QString("(%1,%2)").arg(pos.x, 0, 'f', 2).arg(pos.y, 0, 'f', 2);
            array.markers.push_back(common::makeTextLabel(label_pos, ns, 10 + i, coord_str.toStdString(),
                                                          theme::kMarkerTextDark, 0.1, now));
        }

        if (clicked_points_.size() == 2)
        {
            std::string task_type = task_type_dropdown_->currentText().toStdString();
            TaskConfig cfg = task_configs_[task_type];

            geometry_msgs::msg::Point mid_pt;
            mid_pt.x = (clicked_points_[0].x + clicked_points_[1].x) / 2.0;
            mid_pt.y = (clicked_points_[0].y + clicked_points_[1].y) / 2.0;
            mid_pt.z = 0.3;

            array.markers.push_back(
                common::makeTextLabel(mid_pt, ns, 2, "Publish\n" + task_type, theme::kMarkerText, 0.18, now));

            if (cfg.marker_type == "box")
            {
                buildSearchMarkers(array, ns, now);
            }
            else
            {
                buildDeliveryMarkers(array, ns, now);
            }
        }

        marker_pub_->publish(array);
    }

    void MissionPanel::publishConfirmedTaskMarker(const std::string& task_id)
    {
        visualization_msgs::msg::MarkerArray array;
        auto now = node_->now();
        std::string ns = "task_" + task_id;
        std::string task_type = task_type_dropdown_->currentText().toStdString();
        TaskConfig cfg = task_configs_[task_type];

        for (size_t i = 0; i < clicked_points_.size(); i++)
        {
            auto pos = clicked_points_[i];
            pos.z = 0.05;
            array.markers.push_back(common::makeSphere(pos, ns, i, theme::kMarkerConfirmed, 0.1, now));
        }

        geometry_msgs::msg::Point mid_pt;
        mid_pt.x = (clicked_points_[0].x + clicked_points_[1].x) / 2.0;
        mid_pt.y = (clicked_points_[0].y + clicked_points_[1].y) / 2.0;
        mid_pt.z = 0.3;

        array.markers.push_back(
            common::makeTextLabel(mid_pt, ns, 2, task_type + "\n" + task_id, theme::kMarkerText, 0.18, now));

        if (cfg.marker_type == "box")
        {
            geometry_msgs::msg::Point box_pos = mid_pt;
            box_pos.z = 0.01;
            float w = std::abs(clicked_points_[0].x - clicked_points_[1].x);
            float h = std::abs(clicked_points_[0].y - clicked_points_[1].y);

            theme::Color box_color = theme::kMarkerConfirmed;
            box_color.a = 0.2f;
            array.markers.push_back(common::makeCube(box_pos, ns, 3, w, h, 0.01, box_color, now));
        }
        else
        {
            array.markers.push_back(
                common::makeLine(clicked_points_[0], clicked_points_[1], ns, 3, theme::kMarkerConfirmed, 0.04, now));

            geometry_msgs::msg::Point label_a_pos = clicked_points_[0];
            label_a_pos.z = 0.15;
            geometry_msgs::msg::Point label_b_pos = clicked_points_[1];
            label_b_pos.z = 0.15;
            array.markers.push_back(common::makeTextLabel(label_a_pos, ns, 4, "A", theme::kMarkerText, 0.15, now));
            array.markers.push_back(common::makeTextLabel(label_b_pos, ns, 5, "B", theme::kMarkerText, 0.15, now));
        }

        marker_pub_->publish(array);
    }

}  // namespace chroma_rviz_plugins

PLUGINLIB_EXPORT_CLASS(chroma_rviz_plugins::MissionPanel, rviz_common::Panel)