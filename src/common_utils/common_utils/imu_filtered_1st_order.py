#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import math
import time

class ImuHzFilter(Node):
    def __init__(self):
        super().__init__('imu_hz_filter_node')

        # --- CONFIGURACIÓN ---
        # Definimos la Frecuencia de Corte en Hz (Hertz)
        # Ejemplo: 20.0 Hz significa que frecuencias superiores se atenúan.
        self.declare_parameter('cutoff_frequency', 20.0)
        
        # --- ESTADO INTERNO ---
        self.prev_time = None
        self.prev_accel = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.first_run = True

        # Suscriptor y Publicador
        self.subscription = self.create_subscription(
            Imu, '/imu', self.listener_callback, 10)
        self.publisher_ = self.create_publisher(Imu, '/imu_filtered_1st_order', 10)

        self.get_logger().info('Filtro IMU iniciado.')

    def listener_callback(self, msg):
        # 1. Obtener el tiempo actual del mensaje en segundos
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        
        # Obtenemos la frecuencia de corte deseada (puede cambiarse en vivo)
        cutoff_hz = self.get_parameter('cutoff_frequency').get_parameter_value().double_value

        # Valores crudos (raw)
        raw = {'x': msg.linear_acceleration.x, 
               'y': msg.linear_acceleration.y, 
               'z': msg.linear_acceleration.z}

        filtered = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        if self.first_run:
            # Inicialización
            self.prev_time = current_time
            self.prev_accel = raw
            filtered = raw
            self.first_run = False
        else:
            # 2. Calcular dt (diferencia de tiempo real entre mensajes)
            dt = current_time - self.prev_time
            
            # Protección contra dt=0 o saltos de tiempo negativos
            if dt <= 0:
                dt = 0.001 # Asumimos 1ms por seguridad si hay error

            # 3. Calcular Alpha dinámicamente para cumplir con los Hz exactos
            # Fórmula derivada de filtro RC discreto
            rc = 1.0 / (2.0 * math.pi * cutoff_hz)
            alpha = dt / (rc + dt)

            # 4. Aplicar el filtro
            filtered['x'] = alpha * raw['x'] + (1.0 - alpha) * self.prev_accel['x']
            filtered['y'] = alpha * raw['y'] + (1.0 - alpha) * self.prev_accel['y']
            filtered['z'] = alpha * raw['z'] + (1.0 - alpha) * self.prev_accel['z']

            # Actualizar estado
            self.prev_time = current_time
            self.prev_accel = filtered

        # Publicar
        out_msg = msg
        out_msg.linear_acceleration.x = filtered['x']
        out_msg.linear_acceleration.y = filtered['y']
        out_msg.linear_acceleration.z = filtered['z']
        
        self.publisher_.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuHzFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
