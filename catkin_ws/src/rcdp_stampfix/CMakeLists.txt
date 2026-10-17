cmake_minimum_required(VERSION 3.5.1)
project(rcdp_stampfix)

find_package(catkin REQUIRED COMPONENTS
  geometry_msgs
  nav_msgs
  roscpp
  sensor_msgs
  tf
)
find_package(gazebo 11 REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread)
find_package(Threads REQUIRED)

# Reuse only the installed ROS utility library, not the original diff-drive
# library or every sensor plugin exported by the gazebo_plugins package.
find_path(GAZEBO_ROS_UTILS_INCLUDE_DIR
  NAMES gazebo_plugins/gazebo_ros_utils.h
  HINTS ${catkin_INCLUDE_DIRS} ${CMAKE_PREFIX_PATH}
  PATH_SUFFIXES include
)
find_library(GAZEBO_ROS_UTILS_LIBRARY
  NAMES gazebo_ros_utils
  HINTS ${catkin_LIBRARY_DIRS} ${CMAKE_PREFIX_PATH}
  PATH_SUFFIXES lib
)
if(NOT GAZEBO_ROS_UTILS_INCLUDE_DIR OR NOT GAZEBO_ROS_UTILS_LIBRARY)
  message(FATAL_ERROR
    "gazebo_ros_utils header/library not found. Source the Noetic environment "
    "and check the installed ros-noetic-gazebo-plugins development files.")
endif()

catkin_package(
  LIBRARIES rcdp_diff_drive_stampfix
  CATKIN_DEPENDS geometry_msgs nav_msgs roscpp sensor_msgs tf
)

link_directories(${GAZEBO_LIBRARY_DIRS})
add_library(rcdp_diff_drive_stampfix SHARED
  src/gazebo_ros_diff_drive_stampfix.cpp
)
set_target_properties(rcdp_diff_drive_stampfix PROPERTIES
  CXX_STANDARD 14
  CXX_STANDARD_REQUIRED ON
  CXX_EXTENSIONS OFF
)
target_include_directories(rcdp_diff_drive_stampfix PRIVATE
  include
  ${GAZEBO_ROS_UTILS_INCLUDE_DIR}
  ${catkin_INCLUDE_DIRS}
  ${GAZEBO_INCLUDE_DIRS}
  ${Boost_INCLUDE_DIRS}
)
target_link_libraries(rcdp_diff_drive_stampfix
  ${GAZEBO_ROS_UTILS_LIBRARY}
  ${catkin_LIBRARIES}
  ${GAZEBO_LIBRARIES}
  ${Boost_LIBRARIES}
  Threads::Threads
)
if(catkin_EXPORTED_TARGETS)
  add_dependencies(rcdp_diff_drive_stampfix ${catkin_EXPORTED_TARGETS})
endif()

install(TARGETS rcdp_diff_drive_stampfix
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
)
install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION}
)
install(FILES README.md LICENSE UPSTREAM.json
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

message(STATUS "rcdp_stampfix: Gazebo ${GAZEBO_VERSION}; timestamp-only patch")
message(STATUS "rcdp_stampfix: utility library ${GAZEBO_ROS_UTILS_LIBRARY}")
