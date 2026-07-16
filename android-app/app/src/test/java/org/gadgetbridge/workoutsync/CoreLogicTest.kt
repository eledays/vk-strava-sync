package org.gadgetbridge.workoutsync

import org.gadgetbridge.workoutsync.data.*
import org.gadgetbridge.workoutsync.sync.*
import org.junit.Assert.*
import org.junit.Test
import java.io.ByteArrayInputStream
import java.net.UnknownHostException

class CoreLogicTest {
    @Test fun sha256IsStreamingAndCorrect() { assertEquals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",Sha256Calculator.calculate(ByteArrayInputStream("abc".toByteArray()))) }
    @Test fun extensionsAreCaseInsensitive() { assertTrue(WorkoutFileFilter.supports("run.FIT")); assertTrue(WorkoutFileFilter.supports("x.gPx")); assertFalse(WorkoutFileFilter.supports("x.fit.tmp")) }
    @Test fun httpClassification() { assertEquals(ErrorKind.RETRY,NetworkErrorClassifier.http(429).kind); assertEquals(ErrorKind.RETRY,NetworkErrorClassifier.http(500).kind); assertEquals(ErrorKind.PERMANENT,NetworkErrorClassifier.http(401).kind); assertEquals(ErrorKind.PERMANENT,NetworkErrorClassifier.http(413).kind) }
    @Test fun networkExceptionRetries() { assertEquals(ErrorKind.RETRY,NetworkErrorClassifier.exception(UnknownHostException()).kind) }
    @Test fun duplicateRequiresMachineReadableStatus() { val accepted=UploadResponse("already_processed"); assertEquals("already_processed",accepted.status); assertNotEquals("already_processed",UploadResponse("conflict").status) }
    @Test fun workerPolicy() { assertEquals("retry",WorkerResultPolicy.result(true,false,true)); assertEquals("failure",WorkerResultPolicy.result(false,false,false)); assertEquals("success",WorkerResultPolicy.result(true,false,false)) }
    @Test fun intervalsRespectWorkManagerMinimum() { assertTrue(SyncScheduler.intervals.all { it>=15 }); assertEquals(60L,SyncScheduler.intervals[2]) }
    @Test fun validatesUrls() { assertNull(UrlValidator.error("https://example.org",false)); assertNotNull(UrlValidator.error("http://example.org",false)); assertNotNull(UrlValidator.error("https://example.org/?token=x",false)); assertNull(UrlValidator.error("http://10.0.2.2:8080",true)) }
}
