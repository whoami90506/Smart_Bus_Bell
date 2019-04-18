package com.example.user.busdriver;

import android.content.Intent;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.concurrent.ExecutionException;

public class MainActivity extends AppCompatActivity {

    public final String MainUrl = "http://192.168.137.1:5000/";
    String num;
    String car;
    boolean isClick;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        isClick = false;
        setTitle("智慧上車鈴 - 公車司機端");
    }

    public void onLoginClick(View view) throws IOException, JSONException, ExecutionException, InterruptedException {
        if(isClick){
            Toast.makeText(this,"正在等待結果...", Toast.LENGTH_SHORT).show();
            return;
        }

        isClick = true;
        EditText text= (EditText)findViewById(R.id.bus);
        num = text.getText().toString();
        if(num.equals("小9"))num = "小9 (台灣好行-北投竹子湖)";
        Log.v("MainAct Bus", num);

        if(num.equals("")){
            Toast.makeText(this,"請輸入公車號碼", Toast.LENGTH_SHORT).show();
            isClick = false;
            return;
        }

        EditText textCar = (EditText)findViewById(R.id.car);
        car = textCar.getText().toString();

        Toast.makeText(this,"擷取資料中...", Toast.LENGTH_SHORT).show();
        CheckAsyncTask check = new CheckAsyncTask();
        check.execute(num);
        /*if(check.get().equals("Internet"))Toast.makeText(this,"Please check the internet.", Toast.LENGTH_SHORT).show();
        else if(check.get().equals("BusNumber"))Toast.makeText(this,"Please enter the correct bus number.", Toast.LENGTH_SHORT).show();
        else{

            Intent intent = new Intent(this, LineListActivity.class);
            intent.putExtra("Number", num);
            intent.putExtra("Car", car);
            intent.putExtra("JSON", check.get());
            startActivity(intent);

        }*/


    }

    private class CheckAsyncTask extends AsyncTask<String, Boolean, String>{

        @Override
        protected String doInBackground(String... num){
            Log.v("CheckAsyncTask BusNum", num[0]);
            String response = null;
            try {
                response = QueryUtils.makeHTTPRequest(MainUrl + "seebell/" + num[0]);
            } catch (IOException e) {
                e.printStackTrace();
                return "Internet";
            }
            Log.v("CheckAsyncTask JSON", response);

            if(response.equals(""))return "Internet";

            try {
                JSONObject root = new JSONObject(response);
                root.getString("number");
                return response;
            } catch (JSONException e) {
                e.printStackTrace();
                Log.v("MainA ATask 72 ERROR", response);
                return "BusNumber";
            }

        }

        @Override
        protected void onPostExecute(String ans) {
            super.onPostExecute(ans);
            if(ans.equals("Internet"))Toast.makeText(MainActivity.this,"網路不穩，請稍後嘗試", Toast.LENGTH_SHORT).show();
            else if(ans.equals("BusNumber"))Toast.makeText(MainActivity.this,"請輸入正確的公車號碼", Toast.LENGTH_SHORT).show();
            else{

                Intent intent = new Intent(MainActivity.this, LineListActivity.class);
                intent.putExtra("Number", num);
                intent.putExtra("Car", car);
                intent.putExtra("JSON", ans);
                startActivity(intent);

            }
            isClick = false;
        }

    }

}
