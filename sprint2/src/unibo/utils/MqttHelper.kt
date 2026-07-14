package unibo.utils

import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence

class MqttHelper(private val brokerUrl: String, clientId: String) {
    private var client: MqttClient = MqttClient(brokerUrl, clientId, MemoryPersistence())

    fun connect() {
        val options = MqttConnectOptions()
        options.isCleanSession = true
        options.connectionTimeout = 10
        options.keepAliveInterval = 20
        try {
            client.connect(options)
            println("MqttHelper | Connected to broker: $brokerUrl")
        } catch (e: Exception) {
            println("MqttHelper | Connection failed: ${e.message}")
        }
    }

    fun publish(topic: String, payload: String, qos: Int = 1) {
        if (!client.isConnected) {
            println("MqttHelper | Not connected. Attempting reconnect...")
            connect()
        }
        try {
            val message = MqttMessage(payload.toByteArray())
            message.qos = qos
            client.publish(topic, message)
        } catch (e: Exception) {
            println("MqttHelper | Publish failed: ${e.message}")
        }
    }

    fun subscribe(topic: String, callback: (String) -> Unit) {
        if (!client.isConnected) {
            connect()
        }
        try {
            client.subscribe(topic) { _, message ->
                val payload = String(message.payload)
                callback(payload)
            }
            println("MqttHelper | Subscribed to topic: $topic")
        } catch (e: Exception) {
            println("MqttHelper | Subscription failed: ${e.message}")
        }
    }

    fun disconnect() {
        try {
            if (client.isConnected) {
                client.disconnect()
            }
        } catch (e: Exception) {
            println("MqttHelper | Disconnect failed: ${e.message}")
        }
    }
}
