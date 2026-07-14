package unibo.ioport

import com.sun.net.httpserver.HttpServer
import com.sun.net.httpserver.HttpHandler
import com.sun.net.httpserver.HttpExchange
import java.net.InetSocketAddress
import java.io.File
import org.eclipse.californium.core.CoapClient
import org.eclipse.californium.core.coap.MediaTypeRegistry
import it.unibo.kactor.MsgUtil
import unibo.basicomm23.coap.CoapConnection

class IOPortWebServer(private val port: Int) {
    private var server: HttpServer? = null

    fun start() {
        try {
            // Start HTTP Server
            server = HttpServer.create(InetSocketAddress(port), 0)
            server?.createContext("/", StaticFileHandler())
            server?.createContext("/status", StatusHandler())
            server?.createContext("/load", LoadHandler())
            server?.executor = java.util.concurrent.Executors.newCachedThreadPool()
            server?.start()
            println("IOPortWebServer | Server started on port $port")
        } catch (e: Exception) {
            println("IOPortWebServer | Error starting server: ${e.message}")
        }
    }

    fun stop() {
        server?.stop(0)
    }

    private inner class StaticFileHandler : HttpHandler {
        override fun handle(exchange: HttpExchange) {
            val path = exchange.requestURI.path
            val filePath = if (path == "/" || path.isEmpty()) "userDocs/webgui/index.html" else "userDocs/webgui$path"
            val file = File(filePath)
            if (file.exists() && !file.isDirectory) {
                val bytes = file.readBytes()
                val mimeType = when {
                    filePath.endsWith(".html") -> "text/html"
                    filePath.endsWith(".js") -> "application/javascript"
                    filePath.endsWith(".css") -> "text/css"
                    else -> "text/plain"
                }
                exchange.responseHeaders.set("Content-Type", mimeType)
                exchange.sendResponseHeaders(200, bytes.size.toLong())
                exchange.responseBody.write(bytes)
            } else {
                val errorMsg = "File not found: $filePath"
                exchange.sendResponseHeaders(404, errorMsg.length.toLong())
                exchange.responseBody.write(errorMsg.toByteArray())
            }
            exchange.close()
        }
    }

    private inner class StatusHandler : HttpHandler {
        override fun handle(exchange: HttpExchange) {
            exchange.responseHeaders.set("Access-Control-Allow-Origin", "*")
            exchange.responseHeaders.set("Content-Type", "application/json")
            
            var responseText = "state(false,false,false,false,false,,false)"
            try {
                // Fetch state via CoAP on-demand to avoid startup race conditions
                val client = CoapClient("coap://localhost:8082/ctx_cargoservice/cargoservice")
                client.timeout = 1000 // 1 second timeout
                val response = client.get()
                if (response != null && response.responseText.isNotEmpty()) {
                    responseText = response.responseText
                }
            } catch (e: Exception) {
                // Fallback to default state if CoAP server is not yet online
            }
            
            val bytes = responseText.toByteArray()
            exchange.sendResponseHeaders(200, bytes.size.toLong())
            exchange.responseBody.write(bytes)
            exchange.close()
        }
    }

    private inner class LoadHandler : HttpHandler {
        override fun handle(exchange: HttpExchange) {
            exchange.responseHeaders.set("Content-Type", "application/json")
            exchange.responseHeaders.set("Access-Control-Allow-Origin", "*")
            
            if (exchange.requestMethod.equals("POST", ignoreCase = true)) {
                try {
                    // Send load request via CoAP using ConnToCoap
                    val conn = CoapConnection("localhost:8082", "ctx_cargoservice/cargoservice")
                    val msg = MsgUtil.buildRequest("gui", "load", "load(client1)", "cargoservice")
                    println("IOPortWebServer | GUI EMETTE UNA LOAD: Requesting slot reservation for client...")
                    println("IOPortWebServer | Sending load request: $msg")
                    val reply = conn.request(msg.toString())
                    println("IOPortWebServer | Received reply: $reply")
                    
                    val responseBytes = reply.toByteArray()
                    exchange.sendResponseHeaders(200, responseBytes.size.toLong())
                    exchange.responseBody.write(responseBytes)
                } catch (e: Exception) {
                    val error = "{\"error\":\"${e.message}\"}".toByteArray()
                    exchange.sendResponseHeaders(500, error.size.toLong())
                    exchange.responseBody.write(error)
                }
            } else {
                exchange.sendResponseHeaders(405, 0)
            }
            exchange.close()
        }
    }
}
