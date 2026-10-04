#pragma once

#include <rclcpp/rclcpp.hpp>
#include <rviz_common/display_context.hpp>
#include <rviz_common/ros_integration/ros_node_abstraction_iface.hpp>

namespace chroma_rviz_plugins::common
{
    inline rclcpp::Node::SharedPtr getRosNode(rviz_common::DisplayContext* context)
    {
        return context->getRosNodeAbstraction().lock()->get_raw_node();
    }

}  // namespace chroma_rviz_plugins::common