cmake_minimum_required(VERSION 3.8)
project(quadruped_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# --- DEPENDENCIAS ROS ---
find_package(ament_cmake REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(ros_gz_interfaces REQUIRED) # añadido
find_package(ros_gz_sim REQUIRED)
find_package(std_msgs REQUIRED)

# --- DEPENDENCIAS DE GAZEBO (vendor packages de Jazzy) ---
find_package(gz-sim8 REQUIRED)
find_package(gz-transport13 REQUIRED)

# --- CREACIÓN DE LA LIBRERÍA DEL PLUGIN ---
add_library(gaz_publisher SHARED src/gaz_publisher.cpp)

# --- ENLAZADO DE DEPENDENCIAS ---
target_link_libraries(gaz_publisher
  gz-sim8::core
  gz-transport13::core
)

ament_target_dependencies(gaz_publisher
  rclcpp_components
  ros_gz_sim
  ros_gz_interfaces # añadido
  std_msgs
)

# --- INSTALACIÓN ---
install(TARGETS gaz_publisher DESTINATION lib)

install(
  DIRECTORY worlds models
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/telemetry_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# --- CONFIGURACIÓN DEL PAQUETE AMENT ---
ament_export_dependencies(
  rclcpp_components
  ros_gz_sim
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
