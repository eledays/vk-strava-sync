plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.ksp)
}

android {
    namespace = "org.gadgetbridge.workoutsync"
    compileSdk = 35
    defaultConfig {
        applicationId = "org.gadgetbridge.workoutsync"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        buildConfigField("boolean", "ALLOW_LOCAL_HTTP", "false")
    }
    buildTypes {
        debug { buildConfigField("boolean", "ALLOW_LOCAL_HTTP", "true") }
        release { isMinifyEnabled = false }
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}

dependencies {
    implementation(libs.androidx.core); implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.runtime); implementation(libs.androidx.lifecycle.viewmodel)
    implementation(platform(libs.compose.bom)); implementation(libs.compose.ui); implementation(libs.compose.ui.preview)
    implementation(libs.compose.material3); implementation(libs.compose.icons); debugImplementation(libs.compose.ui.tooling)
    implementation(libs.navigation.compose); implementation(libs.room.runtime); implementation(libs.room.ktx)
    ksp(libs.room.compiler); implementation(libs.work.runtime); implementation(libs.datastore)
    implementation(libs.documentfile); implementation(libs.retrofit); implementation(libs.okhttp)
    implementation(libs.serialization.json)
    testImplementation(libs.junit); testImplementation(libs.coroutines.test); testImplementation(libs.mockwebserver)
    testImplementation(libs.room.testing); testImplementation(libs.work.testing)
    androidTestImplementation(libs.androidx.junit); androidTestImplementation(libs.espresso)
    androidTestImplementation(platform(libs.compose.bom)); androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}
