#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "olfaction_msgs/msg/gas_sensor.hpp"   // <--- nombre correcto

using std::placeholders::_1;

class GasBridgeNode : public rclcpp::Node
{
public:
  GasBridgeNode()
  : Node("gas_bridge")
  {
    // Parámetros configurables
    sensor_topic_ = this->declare_parameter<std::string>(
      "sensor_topic", "/fake_pid/Sensor_reading");
    gas_topic_ = this->declare_parameter<std::string>(
      "gas_topic", "/gas");
    scale_ = this->declare_parameter<double>("scale", 1.0);
    offset_ = this->declare_parameter<double>("offset", 0.0);

    RCLCPP_INFO(
      this->get_logger(),
      "GasBridgeNode: escuchando '%s', publicando en '%s' (y = %.3f * raw + %.3f)",
      sensor_topic_.c_str(), gas_topic_.c_str(), scale_, offset_);

    gas_pub_ = this->create_publisher<std_msgs::msg::Float32>(gas_topic_, 10);

    // Tipo correcto: olfaction_msgs::msg::GasSensor
    sensor_sub_ = this->create_subscription<olfaction_msgs::msg::GasSensor>(
      sensor_topic_, 10,
      std::bind(&GasBridgeNode::sensorCallback, this, _1));
  }

private:
  void sensorCallback(const olfaction_msgs::msg::GasSensor::SharedPtr msg)
  {
    // /fake_pid/Sensor_reading tiene campos: technology, manufacturer, raw, etc.
    // Nos quedamos con msg->raw y lo escalamos
    float value = static_cast<float>(scale_ * msg->raw + offset_);

    std_msgs::msg::Float32 out;
    out.data = value;
    gas_pub_->publish(out);
  }

  std::string sensor_topic_;
  std::string gas_topic_;
  double scale_;
  double offset_;

  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr gas_pub_;
  rclcpp::Subscription<olfaction_msgs::msg::GasSensor>::SharedPtr sensor_sub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<GasBridgeNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
