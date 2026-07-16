package org.gadgetbridge.workoutsync

import android.Manifest
import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.*
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import org.gadgetbridge.workoutsync.data.*
import org.gadgetbridge.workoutsync.sync.SyncScheduler
import java.text.DateFormat
import java.util.Date

class MainActivity:ComponentActivity() {
    override fun onCreate(savedInstanceState:Bundle?) { super.onCreate(savedInstanceState); setContent { MaterialTheme { WorkoutSyncUi(application as WorkoutSyncApp) } } }
}

data class HomeState(val settings:Settings=Settings(),val files:List<WorkoutFileEntity> = emptyList(),val pending:Int=0,val uploaded:Int=0,val errors:Int=0)
class MainViewModel(private val app:WorkoutSyncApp):ViewModel() {
    private val dao=app.db.workoutFiles()
    val state=combine(app.settings.settings,dao.recent(),dao.pendingCount(),dao.uploadedCount(),dao.errorCount()) { s,f,p,u,e -> HomeState(s,f,p,u,e) }.stateIn(viewModelScope,SharingStarted.WhileSubscribed(5_000),HomeState())
    fun save(settings:Settings) { viewModelScope.launch { app.settings.save(settings); SyncScheduler.configure(app,settings.automatic,settings.intervalMinutes) } }
    fun sync()=SyncScheduler.manual(app)
    fun retry(id:Long) { viewModelScope.launch { dao.requeue(id); sync() } }
}

@Composable private fun WorkoutSyncUi(app:WorkoutSyncApp) {
    val vm:MainViewModel= androidx.lifecycle.viewmodel.compose.viewModel(factory=object:ViewModelProvider.Factory { override fun <T:ViewModel> create(modelClass:Class<T>):T { @Suppress("UNCHECKED_CAST") return MainViewModel(app) as T } })
    val state by vm.state.collectAsStateWithLifecycle(); var settingsScreen by remember { mutableStateOf(!state.settings.configured) }
    val permission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){}
    LaunchedEffect(Unit) { if(Build.VERSION.SDK_INT>=33) permission.launch(Manifest.permission.POST_NOTIFICATIONS) }
    if(settingsScreen) SettingsScreen(state.settings,onSave={ vm.save(it); settingsScreen=false },onBack={settingsScreen=false})
    else HomeScreen(state,onSettings={settingsScreen=true},onSync=vm::sync,onRetry=vm::retry)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable private fun SettingsScreen(initial:Settings,onSave:(Settings)->Unit,onBack:()->Unit) {
    var folder by remember(initial.folderUri){mutableStateOf(initial.folderUri)}; var url by remember(initial.baseUrl){mutableStateOf(initial.baseUrl)}; var token by remember(initial.token){mutableStateOf(initial.token)}
    var automatic by remember(initial.automatic){mutableStateOf(initial.automatic)}; var interval by remember(initial.intervalMinutes){mutableLongStateOf(initial.intervalMinutes)}; var expanded by remember{mutableStateOf(false)}; var error by remember{mutableStateOf<String?>(null)}
    val context=LocalContext.current
    val launcher=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri -> uri?.let { runCatching { context.contentResolver.takePersistableUriPermission(it,Intent.FLAG_GRANT_READ_URI_PERMISSION) }; folder=it.toString() } }
    Scaffold(topBar={TopAppBar(title={Text("Настройки")},navigationIcon={TextButton(onClick=onBack){Text("Назад")}})}) { padding ->
        LazyColumn(Modifier.padding(padding).padding(16.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
            item { Text(if(folder.isBlank()) "Папка не выбрана" else folder,maxLines=2); Button(onClick={launcher.launch(null)}){Text("Выбрать папку")} }
            item { OutlinedTextField(url,{url=it},label={Text("URL сервера")},singleLine=true,modifier=Modifier.fillMaxWidth()) }
            item { OutlinedTextField(token,{token=it},label={Text("Токен")},visualTransformation=PasswordVisualTransformation(),singleLine=true,modifier=Modifier.fillMaxWidth()) }
            item { Row { Text("Автоматическая синхронизация",Modifier.weight(1f)); Switch(automatic,{automatic=it}) } }
            item { ExposedDropdownMenuBox(expanded,{expanded=!expanded}) { OutlinedTextField("$interval мин",{},readOnly=true,label={Text("Интервал")},modifier=Modifier.menuAnchor().fillMaxWidth()); ExposedDropdownMenu(expanded,{expanded=false}) { SyncScheduler.intervals.forEach { DropdownMenuItem({Text(if(it<60)"$it минут" else "${it/60} ч")},{interval=it;expanded=false}) } } } }
            item { Text("Android запускает фоновую синхронизацию приблизительно; точная минута не гарантируется.",style=MaterialTheme.typography.bodySmall) }
            error?.let { item { Text(it,color=MaterialTheme.colorScheme.error) } }
            item { Button(onClick={ error=when { folder.isBlank()->"Выберите папку"; token.isBlank()->"Введите токен"; else->UrlValidator.error(url,BuildConfig.ALLOW_LOCAL_HTTP) }; if(error==null)onSave(Settings(folder,url,token,automatic,interval,initial.lastAttempt,initial.lastSuccess,initial.lastResult)) },modifier=Modifier.fillMaxWidth()){Text("Сохранить")} }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable private fun HomeScreen(state:HomeState,onSettings:()->Unit,onSync:()->Unit,onRetry:(Long)->Unit) {
    var detail by remember{mutableStateOf<WorkoutFileEntity?>(null)}
    Scaffold(topBar={TopAppBar(title={Text("Тренировки")},actions={TextButton(onClick=onSettings){Text("Настройки")}})}) { padding -> LazyColumn(Modifier.padding(padding).padding(horizontal=16.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
        item { Card(Modifier.fillMaxWidth()){Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(5.dp)){Text(state.settings.baseUrl); Text("Автосинхронизация: ${if(state.settings.automatic)"включена" else "выключена"}"); Text("Ожидают: ${state.pending} · Загружено: ${state.uploaded} · Ошибки: ${state.errors}"); Text("Последняя попытка: ${date(state.settings.lastAttempt)}"); Text("Последний успех: ${date(state.settings.lastSuccess)}"); Text(state.settings.lastResult); Button(onClick=onSync,enabled=state.settings.configured,modifier=Modifier.fillMaxWidth()){Text("Синхронизировать сейчас")}}} }
        item { Text("Последние файлы",style=MaterialTheme.typography.titleMedium) }
        items(state.files,key={it.id}) { file -> Card(Modifier.fillMaxWidth().clickable{detail=file}) { Column(Modifier.padding(12.dp)){Text(file.fileName); Text(statusText(file.status)); Text(if(file.status==SyncStatus.UPLOADED)"Загружен: ${date(file.uploadedAt)}" else file.lastError?:"Обнаружен: ${date(file.discoveredAt)}",style=MaterialTheme.typography.bodySmall); if(file.status==SyncStatus.PERMANENT_ERROR)TextButton(onClick={onRetry(file.id)}){Text("Повторить")}} } }
    } }
    detail?.let { f -> AlertDialog(onDismissRequest={detail=null},confirmButton={TextButton(onClick={detail=null}){Text("Закрыть")}},title={Text(f.fileName)},text={Text("Статус: ${statusText(f.status)}\nURI: ${f.uri}\nРазмер: ${f.sizeBytes?:"?"}\nSHA-256: ${f.sha256}\nПопыток: ${f.attempts}\nHTTP: ${f.lastHttpCode?:"—"}\nОшибка: ${f.lastError?:"—"}")}) }
}

private fun date(value:Long?)=value?.let { DateFormat.getDateTimeInstance().format(Date(it)) }?:"—"
private fun statusText(s:SyncStatus)=when(s){SyncStatus.PENDING->"Ожидает";SyncStatus.UPLOADING->"Отправляется";SyncStatus.UPLOADED->"Загружен";SyncStatus.RETRY_REQUIRED->"Будет повторено";SyncStatus.PERMANENT_ERROR->"Ошибка"}
