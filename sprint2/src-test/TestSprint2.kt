package test.kotlin

import org.junit.Before
import org.junit.After
import org.junit.BeforeClass
import org.junit.AfterClass
import org.junit.Test
import org.junit.Assert.*
import unibo.basicomm23.interfaces.IApplMessage
import unibo.basicomm23.interfaces.Interaction
import unibo.basicomm23.utils.CommUtils
import unibo.basicomm23.utils.ConnectionFactory
import unibo.basicomm23.msg.ProtocolType
import java.net.ServerSocket
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.PrintWriter
import kotlin.concurrent.thread

class TestSprint2 {

    companion object {
        private var serverSocket: ServerSocket? = null
        private var mockRobotThread: Thread? = null

        @JvmStatic
        @BeforeClass
        fun setupClass() {
            // 1. Start Mock Robot Server on port 8020 to handle cargorobot requests
            startMockRobot()

            // 2. Start QAK Contexts
            thread {
                it.unibo.ctx_cargoservice.main()
            }
            thread {
                it.unibo.ctx_gui.main()
            }
            thread {
                it.unibo.ctx_picow.main()
            }

            // Wait for QAK contexts to boot
            CommUtils.delay(4000)
        }

        @JvmStatic
        @AfterClass
        fun tearDownClass() {
            serverSocket?.close()
            // Force JVM shutdown to cleanly terminate background QAK threads and exit
            System.exit(0)
        }

        private fun startMockRobot() {
            try {
                serverSocket = ServerSocket(8020)
                mockRobotThread = thread {
                    try {
                        while (true) {
                            val client = serverSocket?.accept() ?: break
                            thread {
                                try {
                                    val reader = BufferedReader(InputStreamReader(client.getInputStream()))
                                    val writer = PrintWriter(client.getOutputStream(), true)
                                    var line: String?
                                    while (reader.readLine().also { line = it } != null) {
                                        CommUtils.outgreen("MockRobot received: $line")
                                        if (line!!.contains("moverobot")) {
                                            // Extract message sequence number to construct a valid QAK reply
                                            val parts = line!!.split(",")
                                            if (parts.size >= 6) {
                                                val msgNum = parts.last().replace(")", "").trim()
                                                val reply = "msg(moverobotdone,reply,robotsmart,cargorobot,moverobotdone(ok),$msgNum)\n"
                                                CommUtils.outgreen("MockRobot replying: $reply")
                                                writer.print(reply)
                                                writer.flush()
                                            }
                                        }
                                    }
                                } catch (e: Exception) {
                                    // Client disconnected
                                }
                            }
                        }
                    } catch (e: Exception) {
                        // Server stopped
                    }
                }
            } catch (e: Exception) {
                CommUtils.outred("Failed to start Mock Robot: ${e.message}")
            }
        }
    }

    private var conn: Interaction? = null

    @Before
    fun setUp() {
        // Establish TCP connection to cargoservice context (port 8082)
        conn = ConnectionFactory.createClientSupport23(ProtocolType.tcp, "localhost", "8082")
    }

    @After
    fun tearDown() {
        conn?.close()
    }

    @Test
    fun testHappyPath() {
        CommUtils.outblue("--- Starting Test: testHappyPath ---")
        try {
            // 1. Send load request
            val requestMsg = CommUtils.buildRequest("testclient", "load", "load(client1)", "cargoservice")
            CommUtils.outblue("Sending load request: $requestMsg")
            val reply = conn?.request(requestMsg)
            CommUtils.outblue("Received reply: $reply")

            // Verify reply is reserved(slot1)
            assertNotNull(reply)
            assertTrue(reply!!.msgContent().contains("reserved"))
            assertTrue(reply.msgContent().contains("slot1"))

            // 2. Simulate container arrival by sending distance(2) to cargoservice
            val sonarMsg = CommUtils.buildDispatch("testclient", "distance", "distance(2)", "cargoservice")
            CommUtils.outblue("Simulating container arrival: $sonarMsg")
            conn?.forward(sonarMsg)

            // 3. Wait for the cargoservice and cargorobot to complete movement sequence (home -> ioport -> slot5 -> slot1 -> home)
            CommUtils.delay(12000)

            // 4. Send another load request, verify slot1 is occupied so it assigns slot2
            val requestMsg2 = CommUtils.buildRequest("testclient", "load", "load(client2)", "cargoservice")
            CommUtils.outblue("Sending second load request: $requestMsg2")
            val reply2 = conn?.request(requestMsg2)
            CommUtils.outblue("Received reply: $reply2")

            assertNotNull(reply2)
            assertTrue(reply2!!.msgContent().contains("reserved"))
            assertTrue(reply2.msgContent().contains("slot2"))

        } catch (e: Exception) {
            fail("Test failed with exception: ${e.message}")
        }
    }

    @Test
    fun testOutOfService() {
        CommUtils.outblue("--- Starting Test: testOutOfService ---")
        try {
            // 1. Simulate a sonar failure event sent to cargoservice
            val sonarFailMsg = CommUtils.buildDispatch("testclient", "sonar_fail", "sonar_fail(30)", "cargoservice")
            CommUtils.outblue("Simulating sonar failure: $sonarFailMsg")
            conn?.forward(sonarFailMsg)
            CommUtils.delay(500)

            // 2. Try sending a load request, should reply with retrylater(busy_or_out_of_service)
            val requestMsg = CommUtils.buildRequest("testclient", "load", "load(client3)", "cargoservice")
            CommUtils.outblue("Sending load request during failure: $requestMsg")
            val reply = conn?.request(requestMsg)
            CommUtils.outblue("Received reply: $reply")

            assertNotNull(reply)
            assertTrue(reply!!.msgContent().contains("retrylater"))

            // 3. Recover the sonar failure
            val sonarOkMsg = CommUtils.buildDispatch("testclient", "sonar_ok", "sonar_ok(2)", "cargoservice")
            CommUtils.outblue("Simulating sonar recovery: $sonarOkMsg")
            conn?.forward(sonarOkMsg)
            CommUtils.delay(500)

            // 4. Verify system is working again by requesting a load (should assign next free slot, slot3 since 1 and 2 were occupied in previous test)
            val requestMsg2 = CommUtils.buildRequest("testclient", "load", "load(client4)", "cargoservice")
            CommUtils.outblue("Sending load request after recovery: $requestMsg2")
            val reply2 = conn?.request(requestMsg2)
            CommUtils.outblue("Received reply: $reply2")

            assertNotNull(reply2)
            assertTrue(reply2!!.msgContent().contains("reserved"))

        } catch (e: Exception) {
            fail("Test failed with exception: ${e.message}")
        }
    }
}
