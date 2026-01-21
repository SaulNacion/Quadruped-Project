#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
import struct
import numpy as np

class AddLidarTimestamps(Node):
    def __init__(self):
        super().__init__('add_lidar_timestamps')
        
        self.subscription = self.create_subscription(
            PointCloud2,
            '/unitree_lidar/points',
            self.lidar_callback,
            10)
        
        self.publisher = self.create_publisher(
            PointCloud2,
            '/unitree_lidar/points_stamped',
            10)
        
        self.get_logger().info('🔧 Adding timestamps to /lidar → /lidar_with_time')

    def lidar_callback(self, msg):
        # Calcular tiempo de escaneo (10Hz = 0.1s)
        scan_duration = 1.0 / 10.0  # Ajustar según tu update_rate
        
        # Leer datos originales
        point_step = msg.point_step
        num_points = msg.width * msg.height
        
        # Crear nuevo PointCloud2 con campo 'time'
        new_fields = list(msg.fields)
        
        # Verificar si 'time' ya existe
        has_time = any(f.name == 'time' for f in new_fields)
        
        if not has_time:
            # Agregar campo 'time'
            time_field = PointField()
            time_field.name = 'time'
            time_field.offset = msg.point_step
            time_field.datatype = PointField.FLOAT32
            time_field.count = 1
            new_fields.append(time_field)
            
            # Nuevo point_step
            new_point_step = msg.point_step + 4  # FLOAT32 = 4 bytes
            
            # Crear datos nuevos
            new_data = bytearray()
            timestamps = np.linspace(0.0, scan_duration, num_points, dtype=np.float32)
            
            for i in range(num_points):
                # Copiar punto original
                start = i * point_step
                end = start + point_step
                new_data.extend(msg.data[start:end])
                
                # Agregar timestamp
                new_data.extend(struct.pack('f', timestamps[i]))
            
            # Crear mensaje nuevo
            new_msg = PointCloud2()
            new_msg.header = msg.header
            new_msg.height = msg.height
            new_msg.width = msg.width
            new_msg.fields = new_fields
            new_msg.is_bigendian = msg.is_bigendian
            new_msg.point_step = new_point_step
            new_msg.row_step = new_point_step * msg.width
            new_msg.data = bytes(new_data)
            new_msg.is_dense = msg.is_dense
            
            self.publisher.publish(new_msg)
        else:
            # Ya tiene timestamps, solo republicar
            self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AddLidarTimestamps()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()