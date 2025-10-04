// Incluye el registro de plugins de Gazebo
#include <gz/plugin/Register.hh>

// Incluye la clase base System de Gazebo
#include <gz/sim/System.hh>

// Incluye el nodo de transporte para comunicación entre topics
#include <gz/transport/Node.hh>

// Mensajes para recibir información del reloj de simulación
#include <gz/msgs/clock.pb.h>

// Librería estándar para salida por consola
#include <iostream>

// Mensajes para publicar datos tipo double
#include <gz/msgs/double.pb.h>

#include <cstdlib>  // para std::getenv

// Definición de la clase GazPublisher que hereda de System
// e implementa la interfaz ISystemConfigure
class GazPublisher : public gz::sim::System,
                     public gz::sim::ISystemConfigure
{
public:
    // Método de configuración del sistema llamado al iniciar la simulación
    void Configure(const gz::sim::Entity& /*_entity*/,
                   const std::shared_ptr<const sdf::Element>& /*_sdf*/,
                   gz::sim::EntityComponentManager& /*_ecm*/,
                   gz::sim::EventManager& /*_eventMgr*/) override
    {
        // Crear un nodo de transporte para publicar y suscribirse a topics
        node = std::make_unique<gz::transport::Node>();

         // Leer variable de entorno WORLD_NAME (la defines en tu launch file)
        const char* worldEnv = std::getenv("WORLD_NAME");
        if (worldEnv == nullptr)
        {
            std::cerr << "[GazPublisher] ERROR: WORLD_NAME not defined." << std::endl;
            return; // Stopping configuration
        }        
        std::string worldName(worldEnv);
        std::string clockTopic = "/world/" + worldName + "/clock";

        // Suscribirse al tópico del reloj de la simulación
        if (!node->Subscribe(clockTopic, &GazPublisher::OnClock, this))
        {
            std::cerr << "Error al suscribirse al tópico [" << clockTopic << "]" << std::endl;        
        }

        // Anunciar un nuevo tópico para publicar valores tipo double
        this->pub = this->node->Advertise<gz::msgs::Double>("/nivel_de_gaz");
        if (!this->pub)
        {
            std::cerr << "Error al anunciar el tópico [/nivel_de_gaz]" << std::endl;
        }
    }

private:
    // Callback que se ejecuta cada vez que llega un mensaje del reloj
    void OnClock(const gz::msgs::Clock& _msg)
    {
        // Obtener el tiempo de simulación en segundos (sumando segundos y nanosegundos)
        double time_in_seconds = _msg.sim().sec() + _msg.sim().nsec() / 1e9;

        // Definir una función lineal del tiempo
        double linear_function_output = 2.0 * time_in_seconds;

        // Crear un mensaje tipo double y asignarle el valor calculado
        gz::msgs::Double msg;
        msg.set_data(linear_function_output);

        // Publicar el mensaje en el tópico
        this->pub.Publish(msg);
    }

    // Nodo de transporte único para comunicación con Gazebo
    std::unique_ptr<gz::transport::Node> node;

    // Publicador de mensajes tipo double
    gz::transport::Node::Publisher pub;
};

// Registro del plugin en Gazebo
GZ_ADD_PLUGIN(
    GazPublisher,                  // Nombre de la clase del plugin
    gz::sim::System,               // Clase base del sistema
    GazPublisher::ISystemConfigure // Interfaz implementada
)
