package unibo.utils

import it.unibo.kactor.MsgUtil
import it.unibo.kactor.sysUtil
import kotlinx.coroutines.runBlocking

object QakHelper {
    fun sendDispatch(sender: String, msgId: String, payload: String, receiver: String) {
        try {
            val msg = MsgUtil.buildDispatch(sender, msgId, "$msgId($payload)", receiver)
            val actor = sysUtil.getActor(receiver)
            if (actor != null) {
                runBlocking {
                    MsgUtil.sendMsg(msg, actor)
                }
            } else {
                println("QakHelper | Actor $receiver not found")
            }
        } catch (e: Exception) {
            println("QakHelper | Error sending dispatch: ${e.message}")
        }
    }
}
