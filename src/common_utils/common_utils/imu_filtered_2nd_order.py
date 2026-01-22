#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import math

class LowPassFilter:
    """Clase auxiliar para manejar el estado de un filtro simple"""
    def __init__(self):
        self.prev_out = 0.0
        self.is_initialized = False

    def update(self, input_val, alpha):
        if not self.is_initialized:
            self.prev_out = input_val
            self.is_initialized = True
        
        # Fórmula estándar: y[n] = alpha*x[n] + (1-alpha)*y[n-1]
        output = alpha * input_val + (1.0 - alpha) * self.prev_out
        self.prev_out = output
        return output

class ImuSecondOrderFilter(Node):
    def __init__(self):
        super().__init__('imu_second_order_filter')

        # --- CONFIGURACIÓN ---
        # Frecuencia de corte deseada para el sistema TOTAL
        self.declare_parameter('cutoff_frequency', 20.0) 
        
        # Creamos DOS etapas de filtrado por cada eje (Cascada)
        # Eje X
        self.filter_x_stage1 = LowPassFilter()
        self.filter_x_stage2 = LowPassFilter()
        # Eje Y
        self.filter_y_stage1 = LowPassFilter()
        self.filter_y_stage2 = LowPassFilter()
        # Eje Z
        self.filter_z_stage1 = LowPassFilter()
        self.filter_z_stage2 = LowPassFilter()

        self.prev_time = None

        self.subscription = self.create_subscription(
            Imu, '/imu', self.listener_callback, 10)
        self.publisher_ = self.create_publisher(Imu, '/imu_filtered_2nd_order', 10)

        self.get_logger().info('Filtro de 2do Orden Iniciado.')

    def listener_callback(self, msg):
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        
        # Obtenemos la frecuencia deseada
        target_cutoff = self.get_parameter('cutoff_frequency').get_parameter_value().double_value

        # --- CORRECCIÓN DE FRECUENCIA PARA 2DO ORDEN ---
        # Al poner 2 filtros en serie, la frecuencia de corte baja.
        # Para que el corte final sea realmente 'target_cutoff', cada etapa individual
        # debe cortar a una frecuencia más alta.
        # Factor de corrección para 2 etapas: 1 / sqrt(sqrt(2) - 1) ≈ 1.5537
        stage_cutoff = target_cutoff * 1.55377

        # Cálculo de Alpha dinámico (basado en dt)
        if self.prev_time is None:
            dt = 0.008 # Asumimos 8ms para el primer frame
        else:
            dt = current_time - self.prev_time
            if dt <= 0: dt = 0.001

        rc = 1.0 / (2.0 * math.pi * stage_cutoff)
        alpha = dt / (rc + dt)

        # --- PROCESAMIENTO EN CASCADA ---
        
        # Eje X: Crudo -> Etapa 1 -> Etapa 2 -> Salida
        x_st1 = self.filter_x_stage1.update(msg.linear_acceleration.x, alpha)
        x_final = self.filter_x_stage2.update(x_st1, alpha)

        # Eje Y
        y_st1 = self.filter_y_stage1.update(msg.linear_acceleration.y, alpha)
        y_final = self.filter_y_stage2.update(y_st1, alpha)

        # Eje Z
        z_st1 = self.filter_z_stage1.update(msg.linear_acceleration.z, alpha)
        z_final = self.filter_z_stage2.update(z_st1, alpha)

        # Actualizamos tiempo
        self.prev_time = current_time

        # Publicar
        out_msg = msg
        out_msg.linear_acceleration.x = x_final
        out_msg.linear_acceleration.y = y_final
        out_msg.linear_acceleration.z = z_final
        
        self.publisher_.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuSecondOrderFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
