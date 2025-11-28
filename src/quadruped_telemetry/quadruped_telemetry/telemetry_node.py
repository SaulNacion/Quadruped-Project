#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
from champ_msgs.msg import ContactsStamped
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist


class TelemetryNode(Node):
    def __init__(self):
        super().__init__('telemetry_node')

        self.base_ns = '/telemetry'

        # Nombres de juntas por pata (3 por pata, sin 'foot')
        self.joint_names = {
            'lf': ['lf_hip_joint', 'lf_upper_leg_joint', 'lf_lower_leg_joint'],
            'rf': ['rf_hip_joint', 'rf_upper_leg_joint', 'rf_lower_leg_joint'],
            'lh': ['lh_hip_joint', 'lh_upper_leg_joint', 'lh_lower_leg_joint'],
            'rh': ['rh_hip_joint', 'rh_upper_leg_joint', 'rh_lower_leg_joint']
        }

        # Almacenamiento de datos
        self.current_positions = {}
        self.target_positions = {}
        self.current_velocities = {}
        self.target_velocities = {}
        self.foot_contacts = {}
        self.cmd_vel = {'linear_x': 0.0, 'linear_y': 0.0, 'angular_z': 0.0}

        # === Suscriptores ===
        self.joint_states_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )

        self.joint_trajectory_sub = self.create_subscription(
            JointTrajectory,
            '/joint_group_effort_controller/joint_trajectory',
            self.joint_trajectory_callback,
            10
        )

        self.foot_contacts_sub = self.create_subscription(
            ContactsStamped,
            '/foot_contacts',
            self.foot_contacts_callback,
            10
        )

        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # === Publicadores para PlotJuggler (telemetría) ===
        self.telemetry_publishers = {}

        # Publicadores por pata y articulación
        for leg_name, joints in self.joint_names.items():
            for i, joint_name in enumerate(joints):
                joint_short = ['hip', 'upper', 'lower'][i]

                # Base del tópico para esa articulación
                topic_base = f'{self.base_ns}/{leg_name}/{joint_short}'

                # Posición
                self.telemetry_publishers[f'{leg_name}_{joint_short}_pos_current'] = self.create_publisher(
                    Float64, f'{topic_base}/position/current', 10)
                self.telemetry_publishers[f'{leg_name}_{joint_short}_pos_target'] = self.create_publisher(
                    Float64, f'{topic_base}/position/target', 10)
                self.telemetry_publishers[f'{leg_name}_{joint_short}_pos_error'] = self.create_publisher(
                    Float64, f'{topic_base}/position/error', 10)

                # Velocidad
                self.telemetry_publishers[f'{leg_name}_{joint_short}_vel_current'] = self.create_publisher(
                    Float64, f'{topic_base}/velocity/current', 10)
                self.telemetry_publishers[f'{leg_name}_{joint_short}_vel_target'] = self.create_publisher(
                    Float64, f'{topic_base}/velocity/target', 10)
                self.telemetry_publishers[f'{leg_name}_{joint_short}_vel_error'] = self.create_publisher(
                    Float64, f'{topic_base}/velocity/error', 10)

        # Contacto de pata
        for leg_name in self.joint_names.keys():
            topic = f'{self.base_ns}/{leg_name}/foot_contact'
            self.telemetry_publishers[f'{leg_name}_contact'] = self.create_publisher(
                Float64, topic, 10)

        # Cmd vel
        self.telemetry_publishers['cmd_vel_linear_x'] = self.create_publisher(
            Float64, f'{self.base_ns}/cmd_vel/linear_x', 10)
        self.telemetry_publishers['cmd_vel_linear_y'] = self.create_publisher(
            Float64, f'{self.base_ns}/cmd_vel/linear_y', 10)
        self.telemetry_publishers['cmd_vel_angular_z'] = self.create_publisher(
            Float64, f'{self.base_ns}/cmd_vel/angular_z', 10)

        # Timer de publicación (100 Hz)
        self.timer = self.create_timer(0.01, self.publish_telemetry)

        self.get_logger().info('Telemetry Node initialized')
        self.get_logger().info(
            f'Publishing telemetry data for legs: {list(self.joint_names.keys())}'
        )

    # ==================
    #   Callbacks
    # ==================

    def joint_states_callback(self, msg: JointState):
        """Guardar estados actuales de las juntas."""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.current_positions[name] = msg.position[i]
            if i < len(msg.velocity):
                self.current_velocities[name] = msg.velocity[i]

    def joint_trajectory_callback(self, msg: JointTrajectory):
        """Guardar posiciones/velocidades objetivo de los comandos de trayectoria."""
        if len(msg.points) > 0:
            point = msg.points[0]  # primer punto de la trayectoria
            for i, name in enumerate(msg.joint_names):
                if i < len(point.positions):
                    self.target_positions[name] = point.positions[i]
                if i < len(point.velocities):
                    self.target_velocities[name] = point.velocities[i]

    def foot_contacts_callback(self, msg: ContactsStamped):
        """Guardar información de contacto de cada pata."""
        leg_names = ['lf', 'rf', 'lh', 'rh']
        for i, contact in enumerate(msg.contacts):
            if i < len(leg_names):
                # convertir a float (0.0 o 1.0 típicamente)
                self.foot_contacts[leg_names[i]] = float(contact)

    def cmd_vel_callback(self, msg: Twist):
        """Guardar comando de velocidad."""
        self.cmd_vel['linear_x'] = msg.linear.x
        self.cmd_vel['linear_y'] = msg.linear.y
        self.cmd_vel['angular_z'] = msg.angular.z

    # ==================
    #   Publicación
    # ==================

    def publish_telemetry(self):
        """Publicar todas las señales de telemetría para PlotJuggler."""
        # current_time = self.get_clock().now()  # Si algún día quieres time stamping, ya lo tienes

        for leg_name, joints in self.joint_names.items():
            for i, joint_name in enumerate(joints):
                joint_short = ['hip', 'upper', 'lower'][i]

                # Valores actuales y objetivo
                current_pos = self.current_positions.get(joint_name, 0.0)
                target_pos = self.target_positions.get(joint_name, 0.0)
                current_vel = self.current_velocities.get(joint_name, 0.0)
                target_vel = self.target_velocities.get(joint_name, 0.0)

                # Errores
                pos_error = target_pos - current_pos
                vel_error = target_vel - current_vel

                # Publicar posición
                self.publish_float64(f'{leg_name}_{joint_short}_pos_current', current_pos)
                self.publish_float64(f'{leg_name}_{joint_short}_pos_target', target_pos)
                self.publish_float64(f'{leg_name}_{joint_short}_pos_error', pos_error)

                # Publicar velocidad
                self.publish_float64(f'{leg_name}_{joint_short}_vel_current', current_vel)
                self.publish_float64(f'{leg_name}_{joint_short}_vel_target', target_vel)
                self.publish_float64(f'{leg_name}_{joint_short}_vel_error', vel_error)

        # Contactos de pie
        for leg_name in self.joint_names.keys():
            contact = self.foot_contacts.get(leg_name, 0.0)
            self.publish_float64(f'{leg_name}_contact', contact)

        # Cmd vel
        self.publish_float64('cmd_vel_linear_x', self.cmd_vel['linear_x'])
        self.publish_float64('cmd_vel_linear_y', self.cmd_vel['linear_y'])
        self.publish_float64('cmd_vel_angular_z', self.cmd_vel['angular_z'])

    def publish_float64(self, key: str, value: float):
        """Helper para publicar Float64 en el tópico asociado a `key`."""
        pub = self.telemetry_publishers.get(key, None)
        if pub is not None:
            msg = Float64()
            msg.data = float(value)
            pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TelemetryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
