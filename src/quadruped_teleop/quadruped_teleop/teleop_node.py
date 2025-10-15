import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from flask import Flask, Response
import threading

# Flask app
app = Flask(__name__)

# Variable global para almacenar el último frame
latest_frame = None
bridge = CvBridge()

@app.route('/frame')
def get_frame():
    """
    Endpoint HTTP que devuelve el último frame JPEG
    """
    global latest_frame
    if latest_frame is None:
        return "No frame available", 503

    # Encode frame as JPEG
    ret, jpeg = cv2.imencode('.jpg', latest_frame)
    if not ret:
        return "Failed to encode frame", 500

    return Response(jpeg.tobytes(), mimetype='image/jpeg')


def run_flask():
    """
    Ejecuta Flask en un hilo separado
    """
    app.run(host='0.0.0.0', port=5000, threaded=True)


class CameraServer(Node):
    def __init__(self):
        super().__init__('camera_server')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )
        self.get_logger().info("Subscribed to /camera/image_raw")

    def camera_callback(self, msg):
        """
        Convierte el mensaje ROS Image a OpenCV frame (RGB8)
        """
        global latest_frame
        try:
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
            latest_frame = cv_image
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")


def main(args=None):
    rclpy.init(args=args)
    
    # Ejecuta Flask en un hilo
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Nodo ROS
    node = CameraServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
