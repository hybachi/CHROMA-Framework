#pragma once

#include <geometry_msgs/msg/point.hpp>
#include <rclcpp/time.hpp>
#include <string>
#include <visualization_msgs/msg/marker.hpp>

#include "chroma_rviz_plugins/common/theme.hpp"

namespace chroma_rviz_plugins::common
{
    visualization_msgs::msg::Marker makeSphere(const geometry_msgs::msg::Point& pos, const std::string& ns, int id,
                                               const theme::Color& color, float scale, const rclcpp::Time& stamp);

    visualization_msgs::msg::Marker makeTextLabel(const geometry_msgs::msg::Point& pos, const std::string& ns, int id,
                                                  const std::string& text, const theme::Color& color, float scale_z,
                                                  const rclcpp::Time& stamp);

    visualization_msgs::msg::Marker makeLine(const geometry_msgs::msg::Point& p1, const geometry_msgs::msg::Point& p2,
                                             const std::string& ns, int id, const theme::Color& color, float width,
                                             const rclcpp::Time& stamp);

    visualization_msgs::msg::Marker makeCube(const geometry_msgs::msg::Point& pos, const std::string& ns, int id,
                                             float scale_x, float scale_y, float scale_z, const theme::Color& color,
                                             const rclcpp::Time& stamp);

    visualization_msgs::msg::Marker makeDeleteAll(const std::string& ns);

}  // namespace chroma_rviz_plugins::common