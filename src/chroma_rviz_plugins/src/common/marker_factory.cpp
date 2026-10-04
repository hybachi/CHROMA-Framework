#include "chroma_rviz_plugins/common/marker_factory.hpp"

namespace chroma_rviz_plugins::common
{
    visualization_msgs::msg::Marker makeBaseMarker(const std::string& ns, int id, int type, const theme::Color& color,
                                                   const rclcpp::Time& stamp)
    {
        visualization_msgs::msg::Marker m;
        m.header.frame_id = "map";
        m.header.stamp = stamp;
        m.ns = ns;
        m.id = id;
        m.type = type;
        m.action = visualization_msgs::msg::Marker::ADD;
        m.color.r = color.r;
        m.color.g = color.g;
        m.color.b = color.b;
        m.color.a = color.a;
        return m;
    }

    visualization_msgs::msg::Marker makeSphere(const geometry_msgs::msg::Point& pos, const std::string& ns, int id,
                                               const theme::Color& color, float scale, const rclcpp::Time& stamp)
    {
        auto m = makeBaseMarker(ns, id, visualization_msgs::msg::Marker::SPHERE, color, stamp);
        m.pose.position = pos;
        m.scale.x = scale;
        m.scale.y = scale;
        m.scale.z = scale;
        return m;
    }

    visualization_msgs::msg::Marker makeTextLabel(const geometry_msgs::msg::Point& pos, const std::string& ns, int id,
                                                  const std::string& text, const theme::Color& color, float scale_z,
                                                  const rclcpp::Time& stamp)
    {
        auto m = makeBaseMarker(ns, id, visualization_msgs::msg::Marker::TEXT_VIEW_FACING, color, stamp);
        m.pose.position = pos;
        m.scale.z = scale_z;
        m.text = text;
        return m;
    }

    visualization_msgs::msg::Marker makeLine(const geometry_msgs::msg::Point& p1, const geometry_msgs::msg::Point& p2,
                                             const std::string& ns, int id, const theme::Color& color, float width,
                                             const rclcpp::Time& stamp)
    {
        auto m = makeBaseMarker(ns, id, visualization_msgs::msg::Marker::LINE_STRIP, color, stamp);
        m.scale.x = width;
        m.points.push_back(p1);
        m.points.push_back(p2);
        return m;
    }

    visualization_msgs::msg::Marker makeCube(const geometry_msgs::msg::Point& pos, const std::string& ns, int id,
                                             float scale_x, float scale_y, float scale_z, const theme::Color& color,
                                             const rclcpp::Time& stamp)
    {
        auto m = makeBaseMarker(ns, id, visualization_msgs::msg::Marker::CUBE, color, stamp);
        m.pose.position = pos;
        m.scale.x = scale_x;
        m.scale.y = scale_y;
        m.scale.z = scale_z;
        return m;
    }

    visualization_msgs::msg::Marker makeDeleteAll(const std::string& ns)
    {
        visualization_msgs::msg::Marker m;
        m.action = visualization_msgs::msg::Marker::DELETEALL;
        m.ns = ns;
        return m;
    }

}  // namespace chroma_rviz_plugins::common