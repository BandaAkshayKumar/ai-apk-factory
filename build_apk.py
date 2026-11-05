import os, sys, json, glob, shutil, subprocess, urllib.request

prompt = os.environ.get('USER_PROMPT', '')
app_name = os.environ.get('APP_NAME', 'AI App')
app_id = os.environ.get('APP_ID', 'app100')
pkg = f'com.ai.{app_id}'

sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
bt_dir = sorted(glob.glob(f'{sdk}/build-tools/*'))[-1]
android_jar = sorted(glob.glob(f'{sdk}/platforms/android-*/android.jar'))[-1]

os.makedirs(f'src/com/ai/{app_id}', exist_ok=True)
os.makedirs('assets', exist_ok=True)
os.makedirs('build/classes', exist_ok=True)

manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{pkg}" android:versionCode="1" android:versionName="1.0">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="28" />
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:label="{app_name}" android:usesCleartextTraffic="true" android:theme="@android:style/Theme.Material.Light.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true" android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
with open('AndroidManifest.xml', 'w', encoding='utf-8') as f:
    f.write(manifest)

def call_ai(sys_msg):
    for model_name in ['openai', 'mistral']:
        try:
            data = json.dumps({'messages':[{'role':'user','content':sys_msg}],'model':model_name}).encode('utf-8')
            req = urllib.request.Request('https://text.pollinations.ai/', data=data, headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=45) as r:
                txt = r.read().decode('utf-8').strip()
                if len(txt) > 100: return txt
        except Exception as e:
            print('AI error:', e)
    return ''

sys_java = (
    f'Write a COMPLETE single-file Android Java class MainActivity in package {pkg}. '
    f'Return ONLY valid Java code starting with package {pkg}; and ending with }}. '
    'Do NOT use markdown fences. Use ONLY standard android.* and java.* packages (Activity, LinearLayout, ScrollView, Button, EditText, TextView, PdfDocument, Bitmap, BitmapFactory, Canvas, Paint, Intent, Uri, Bundle, BufferedReader, InputStreamReader, InputStream, OutputStream, ArrayList, Toast, Color, Gravity, ParcelFileDescriptor, PdfRenderer). '
    'Build a clean modern UI programmatically in onCreate. Use Intent.ACTION_GET_CONTENT with EXTRA_ALLOW_MULTIPLE to pick multiple files (.pdf, .txt, .jpg, .png, .jpeg, .eml) or fetch online URLs, merge/render them into a single PDF using android.graphics.pdf.PdfDocument (use PdfRenderer to copy existing PDF pages, BitmapFactory for images, Canvas.drawText for txt/eml), and use Intent.ACTION_CREATE_DOCUMENT (type application/pdf) so the user can choose the exact save location in local storage! '
    'App idea: ' + prompt
)
code = call_ai(sys_java)
if '```' in code:
    code = '\n'.join([l for l in code.splitlines() if not l.strip().startswith('```')])
if 'package ' in code:
    code = code[code.index('package '):]

compiled = False
if code:
    with open(f'src/com/ai/{app_id}/MainActivity.java', 'w', encoding='utf-8') as f:
        f.write(code)
    res = subprocess.run(['javac', '-source', '1.8', '-target', '1.8', '-bootclasspath', android_jar, '-classpath', android_jar, '-d', 'build/classes', f'src/com/ai/{app_id}/MainActivity.java'])
    if res.returncode == 0:
        compiled = True
        print('Compiled AI Native Java successfully!')

if not compiled:
    print('Using Verified Self-Healing Native Java Implementation')
    shutil.rmtree('build/classes', ignore_errors=True)
    os.makedirs('build/classes', exist_ok=True)
    verified_java = f'''package {pkg};
import android.app.Activity;
import android.content.Intent;
import android.graphics.*;
import android.graphics.pdf.PdfDocument;
import android.graphics.pdf.PdfRenderer;
import android.net.Uri;
import android.os.*;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;

public class MainActivity extends Activity {{
    private ArrayList<Uri> selectedFiles = new ArrayList<Uri>();
    private ArrayList<String> onlineUrls = new ArrayList<String>();
    private TextView listStatus;
    private EditText urlInput;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(48, 64, 48, 48);
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("{app_name}");
        title.setTextSize(22);
        title.setTypeface(null, Typeface.BOLD);
        title.setPadding(0, 0, 0, 24);
        root.addView(title);

        Button pickBtn = new Button(this);
        pickBtn.setText("+ Select Local Files (.PDF, .JPG, .PNG, .TXT, .EML)");
        root.addView(pickBtn);

        urlInput = new EditText(this);
        urlInput.setHint("Or paste online file/text URL (https://...)");
        root.addView(urlInput);

        Button addUrlBtn = new Button(this);
        addUrlBtn.setText("+ Add Online URL to Queue");
        root.addView(addUrlBtn);

        listStatus = new TextView(this);
        listStatus.setText("Queue: 0 local files, 0 URLs selected.");
        listStatus.setPadding(8, 30, 8, 30);
        root.addView(listStatus);

        Button mergeBtn = new Button(this);
        mergeBtn.setText("MERGE ALL TO PDF & CHOOSE SAVE LOCATION");
        mergeBtn.setBackgroundColor(Color.parseColor("#1976D2"));
        mergeBtn.setTextColor(Color.WHITE);
        root.addView(mergeBtn);

        Button clearBtn = new Button(this);
        clearBtn.setText("Clear Queue");
        root.addView(clearBtn);

        setContentView(scroll);

        pickBtn.setOnClickListener(new View.OnClickListener() {{
            public void onClick(View v) {{
                Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("*/*");
                i.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                startActivityForResult(Intent.createChooser(i, "Select Files to Merge"), 101);
            }}
        }});

        addUrlBtn.setOnClickListener(new View.OnClickListener() {{
            public void onClick(View v) {{
                String u = urlInput.getText().toString().trim();
                if (!u.isEmpty()) {{
                    onlineUrls.add(u);
                    urlInput.setText("");
                    updateQueueText();
                }}
            }}
        }});

        clearBtn.setOnClickListener(new View.OnClickListener() {{
            public void onClick(View v) {{
                selectedFiles.clear();
                onlineUrls.clear();
                updateQueueText();
            }}
        }});

        mergeBtn.setOnClickListener(new View.OnClickListener() {{
            public void onClick(View v) {{
                if (selectedFiles.isEmpty() && onlineUrls.isEmpty()) {{
                    Toast.makeText(MainActivity.this, "Select files or add URLs first!", Toast.LENGTH_SHORT).show();
                    return;
                }}
                Intent saveIntent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                saveIntent.addCategory(Intent.CATEGORY_OPENABLE);
                saveIntent.setType("application/pdf");
                saveIntent.putExtra(Intent.EXTRA_TITLE, "Merged_Document.pdf");
                startActivityForResult(saveIntent, 102);
            }}
        }});
    }}

    private void updateQueueText() {{
        listStatus.setText("Queued: " + selectedFiles.size() + " local file(s), " + onlineUrls.size() + " online URL(s) ready to merge.");
    }}

    @Override
    protected void onActivityResult(int req, int res, Intent data) {{
        if (req == 101 && res == RESULT_OK && data != null) {{
            if (data.getClipData() != null) {{
                for (int i = 0; i < data.getClipData().getItemCount(); i++) {{
                    selectedFiles.add(data.getClipData().getItemAt(i).getUri());
                }}
            }} else if (data.getData() != null) {{
                selectedFiles.add(data.getData());
            }}
            updateQueueText();
        }} else if (req == 102 && res == RESULT_OK && data != null && data.getData() != null) {{
            final Uri outUri = data.getData();
            listStatus.setText("Merging files into PDF...");
            new Thread(new Runnable() {{
                public void run() {{
                    mergeAllToPdf(outUri);
                }}
            }}).start();
        }}
    }}

    private void mergeAllToPdf(Uri outUri) {{
        PdfDocument outPdf = new PdfDocument();
        int pageNum = 1;
        try {{
            for (Uri uri : selectedFiles) {{
                String mime = getContentResolver().getType(uri);
                if (mime == null) mime = "";
                if (mime.contains("pdf") || uri.toString().toLowerCase().endsWith(".pdf")) {{
                    ParcelFileDescriptor pfd = getContentResolver().openFileDescriptor(uri, "r");
                    if (pfd != null) {{
                        PdfRenderer renderer = new PdfRenderer(pfd);
                        for (int i = 0; i < renderer.getPageCount(); i++) {{
                            PdfRenderer.Page p = renderer.openPage(i);
                            Bitmap bmp = Bitmap.createBitmap(p.getWidth() * 2, p.getHeight() * 2, Bitmap.Config.ARGB_8888);
                            bmp.eraseColor(Color.WHITE);
                            p.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_PRINT);
                            p.close();
                            PdfDocument.PageInfo pi = new PdfDocument.PageInfo.Builder(595, 842, pageNum++).create();
                            PdfDocument.Page outPage = outPdf.startPage(pi);
                            Rect dst = new Rect(0, 0, 595, 842);
                            outPage.getCanvas().drawBitmap(bmp, null, dst, null);
                            outPdf.finishPage(outPage);
                            bmp.recycle();
                        }}
                        renderer.close();
                        pfd.close();
                    }}
                }} else if (mime.startsWith("image/") || uri.toString().toLowerCase().matches(".*\\.(jpg|jpeg|png|webp)$")) {{
                    InputStream is = getContentResolver().openInputStream(uri);
                    Bitmap bmp = BitmapFactory.decodeStream(is);
                    if (is != null) is.close();
                    if (bmp != null) {{
                        PdfDocument.PageInfo pi = new PdfDocument.PageInfo.Builder(595, 842, pageNum++).create();
                        PdfDocument.Page outPage = outPdf.startPage(pi);
                        Canvas canvas = outPage.getCanvas();
                        canvas.drawColor(Color.WHITE);
                        float scale = Math.min(555f / bmp.getWidth(), 802f / bmp.getHeight());
                        int w = (int)(bmp.getWidth() * scale);
                        int h = (int)(bmp.getHeight() * scale);
                        Rect dst = new Rect((595 - w)/2, (842 - h)/2, (595 + w)/2, (842 + h)/2);
                        canvas.drawBitmap(bmp, null, dst, null);
                        outPdf.finishPage(outPage);
                        bmp.recycle();
                    }}
                }} else {{
                    InputStream is = getContentResolver().openInputStream(uri);
                    drawTextStreamToPdf(outPdf, is, pageNum++);
                    if (is != null) is.close();
                }}
            }}
            for (String u : onlineUrls) {{
                HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
                InputStream is = c.getInputStream();
                if (u.toLowerCase().matches(".*\\.(jpg|jpeg|png)$")) {{
                    Bitmap bmp = BitmapFactory.decodeStream(is);
                    if (bmp != null) {{
                        PdfDocument.PageInfo pi = new PdfDocument.PageInfo.Builder(595, 842, pageNum++).create();
                        PdfDocument.Page outPage = outPdf.startPage(pi);
                        outPage.getCanvas().drawBitmap(bmp, null, new Rect(20, 20, 575, 822), null);
                        outPdf.finishPage(outPage);
                    }}
                }} else {{
                    drawTextStreamToPdf(outPdf, is, pageNum++);
                }}
                is.close();
            }}
            OutputStream os = getContentResolver().openOutputStream(outUri);
            outPdf.writeTo(os);
            os.flush();
            os.close();
            outPdf.close();
            runOnUiThread(new Runnable() {{
                public void run() {{
                    listStatus.setText("Success! Merged PDF saved to your selected location!");
                    Toast.makeText(MainActivity.this, "Merged PDF Saved Successfully!", Toast.LENGTH_LONG).show();
                }}
            }});
        }} catch (final Exception e) {{
            runOnUiThread(new Runnable() {{
                public void run() {{
                    listStatus.setText("Error merging: " + e.getMessage());
                }}
            }});
        }}
    }}

    private void drawTextStreamToPdf(PdfDocument pdf, InputStream is, int pageNum) throws Exception {{
        BufferedReader br = new BufferedReader(new InputStreamReader(is, "UTF-8"));
        PdfDocument.PageInfo pi = new PdfDocument.PageInfo.Builder(595, 842, pageNum).create();
        PdfDocument.Page page = pdf.startPage(pi);
        Canvas canvas = page.getCanvas();
        Paint paint = new Paint();
        paint.setColor(Color.BLACK);
        paint.setTextSize(11f);
        int y = 40;
        String line;
        while ((line = br.readLine()) != null) {{
            while (line.length() > 85) {{
                canvas.drawText(line.substring(0, 85), 30, y, paint);
                line = line.substring(85);
                y += 16;
                if (y > 800) break;
            }}
            if (y > 800) break;
            canvas.drawText(line, 30, y, paint);
            y += 16;
        }}
        pdf.finishPage(page);
    }}
}}'''
    with open(f'src/com/ai/{app_id}/MainActivity.java', 'w', encoding='utf-8') as f:
        f.write(verified_java)
    subprocess.run(['javac', '-source', '1.8', '-target', '1.8', '-bootclasspath', android_jar, '-classpath', android_jar, '-d', 'build/classes', f'src/com/ai/{app_id}/MainActivity.java'], check=True)

class_files = []
for root_dir, _, files in os.walk('build/classes'):
    for f in files:
        if f.endswith('.class'):
            class_files.append(os.path.join(root_dir, f))

subprocess.run([f'{bt_dir}/d8', '--lib', android_jar, '--output', 'build/'] + class_files, check=True)
subprocess.run([f'{bt_dir}/aapt2', 'link', '-o', 'build/unaligned.apk', '-I', android_jar, '--manifest', 'AndroidManifest.xml', '-A', 'assets'], check=True)
subprocess.run(['zip', '-j', 'build/unaligned.apk', 'build/classes.dex'], check=True)
subprocess.run([f'{bt_dir}/zipalign', '-f', '4', 'build/unaligned.apk', 'build/aligned.apk'], check=True)
if not os.path.exists('debug.keystore'):
    subprocess.run(['keytool', '-genkeypair', '-v', '-keystore', 'debug.keystore', '-storepass', 'android', '-alias', 'androiddebugkey', '-keypass', 'android', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-dname', 'CN=Android Debug,O=Android,C=US'], check=True)
subprocess.run([f'{bt_dir}/apksigner', 'sign', '--ks', 'debug.keystore', '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', f'{app_id}.apk', 'build/aligned.apk'], check=True)
print('APK BUILT AND SIGNED SUCCESSFULLY!')
