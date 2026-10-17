cmake_minimum_required(VERSION 3.0.2)
project(rcdp)
find_package(catkin REQUIRED)
catkin_package()
install(DIRECTORY urdf launch worlds config docs DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
install(DIRECTORY scripts DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
        USE_SOURCE_PERMISSIONS PATTERN "__pycache__" EXCLUDE)
