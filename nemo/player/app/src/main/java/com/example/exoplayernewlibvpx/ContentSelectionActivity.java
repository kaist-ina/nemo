package com.example.exoplayernewlibvpx;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class ContentSelectionActivity extends AppCompatActivity {

    Spinner contentSpinner;
    Spinner indexSpinner;
    Spinner qualitySpinner;
    Spinner resolutionSpinner;
    Spinner modeSpinner;
    Spinner loopbackSpinner;
    Spinner algorithmSpinner;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_content_selection);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_HIDE_NAVIGATION);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        requestPermissions();

        ArrayAdapter<CharSequence> contentAdapter = ArrayAdapter.createFromResource(this, R.array.content, android.R.layout.simple_spinner_item);
        contentAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        contentSpinner = findViewById(R.id.select_content);
        contentSpinner.setAdapter(contentAdapter);

        ArrayAdapter<CharSequence> indexAdapter = ArrayAdapter.createFromResource(this, R.array.index, android.R.layout.simple_spinner_item);
        indexAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        indexSpinner = findViewById(R.id.select_index);
        indexSpinner.setAdapter(indexAdapter);

        ArrayAdapter<CharSequence> qualityAdapter = ArrayAdapter.createFromResource(this, R.array.quality, android.R.layout.simple_spinner_item);
        qualityAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        qualitySpinner = findViewById(R.id.select_quality);
        qualitySpinner.setAdapter(qualityAdapter);

        ArrayAdapter<CharSequence> resolutionAdapter = ArrayAdapter.createFromResource(this, R.array.resolution, android.R.layout.simple_spinner_item);
        resolutionAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        resolutionSpinner = findViewById(R.id.select_resolution);
        resolutionSpinner.setAdapter(resolutionAdapter);

        ArrayAdapter<CharSequence> modeAdapter = ArrayAdapter.createFromResource(this, R.array.mode, android.R.layout.simple_spinner_item);
        modeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        modeSpinner = findViewById(R.id.select_mode);
        modeSpinner.setAdapter(modeAdapter);

        ArrayAdapter<CharSequence> loopbackAdapter = ArrayAdapter.createFromResource(this, R.array.loopback, android.R.layout.simple_spinner_item);
        loopbackAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        loopbackSpinner = findViewById(R.id.select_loopback);
        loopbackSpinner.setAdapter(loopbackAdapter);

        ArrayAdapter<CharSequence> alogrihtmAdapter = ArrayAdapter.createFromResource(this, R.array.algorithm, android.R.layout.simple_spinner_item);
        alogrihtmAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        algorithmSpinner = findViewById(R.id.select_algorithm);
        algorithmSpinner.setAdapter(alogrihtmAdapter);

        findViewById(R.id.start).setOnClickListener((view)->{
                Intent intent = new Intent(ContentSelectionActivity.this, PlayerActivity.class);
                intent.putExtra("content", contentSpinner.getSelectedItem().toString());
                intent.putExtra("index", indexSpinner.getSelectedItem().toString());
                intent.putExtra("quality", qualitySpinner.getSelectedItem().toString());
                intent.putExtra("resolution", resolutionSpinner.getSelectedItem().toString());
                intent.putExtra("mode",modeSpinner.getSelectedItem().toString());
                intent.putExtra("loopback",loopbackSpinner.getSelectedItem().toString());
                intent.putExtra("algorithm", algorithmSpinner.getSelectedItem().toString());
                startActivity(intent);
            }
        );
    }

    private void requestPermissions(){
        if(ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)!= PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(this,new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},0);
        }
    }
}
