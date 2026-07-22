# === ZenAndroid App Creator ===
# Run this in PowerShell

$root = "$env:USERPROFILE\OneDrive\Documents\opencode_work\ZenAndroidApp"

# Create directory structure
$dirs = @(
    "$root\app\src\main\java\com\example\zenandroid",
    "$root\app\src\main\res\layout",
    "$root\app\src\main\res\values",
    "$root\app\src\main\res\xml",
    "$root\gradle\wrapper"
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }

# build.gradle (root)
@"
buildscript {
    repositories { google(); mavenCentral() }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.5.2'
        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.24'
    }
}
allprojects { repositories { google(); mavenCentral() } }
"@ | Set-Content "$root\build.gradle" -Encoding UTF8

# settings.gradle
@"
rootProject.name = 'ZenAndroid'
include ':app'
"@ | Set-Content "$root\settings.gradle" -Encoding UTF8

# gradle.properties
@"
android.useAndroidX=true
android.enableJetifier=true
"@ | Set-Content "$root\gradle.properties" -Encoding UTF8

# app/build.gradle
@"
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}
android {
    namespace 'com.example.zenandroid'
    compileSdk 34
    defaultConfig {
        applicationId "com.example.zenandroid"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    buildFeatures { viewBinding true }
}
dependencies {
    implementation 'androidx.core:core-ktx:1.13.1'
    implementation 'androidx.appcompat:appcompat:1.7.0'
    implementation 'com.google.android.material:material:1.12.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.google.code.gson:gson:2.11.0'
}
"@ | Set-Content "$root\app\build.gradle" -Encoding UTF8

# AndroidManifest.xml
@"
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-feature android:name="android.hardware.camera" android:required="false"/>
    <application android:allowBackup="true" android:networkSecurityConfig="@xml/network_security_config"
        android:icon="@mipmap/ic_launcher" android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round" android:supportsRtl="true"
        android:theme="@style/Theme.ZenAndroid" tools:targetApi="34">
        <provider android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider" android:exported="false"
            android:grantUriPermissions="true">
            <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths"/>
        </provider>
        <activity android:name=".MainActivity" android:exported="true" android:label="@string/app_name"
            android:theme="@style/Theme.ZenAndroid">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
"@ | Set-Content "$root\app\src\main\AndroidManifest.xml" -Encoding UTF8

# strings.xml
@"
<resources><string name="app_name">Zen Android</string></resources>
"@ | Set-Content "$root\app\src\main\res\values\strings.xml" -Encoding UTF8

# themes.xml
@"
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.ZenAndroid" parent="Theme.Material3.DayNight.NoActionBar">
        <item name="android:statusBarColor">?attr/colorPrimary</item>
    </style>
</resources>
"@ | Set-Content "$root\app\src\main\res\values\themes.xml" -Encoding UTF8

# file_paths.xml
@"
<?xml version="1.0" encoding="utf-8"?>
<paths><external-files-path name="captured" path="captured/"/>
<external-files-path name="sessions" path="sessions/"/></paths>
"@ | Set-Content "$root\app\src\main\res\xml\file_paths.xml" -Encoding UTF8

# network_security_config.xml
@"
<?xml version="1.0" encoding="utf-8"?>
<network-security-config><domain-config cleartextTrafficPermitted="true">
<domain includeSubdomains="true">opencode.ai</domain></domain-config></network-security-config>
"@ | Set-Content "$root\app\src\main\res\xml\network_security_config.xml" -Encoding UTF8

# activity_main.xml
@"
<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="16dp">
        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent" android:layout_height="wrap_content" android:hint="Zen API Key">
            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/apiKeyInput" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:inputType="textPassword"/>
        </com.google.android.material.textfield.TextInputLayout>
        <Button android:id="@+id/saveKeyBtn" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="8dp" android:text="Save Key"/>
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="8dp" android:orientation="horizontal">
            <Button android:id="@+id/cameraBtn" android:layout_width="0dp"
                android:layout_height="wrap_content" android:layout_weight="1" android:text="Camera"/>
            <Button android:id="@+id/galleryBtn" android:layout_width="0dp"
                android:layout_height="wrap_content" android:layout_weight="1" android:text="Gallery"/>
        </LinearLayout>
        <ImageView android:id="@+id/previewImage" android:layout_width="match_parent"
            android:layout_height="160dp" android:layout_marginTop="8dp"
            android:scaleType="centerCrop" android:visibility="gone"/>
        <com.google.android.material.textfield.TextInputLayout
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="16dp" android:hint="Ask about the image...">
            <com.google.android.material.textfield.TextInputEditText
                android:id="@+id/promptInput" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:gravity="top"
                android:inputType="textMultiLine" android:minLines="3"/>
        </com.google.android.material.textfield.TextInputLayout>
        <Spinner android:id="@+id/modelSpinner" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="12dp"/>
        <TextView android:id="@+id/priceLabel" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="4dp"
            android:text="Select a model" android:textSize="12sp"/>
        <Button android:id="@+id/sendBtn" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="12dp" android:text="Send"/>
        <ProgressBar android:id="@+id/progressBar" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="8dp" android:visibility="gone"/>
        <TextView android:id="@+id/responseText" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="16dp"
            android:textIsSelectable="true" android:textSize="14sp"/>
        <Button android:id="@+id/saveSessionBtn" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="12dp" android:text="Save Session"/>
        <TextView android:id="@+id/balanceText" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginTop="12dp"
            android:text="Balance: unknown" android:textSize="12sp"/>
    </LinearLayout>
</ScrollView>
"@ | Set-Content "$root\app\src\main\res\layout\activity_main.xml" -Encoding UTF8

# ZenModel.java
@"
package com.example.zenandroid;
import java.util.ArrayList; import java.util.List;
public class ZenModel {
    public final String displayName, modelId, endpoint;
    public final double input, output;
    public final boolean isFree;
    public ZenModel(String d, String m, String e, double i, double o) {
        displayName=d; modelId=m; endpoint=e; input=i; output=o; isFree=(i==0&&o==0);
    }
    public String priceLabel() { return isFree?"FREE":String.format("in $%.2f / out $%.2f per 1M",input,output); }
    public static List<ZenModel> all() {
        List<ZenModel> l = new ArrayList<>();
        l.add(new ZenModel("Big Pickle","big-pickle","/zen/v1/chat/completions",0,0));
        l.add(new ZenModel("DeepSeek V4 Flash Free","deepseek-v4-flash-free","/zen/v1/chat/completions",0,0));
        l.add(new ZenModel("MiMo-V2.5 Free","mimo-v2.5-free","/zen/v1/chat/completions",0,0));
        l.add(new ZenModel("North Mini Code Free","north-mini-code-free","/zen/v1/chat/completions",0,0));
        l.add(new ZenModel("Nemotron 3 Ultra Free","nemotron-3-ultra-free","/zen/v1/chat/completions",0,0));
        l.add(new ZenModel("GPT 5 Nano","gpt-5-nano","/zen/v1/responses",0.05,0.40));
        l.add(new ZenModel("GPT 5.4 Nano","gpt-5.4-nano","/zen/v1/responses",0.20,1.25));
        l.add(new ZenModel("Gemini 3 Flash","gemini-3-flash","/zen/v1/models/gemini-3-flash",0.50,3.00));
        l.add(new ZenModel("DeepSeek V4 Flash","deepseek-v4-flash","/zen/v1/chat/completions",0.14,0.28));
        l.add(new ZenModel("GPT 5.4 Mini","gpt-5.4-mini","/zen/v1/responses",0.75,4.50));
        l.add(new ZenModel("Qwen3.5 Plus","qwen3.5-plus","/zen/v1/messages",0.20,1.20));
        l.add(new ZenModel("GPT 5.1 Codex Mini","gpt-5.1-codex-mini","/zen/v1/responses",0.25,2.00));
        l.add(new ZenModel("Qwen3.6 Plus","qwen3.6-plus","/zen/v1/messages",0.50,3.00));
        l.add(new ZenModel("Qwen3.7 Plus","qwen3.7-plus","/zen/v1/messages",0.40,1.60));
        l.add(new ZenModel("Kimi K2.5","kimi-k2.5","/zen/v1/chat/completions",0.60,3.00));
        l.add(new ZenModel("MiniMax M2.5","minimax-m2.5","/zen/v1/chat/completions",0.30,1.20));
        l.add(new ZenModel("MiniMax M2.7","minimax-m2.7","/zen/v1/chat/completions",0.30,1.20));
        l.add(new ZenModel("MiniMax M3","minimax-m3","/zen/v1/chat/completions",0.30,1.20));
        l.add(new ZenModel("Claude Haiku 4.5","claude-haiku-4-5","/zen/v1/messages",1.00,5.00));
        l.add(new ZenModel("Grok Build 0.1","grok-build-0.1","/zen/v1/chat/completions",1.00,2.00));
        l.add(new ZenModel("GLM 5","glm-5","/zen/v1/chat/completions",1.00,3.20));
        l.add(new ZenModel("GPT 5","gpt-5","/zen/v1/responses",1.07,8.50));
        l.add(new ZenModel("GPT 5 Codex","gpt-5-codex","/zen/v1/responses",1.07,8.50));
        l.add(new ZenModel("GPT 5.1","gpt-5.1","/zen/v1/responses",1.07,8.50));
        l.add(new ZenModel("GPT 5.1 Codex","gpt-5.1-codex","/zen/v1/responses",1.07,8.50));
        l.add(new ZenModel("Kimi K2.6","kimi-k2.6","/zen/v1/chat/completions",0.95,4.00));
        l.add(new ZenModel("Kimi K2.7 Code","kimi-k2.7-code","/zen/v1/chat/completions",0.95,4.00));
        l.add(new ZenModel("Gemini 3.5 Flash","gemini-3.5-flash","/zen/v1/models/gemini-3.5-flash",1.50,9.00));
        l.add(new ZenModel("GPT 5.2","gpt-5.2","/zen/v1/responses",1.75,14.00));
        l.add(new ZenModel("GPT 5.2 Codex","gpt-5.2-codex","/zen/v1/responses",1.75,14.00));
        l.add(new ZenModel("GPT 5.3 Codex","gpt-5.3-codex","/zen/v1/responses",1.75,14.00));
        l.add(new ZenModel("GPT 5.3 Codex Spark","gpt-5.3-codex-spark","/zen/v1/responses",1.75,14.00));
        l.add(new ZenModel("GLM 5.1","glm-5.1","/zen/v1/chat/completions",1.40,4.40));
        l.add(new ZenModel("GLM 5.2","glm-5.2","/zen/v1/chat/completions",1.40,4.40));
        l.add(new ZenModel("DeepSeek V4 Pro","deepseek-v4-pro","/zen/v1/chat/completions",1.74,3.48));
        l.add(new ZenModel("Claude Sonnet 5","claude-sonnet-5","/zen/v1/messages",2.00,10.00));
        l.add(new ZenModel("Gemini 3.1 Pro (<=200K)","gemini-3.1-pro","/zen/v1/models/gemini-3.1-pro",2.00,12.00));
        l.add(new ZenModel("Qwen3.7 Max","qwen3.7-max","/zen/v1/messages",2.50,7.50));
        l.add(new ZenModel("GPT 5.4 (<=272K)","gpt-5.4","/zen/v1/responses",2.50,15.00));
        l.add(new ZenModel("Claude Sonnet 4.5 (<=200K)","claude-sonnet-4-5","/zen/v1/messages",3.00,15.00));
        l.add(new ZenModel("Claude Sonnet 4.6","claude-sonnet-4-6","/zen/v1/messages",3.00,15.00));
        l.add(new ZenModel("GPT 5.5 (<=272K)","gpt-5.5","/zen/v1/responses",5.00,30.00));
        l.add(new ZenModel("Claude Opus 4.5","claude-opus-4-5","/zen/v1/messages",5.00,25.00));
        l.add(new ZenModel("Claude Opus 4.6","claude-opus-4-6","/zen/v1/messages",5.00,25.00));
        l.add(new ZenModel("Claude Opus 4.7","claude-opus-4-7","/zen/v1/messages",5.00,25.00));
        l.add(new ZenModel("Claude Opus 4.8","claude-opus-4-8","/zen/v1/messages",5.00,25.00));
        l.add(new ZenModel("Gemini 3.1 Pro (>200K)","gemini-3.1-pro","/zen/v1/models/gemini-3.1-pro",4.00,18.00));
        l.add(new ZenModel("GPT 5.4 (>272K)","gpt-5.4","/zen/v1/responses",5.00,22.50));
        l.add(new ZenModel("Claude Sonnet 4.5 (>200K)","claude-sonnet-4-5","/zen/v1/messages",6.00,22.50));
        l.add(new ZenModel("GPT 5.5 (>272K)","gpt-5.5","/zen/v1/responses",10.00,45.00));
        l.add(new ZenModel("Claude Fable 5","claude-fable-5","/zen/v1/messages",10.00,50.00));
        l.add(new ZenModel("GPT 5.4 Pro","gpt-5.4-pro","/zen/v1/responses",30.00,180.00));
        l.add(new ZenModel("GPT 5.5 Pro","gpt-5.5-pro","/zen/v1/responses",30.00,180.00));
        return l;
    }
}
"@ | Set-Content "$root\app\src\main\java\com\example\zenandroid\ZenModel.java" -Encoding UTF8

# ZenClient.java
@"
package com.example.zenandroid;
import android.content.Context; import android.util.Base64;
import org.json.JSONArray; import org.json.JSONException; import org.json.JSONObject;
import java.io.IOException; import java.io.InputStream; import java.util.concurrent.TimeUnit;
import okhttp3.MediaType; import okhttp3.OkHttpClient; import okhttp3.Request; import okhttp3.RequestBody; import okhttp3.Response;
public class ZenClient {
    private static final String BASE = "https://opencode.ai";
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    private final OkHttpClient http; private String apiKey;
    public ZenClient() { http = new OkHttpClient.Builder().connectTimeout(60,TimeUnit.SECONDS)
        .writeTimeout(60,TimeUnit.SECONDS).readTimeout(180,TimeUnit.SECONDS).build(); }
    public void setApiKey(String k) { apiKey = k; }
    public boolean hasKey() { return apiKey != null && !apiKey.trim().isEmpty(); }
    public static String encodeImage(Context ctx, android.net.Uri uri) throws IOException {
        try (InputStream is = ctx.getContentResolver().openInputStream(uri)) {
            if (is == null) throw new IOException("cannot open image");
            java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
            byte[] buf = new byte[8192]; int n; while ((n = is.read(buf)) != -1) bos.write(buf, 0, n);
            return "data:image/jpeg;base64," + Base64.encodeToString(bos.toByteArray(), Base64.NO_WRAP); } }
    public String complete(ZenModel model, String prompt, String img) throws IOException {
        if (!hasKey()) throw new IOException("No API key");
        JSONObject p = buildPayload(model, prompt, img);
        Request req = new Request.Builder().url(BASE + model.endpoint)
            .addHeader("Authorization", "Bearer " + apiKey).addHeader("Content-Type", "application/json")
            .post(RequestBody.create(p.toString(), JSON)).build();
        try (Response resp = http.newCall(req).execute()) {
            String body = resp.body() != null ? resp.body().string() : "";
            if (!resp.isSuccessful()) throw new IOException("HTTP " + resp.code() + ": " + body);
            return extractText(body); } }
    private JSONObject buildPayload(ZenModel m, String prompt, String img) throws JSONException {
        JSONObject p = new JSONObject(); p.put("model", "opencode/" + m.modelId);
        if (m.endpoint.contains("/messages")) {
            JSONArray msgs = new JSONArray(); JSONObject msg = new JSONObject(); msg.put("role","user");
            JSONArray c = new JSONArray();
            if (img != null) { JSONObject i = new JSONObject(); i.put("type","image");
                i.put("source", new JSONObject().put("type","base64").put("media_type","image/jpeg")
                    .put("data", img.substring(img.indexOf(",")+1))); c.put(i); }
            JSONObject t = new JSONObject(); t.put("type","text"); t.put("text",prompt); c.put(t);
            msg.put("content",c); msgs.put(msg); p.put("messages",msgs); p.put("max_tokens",1024);
        } else if (m.endpoint.contains("/responses")) {
            JSONObject inp = new JSONObject(); inp.put("role","user"); JSONArray parts = new JSONArray();
            if (img != null) { JSONObject i = new JSONObject(); i.put("type","input_image");
                i.put("image_url",img); parts.put(i); }
            JSONObject t = new JSONObject(); t.put("type","input_text"); t.put("text",prompt); parts.put(t);
            inp.put("content",parts); p.put("input", new JSONArray().put(inp));
        } else {
            JSONArray msgs = new JSONArray(); JSONObject msg = new JSONObject(); msg.put("role","user");
            JSONArray c = new JSONArray();
            if (img != null) { JSONObject i = new JSONObject(); i.put("type","image_url");
                i.put("image_url", new JSONObject().put("url",img)); c.put(i); }
            JSONObject t = new JSONObject(); t.put("type","text"); t.put("text",prompt); c.put(t);
            msg.put("content",c); msgs.put(msg); p.put("messages",msgs); p.put("max_tokens",1024);
            p.put("temperature",0.2); }
        return p; }
    private String extractText(String body) throws JSONException {
        JSONObject r = new JSONObject(body);
        if (r.has("choices")) { JSONArray ch = r.getJSONArray("choices");
            if (ch.length()>0) return ch.getJSONObject(0).getJSONObject("message").optString("content",""); }
        if (r.has("content")) { JSONArray c = r.getJSONArray("content"); StringBuilder s = new StringBuilder();
            for (int i=0;i<c.length();i++) { JSONObject pt = c.getJSONObject(i);
                if ("text".equals(pt.optString("type"))) s.append(pt.optString("text","")); } return s.toString(); }
        if (r.has("output_text")) return r.getString("output_text"); return body; }
    public String fetchBalance() { if (!hasKey()) return "no key";
        try { Request req = new Request.Builder().url(BASE+"/zen/v1/models")
            .addHeader("Authorization","Bearer "+apiKey).get().build();
            try (Response resp = http.newCall(req).execute()) { String body = resp.body()!=null?resp.body().string():"";
                if (!resp.isSuccessful()) return "err "+resp.code(); JSONObject o = new JSONObject(body);
                return o.has("balance") ? "Balance: $"+o.getDouble("balance") : "Balance: n/a"; } }
        catch (Exception e) { return "offline"; } } }
"@ | Set-Content "$root\app\src\main\java\com\example\zenandroid\ZenClient.java" -Encoding UTF8

# SessionStore.java
@"
package com.example.zenandroid;
import android.content.Context; import org.json.JSONObject;
import java.io.File; import java.io.FileWriter; import java.io.IOException;
import java.text.SimpleDateFormat; import java.util.Date; import java.util.Locale;
public class SessionStore {
    private final Context ctx; public SessionStore(Context ctx) { this.ctx = ctx; }
    public void save(String model, String prompt, String response) throws IOException {
        File dir = new File(ctx.getExternalFilesDir(null),"sessions"); if (!dir.exists()) dir.mkdirs();
        String ts = new SimpleDateFormat("yyyyMMdd_HHmmss",Locale.US).format(new Date());
        JSONObject o = new JSONObject(); o.put("timestamp",ts); o.put("model",model);
        o.put("prompt",prompt); o.put("response",response);
        try (FileWriter w = new FileWriter(new File(dir,"session_"+ts+".json"))) { w.write(o.toString(2)); } }
    public File[] listSessions() { File d = new File(ctx.getExternalFilesDir(null),"sessions");
        return d.exists() ? d.listFiles((d2,n)->n.endsWith(".json")) : new File[0]; } }
"@ | Set-Content "$root\app\src\main\java\com\example\zenandroid\SessionStore.java" -Encoding UTF8

# MainActivity.java
@"
package com.example.zenandroid;
import android.Manifest; import android.content.Intent; import android.content.pm.PackageManager;
import android.net.Uri; import android.os.Bundle; import android.provider.MediaStore;
import android.widget.*; import androidx.activity.result.*; import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat; import androidx.core.content.FileProvider;
import com.google.android.material.textfield.TextInputEditText;
import java.io.File; import java.text.SimpleDateFormat; import java.util.*; import java.util.concurrent.Executors;
public class MainActivity extends AppCompatActivity {
    private ZenClient client; private SessionStore store; private List<ZenModel> models;
    private Uri selectedImageUri, cameraUri;
    private TextInputEditText apiKeyInput, promptInput;
    private Spinner modelSpinner; private TextView priceLabel, responseText, balanceText;
    private ProgressBar progressBar; private Button sendBtn; private ImageView previewImage;
    private final ActivityResultLauncher<Intent> cam = registerForActivityResult(
        new ActivityResultContracts.StartActivityForResult(), r -> {
            if (r.getResultCode()==RESULT_OK && cameraUri!=null) { selectedImageUri=cameraUri; showPreview(); } });
    private final ActivityResultLauncher<Intent> gal = registerForActivityResult(
        new ActivityResultContracts.StartActivityForResult(), r -> {
            if (r.getResultCode()==RESULT_OK && r.getData()!=null) { selectedImageUri=r.getData().getData(); showPreview(); } });
    private final ActivityResultLauncher<String> camP = registerForActivityResult(
        new ActivityResultContracts.RequestPermission(), g -> { if (g) launchCam(); });
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b); setContentView(R.layout.activity_main);
        client=new ZenClient(); store=new SessionStore(this); models=ZenModel.all();
        apiKeyInput=findViewById(R.id.apiKeyInput); promptInput=findViewById(R.id.promptInput);
        modelSpinner=findViewById(R.id.modelSpinner); priceLabel=findViewById(R.id.priceLabel);
        responseText=findViewById(R.id.responseText); balanceText=findViewById(R.id.balanceText);
        progressBar=findViewById(R.id.progressBar); sendBtn=findViewById(R.id.sendBtn);
        previewImage=findViewById(R.id.previewImage);
        String k=getSharedPreferences("zen_prefs",MODE_PRIVATE).getString("api_key","");
        if(!k.isEmpty()){apiKeyInput.setText(k);client.setApiKey(k);refreshBal();}
        ArrayAdapter<ZenModel> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_item,models);
        a.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        modelSpinner.setAdapter(a);
        modelSpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onItemSelected(android.widget.AdapterView<?> p,android.view.View v,int pos,long id){
                priceLabel.setText(models.get(pos).displayName+" "+models.get(pos).priceLabel());}
            public void onNothingSelected(android.widget.AdapterView<?> p){}});
        findViewById(R.id.saveKeyBtn).setOnClickListener(v->{String k2=apiKeyInput.getText().toString().trim();
            client.setApiKey(k2);getSharedPreferences("zen_prefs",MODE_PRIVATE).edit().putString("api_key",k2).apply();
            Toast.makeText(this,"Key saved",Toast.LENGTH_SHORT).show();refreshBal();});
        findViewById(R.id.cameraBtn).setOnClickListener(v->{if(ContextCompat.checkSelfPermission(this,
            Manifest.permission.CAMERA)==PackageManager.PERMISSION_GRANTED) launchCam(); else camP.launch(Manifest.permission.CAMERA);});
        findViewById(R.id.galleryBtn).setOnClickListener(v->{gal.launch(new Intent(Intent.ACTION_PICK,
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI));});
        sendBtn.setOnClickListener(v->send());
        findViewById(R.id.saveSessionBtn).setOnClickListener(v->saveSess()); }
    private void launchCam(){File d=new File(getExternalFilesDir(null),"captured");d.mkdirs();
        String ts=new SimpleDateFormat("yyyyMMdd_HHmmss",Locale.US).format(new Date());
        cameraUri=FileProvider.getUriForFile(this,getPackageName()+".fileprovider",new File(d,"IMG_"+ts+".jpg"));
        Intent i=new Intent(MediaStore.ACTION_IMAGE_CAPTURE);i.putExtra(MediaStore.EXTRA_OUTPUT,cameraUri);cam.launch(i);}
    private void showPreview(){if(selectedImageUri!=null){previewImage.setImageURI(selectedImageUri);previewImage.setVisibility(android.view.View.VISIBLE);}}
    private void send(){ZenModel m=(ZenModel)modelSpinner.getSelectedItem();
        String p=promptInput.getText().toString().trim();
        if(!client.hasKey()){Toast.makeText(this,"Save your API key first",Toast.LENGTH_LONG).show();return;}
        if(p.isEmpty()) p="What is in this image? Describe it in detail.";
        progressBar.setVisibility(android.view.View.VISIBLE);sendBtn.setEnabled(false);
        Uri img=selectedImageUri;String fp=p;
        Executors.newSingleThreadExecutor().execute(()->{try{
            String d=img!=null?ZenClient.encodeImage(this,img):null;
            String r=client.complete(m,fp,d);
            runOnUiThread(()->{responseText.setText(r);progressBar.setVisibility(android.view.View.GONE);sendBtn.setEnabled(true);});
        }catch(Exception e){runOnUiThread(()->{responseText.setText("Error: "+e.getMessage());progressBar.setVisibility(android.view.View.GONE);sendBtn.setEnabled(true);});}});}
    private void refreshBal(){if(!client.hasKey()){balanceText.setText("No key");return;}
        Executors.newSingleThreadExecutor().execute(()->{String b=client.fetchBalance();runOnUiThread(()->balanceText.setText(b));});}
    private void saveSess(){ZenModel m=(ZenModel)modelSpinner.getSelectedItem();String p=promptInput.getText().toString().trim();
        String r=responseText.getText().toString().trim();if(r.isEmpty()){Toast.makeText(this,"Nothing to save",Toast.LENGTH_SHORT).show();return;}
        try{store.save(m.displayName,p,r);Toast.makeText(this,"Saved ("+store.listSessions().length+" on device)",Toast.LENGTH_SHORT).show();}
        catch(Exception e){Toast.makeText(this,"Save failed: "+e.getMessage(),Toast.LENGTH_LONG).show();}}
}
"@ | Set-Content "$root\app\src\main\java\com\example\zenandroid\MainActivity.java" -Encoding UTF8

# build.bat
@"
@echo off
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
set GRADLE_VER=8.11.1
set GRADLE_ZIP=%TEMP%\gradle-%GRADLE_VER%-bin.zip
set GRADLE_DIR=%TEMP%\gradle-%GRADLE_VER%
set GRADLE_BIN=%GRADLE_DIR%\bin\gradle.bat
if not exist "%GRADLE_BIN%" (echo Downloading Gradle... && curl -L -o "%GRADLE_ZIP%" "https://services.gradle.org/distributions/gradle-%GRADLE_VER%-bin.zip" && powershell -Command "Expand-Archive -Path '%GRADLE_ZIP%' -DestinationPath '%TEMP%' -Force")
if not exist "gradlew.bat" (echo Wrapper... && "%GRADLE_BIN%" wrapper --gradle-version %GRADLE_VER%)
call gradlew.bat assembleDebug
if %ERRORLEVEL% EQU 0 (echo BUILD OK - app\build\outputs\apk\debug\app-debug.apk && "%ANDROID_HOME%\platform-tools\adb.exe" install app\build\outputs\apk\debug\app-debug.apk) else (echo BUILD FAILED)
pause
"@ | Set-Content "$root\build.bat" -Encoding UTF8

Write-Host ""
Write-Host "========================================"
Write-Host "  ALL FILES CREATED at ZenAndroidApp/"
Write-Host "========================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open ZenAndroidApp folder in Android Studio"
Write-Host "  2. OR run: cd ZenAndroidApp; .\build.bat"
