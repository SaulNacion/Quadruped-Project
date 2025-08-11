import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.publisher_ = self.create_publisher(Image, 'camera_frame', 10)
        self.device = 0
        self.fps = 30
        self.init_param()

        #capturo el video
        self.cap = cv2.VideoCapture(self.device)  
        if not self.cap.isOpened():
            self.get_logger().warn(f"No se puede abrir el dispositivo de video {self.device}")
        self.br = CvBridge()

        rate = 1/self.fps
        # Publicar cada 100 ms
        self.timer = self.create_timer(rate, self.timer_callback)  

    def init_param(self):
        # descriptor='Dipositivo para capturar el video, esto aparece haciendo --ls //dev-- el dispositivo aparece como videoX, donde x es un número')
        self.declare_parameter('device', 
                               value=0)
        self.device = self.get_parameter('device').get_parameter_value().integer_value
        self.get_logger().info("Video device  : %2d " % (self.device))

        # Frames por segundo
        self.declare_parameter('fps', 
                               value=30)
        self.fps = self.get_parameter('fps').get_parameter_value().integer_value
        self.get_logger().info("Frames por segundo : %2d "  % (self.fps))

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # Publicar el frame convertido a mensaje Image de ROS2
            self.publisher_.publish(self.br.cv2_to_imgmsg(frame, 'bgr8'))

    def __del__(self):
        self.cap.release()  # Asegurarse de liberar la cámara cuando termine el nodo

def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
 
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '_main_':
    main()