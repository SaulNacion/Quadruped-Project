import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.subscription = self.create_subscription(
            Image,
            'camera_frame',
            self.listener_callback,
            10)

        self.br = CvBridge()

    def listener_callback(self, msg):
        # Convertir el mensaje de imagen de ROS a una imagen de OpenCV
        frame = self.br.imgmsg_to_cv2(msg, 'bgr8')
        
        # Mostrar la imagen en una ventana de OpenCV
        cv2.imshow("Camera", frame)
        
        # Espera 1 ms entre frames (y permite que OpenCV responda a eventos)
        if cv2.waitKey(1) == 27:  # Presiona 'ESC' para salir
            self.get_logger().info("Cerrando la ventana de video")
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = CameraSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    # Destruye el nodo al terminar
    node.destroy_node()
    rclpy.shutdown()
    # Cierra todas las ventanas de OpenCV
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
