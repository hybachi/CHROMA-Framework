cmake_minimum_required(VERSION 3.8)
project(chroma_rviz_plugins)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Wno-array-bounds -Wno-stringop-overflow -Wno-deprecated-declarations)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(chroma_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(pluginlib REQUIRED)
find_package(Qt5 COMPONENTS Widgets REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rviz_common REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(yaml-cpp REQUIRED)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_SKIP_RPATH TRUE)
set(CMAKE_SKIP_INSTALL_RPATH TRUE)

add_library(chroma_rviz_plugins SHARED
  # Common Helpers
  src/common/marker_factory.cpp

  # Fault Panel
  include/chroma_rviz_plugins/fault_panel.hpp
  src/fault_panel.cpp

  # Log Panel
  include/chroma_rviz_plugins/log_panel.hpp
  src/log_panel.cpp

  # Mission Panel
  include/chroma_rviz_plugins/mission_panel.hpp
  src/mission_panel.cpp

  # Status Panel & Robot Card
  include/chroma_rviz_plugins/robot_card.hpp
  include/chroma_rviz_plugins/status_panel.hpp
  src/robot_card.cpp
  src/status_panel.cpp

  # Task Panel & Task Card
  include/chroma_rviz_plugins/task_card.hpp
  include/chroma_rviz_plugins/task_panel.hpp
  src/task_card.cpp
  src/task_panel.cpp
)

target_include_directories(chroma_rviz_plugins PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(chroma_rviz_plugins
  ament_index_cpp
  chroma_interfaces
  geometry_msgs
  pluginlib
  rclcpp
  rviz_common
  visualization_msgs
  yaml-cpp
)

target_link_libraries(chroma_rviz_plugins Qt5::Widgets yaml-cpp)

pluginlib_export_plugin_description_file(rviz_common plugins.xml)

install(TARGETS chroma_rviz_plugins
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(DIRECTORY include/
  DESTINATION include
)

ament_export_dependencies(
  ament_index_cpp 
  chroma_interfaces 
  geometry_msgs 
  pluginlib 
  rclcpp 
  rviz_common 
  visualization_msgs 
  yaml-cpp
)

ament_package()