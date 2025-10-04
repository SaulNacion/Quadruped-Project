cmake_minimum_required(VERSION 3.8)
project(quadruped_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


find_package(ament_cmake REQUIRED)

# find dependencies
find_package(rclcpp REQUIRED)
find_package(xacro REQUIRED)
find_package(robot_state_publisher REQUIRED)


install(DIRECTORY
  DESTINATION share/${PROJECT_NAME}/

)
ament_package()
