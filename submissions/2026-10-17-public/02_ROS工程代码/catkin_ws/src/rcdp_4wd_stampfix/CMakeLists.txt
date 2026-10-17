cmake_minimum_required(VERSION 3.5.1)
project(rcdp_4wd_stampfix)

find_package(catkin REQUIRED COMPONENTS geometry_msgs nav_msgs roscpp tf)
find_package(gazebo 11 REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread)
find_package(Threads REQUIRED)

catkin_package(
  LIBRARIES rcdp_4wd_stampfix
  CATKIN_DEPENDS geometry_msgs nav_msgs roscpp tf
)

link_directories(${GAZEBO_LIBRARY_DIRS})
add_library(rcdp_4wd_stampfix SHARED src/gazebo_ros_skid_steer_stampfix.cpp)
set_target_properties(rcdp_4wd_stampfix PROPERTIES
  CXX_STANDARD 14
  CXX_STANDARD_REQUIRED ON
  CXX_EXTENSIONS OFF
)
target_include_directories(rcdp_4wd_stampfix PRIVATE
  include ${catkin_INCLUDE_DIRS} ${GAZEBO_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS}
)
target_link_libraries(rcdp_4wd_stampfix
  ${catkin_LIBRARIES} ${GAZEBO_LIBRARIES} ${Boost_LIBRARIES} Threads::Threads
)
if(catkin_EXPORTED_TARGETS)
  add_dependencies(rcdp_4wd_stampfix ${catkin_EXPORTED_TARGETS})
endif()

install(TARGETS rcdp_4wd_stampfix LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION})
install(DIRECTORY include/${PROJECT_NAME}/ DESTINATION ${CATKIN_PACKAGE_INCLUDE_DESTINATION})
install(FILES README.md LICENSE UPSTREAM.json DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})

message(STATUS "rcdp_4wd_stampfix: Gazebo ${GAZEBO_VERSION}; four wheel joints; SimTime stamps")
