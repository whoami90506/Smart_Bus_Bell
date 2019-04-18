package com.example.user.busdriver;

import android.app.Service;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.media.MediaPlayer;
import android.os.AsyncTask;
import android.os.HandlerThread;
import android.os.Message;
import android.os.Vibrator;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.NotificationCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.widget.AbsListView;
import android.widget.ListView;
import android.widget.TabHost;
import android.widget.TextView;
import android.widget.Toast;
import android.os.Handler;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.logging.LogRecord;

import static java.lang.System.currentTimeMillis;

public class LineListActivity extends AppCompatActivity {

    public final String MainUrl = "http://192.168.137.1:5000/";
    String BusNum;
    String CarNum;
    String routeId;
    String departure;
    String destination;
    JSONObject root;
    JSONArray path;
    ArrayList<StopData> Stops;
    ArrayList<BusData> Buses;
    ArrayList<ListData> ListAry;
    boolean carIdLocate;
    boolean ClickBell;

    Handler mHandler;
    Handler mResetHandler;
    Handler mUIHandler = new Handler(){
        public void handleMessage(Message mes){

            ClickBell = true;
            AlertDialog.Builder builder= new AlertDialog.Builder(LineListActivity.this);
            builder.setTitle(alarmStopName+"  上車鈴").setMessage("在「"+alarmStopName+"」停車\n");
            builder.setPositiveButton("知道了", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int id) {
                    // User clicked OK button

                }
            });

            builder.show();
        }
    };
    HandlerThread mThread;
    HandlerThread mResetThread;
    final int mInterval = 5*1000;
    int ListTop = 0;
    long KeyBack = 0;


    String resetStop;
    String alarmStopName;
    static Drawable pic[] = new Drawable[4];

    final Runnable update = new Runnable() {
        @Override
        public void run() {
            Log.v("ListAct Update", "Inside run");
            try {
                String s = QueryUtils.makeHTTPRequest(MainUrl + "seebell/" + BusNum);
                root = new JSONObject(s);
                path = root.getJSONArray("path");
                Update();
                Log.v("ListAct Update", "Thread run");
            } catch (IOException | JSONException e) {
                Log.v("ListAct Update", e.toString());
                e.printStackTrace();
            }

            mUIHandler.post(UIUpdate);
            mHandler.postDelayed(update, mInterval);
        }
    };

    final Runnable UIUpdate = new Runnable() {
        @Override
        public void run() {
            updateTitle();

            ListView listView = (ListView)findViewById(R.id.list);
            ListAdapter adapter = new ListAdapter(LineListActivity.this, ListAry);
            listView.setAdapter(adapter);
            listView.setSelection(ListTop);
        }
    };

    final Runnable Reset = new Runnable() {
        @Override
        public void run() {
            try {
                String stop = resetStop;
                Log.v("ListAct Update", "Reset runnable " + stop);
                QueryUtils.makeHTTPRequest(MainUrl + "reset/" + routeId + "/" + stop);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    };

    final Runnable UIDialog = new Runnable() {
        @Override
        public void run() {
            mUIHandler.sendEmptyMessage(0);
        }
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_line_list);

        Intent intent = getIntent();
        BusNum = intent.getStringExtra("Number");
        CarNum = intent.getStringExtra("Car");
        ClickBell = false;

        pic[0] = getResources().getDrawable(R.drawable.ic_add_alert_black_24dp);
        pic[1] = getResources().getDrawable(R.drawable.disable);
        pic[2] = getResources().getDrawable(R.drawable.pregnantwoman);
        pic[3] = getResources().getDrawable(R.drawable.guidedog);
        try {
            root = new JSONObject(intent.getStringExtra("JSON"));
            routeId = root.getString("routeId");
            departure = root.getString("departureZh");
            destination = root.getString("destinationZh");
            path = root.getJSONArray("path");
            Stops = new ArrayList<StopData>();
            Buses = new ArrayList<BusData>();
            ListAry = new ArrayList<ListData>();
            StopInit();
            BusInit();
            ListAryInit();
            updateTitle();
        } catch (JSONException e) {
            e.printStackTrace();
            Toast.makeText(this, e.toString(),Toast.LENGTH_SHORT ).show();
        }

        ListView listView = (ListView)findViewById(R.id.list);
        ListAdapter adapter = new ListAdapter(this, ListAry);
        listView.setAdapter(adapter);
        listView .setOnScrollListener( new AbsListView.OnScrollListener() {

            @Override
            public void onScrollStateChanged(AbsListView absListView, int i) {

            }

            @Override
            public void onScroll(AbsListView view, int firstVisibleItem,
                                 int visibleItemCount, int totalItemCount) {

                ListTop = firstVisibleItem;
            }
        });


        mThread = new HandlerThread("update");
        mThread.start();
        mHandler = new Handler(mThread.getLooper());
        mResetThread = new HandlerThread("reset");
        mResetThread.start();
        mResetHandler = new Handler(mResetThread.getLooper());


        mHandler.postDelayed(update, mInterval);


    }

    private void Update() throws JSONException {
        for(int i = 0; i<path.length(); i++)
            Stops.get(i).update(path.getJSONObject(i));

        BusUpdate();

        for(int i = 0; i<ListAry.size(); i++)
            ListAry.get(i).update(Stops.get(i), Buses, CarNum);

    }

    private void StopInit() throws JSONException {
        for(int i = 0; i<path.length(); i++){
            StopData temp = new StopData(path.getJSONObject(i));
            Stops.add(temp);
        }
    }

    private void BusInit() throws JSONException{
        for(int i = 0; i<path.length(); i++){
            JSONObject temp = path.getJSONObject(i);

            String busId = temp.getString("busId");
            if(busId.equals("None"))continue;
            boolean found = false;
            for(int j = 0; j< Buses.size(); j++){
                if(busId.equals(Buses.get(j).getCarId())){
                    found = true;
                    break;
                }
            }
            if(found)continue;
            String nextStop =findNextStop(temp.getString("seqNo"), temp.getString("CarOnStop"));
            if(nextStop.equals("-1"))continue;

            Buses.add(new BusData(busId, nextStop));

            if(BusNum.equals(busId) && Stops.get(Integer.parseInt(nextStop)).isRing())showAlert(Integer.parseInt(nextStop));
        }

        carIdLocate = false;
        for(int i = 0; i<Buses.size(); i++)
            if(CarNum.equals(Buses.get(i).getCarId())){
                carIdLocate = true;
                break;
            }
        if(!carIdLocate)Toast.makeText(this, "警告：無法取得"+BusNum+"號 車牌 "+CarNum+" 的公車位置",Toast.LENGTH_SHORT ).show();
    }

    private void BusUpdate() throws JSONException {
        for(int i = 0; i<path.length(); i++){
            JSONObject temp = path.getJSONObject(i);

            String busId = temp.getString("busId");
            if(busId.equals("None"))continue;

            String nextStop = findNextStop(temp.getString("seqNo"), temp.getString("CarOnStop"));
            if(nextStop.equals("-1"))continue;

            int j;
            for(j = 0; j< Buses.size(); j++){
                if(busId.equals(Buses.get(j).getCarId()))break;
                //Log.v("ListAct BusUp", busId + " " + Buses.get(j).getCarId());
            }
            if(CarNum.equals(busId)){
                Log.v("ListAct Update", "BusUp find own car");
                if(j < Buses.size()) {

                    if(Buses.get(j).getArriving() < Integer.parseInt(nextStop)) ListTop = Integer.parseInt(nextStop) -1;

                    for (int k = Buses.get(j).getArriving(); k < Integer.parseInt(nextStop); k++) {
                        Log.v("ListAct Update", "Stop Change");
                        ClickBell = false;
                        if (Stops.get(k).isRing()) {
                            Log.v("ListAct Update", "reset the bell");
                            resetStop = Stops.get(k).getId();
                            Stops.get(k).resetBell();
                            mResetHandler.post(Reset);
                            try {
                                TimeUnit.MILLISECONDS.sleep(200);
                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            }
                        }
                    }
                }else ListTop = Integer.parseInt(nextStop) -1;

                if(Stops.get(Integer.parseInt(nextStop)).isRing() && !ClickBell)showAlert(Integer.parseInt(nextStop));

            }

            if(j < Buses.size())Buses.get(j).update(nextStop);
            else  Buses.add(new BusData(busId, nextStop));
        }

        for(int i = 0; i< Buses.size(); i++){
            if(Buses.get(i).isOverTime()){
                Buses.remove(i);
                i--;
            }
        }

        carIdLocate = false;
        for(int i = 0; i<Buses.size(); i++)
            if(CarNum.equals(Buses.get(i).getCarId())){
                carIdLocate = true;
                break;
            }

            if(!carIdLocate)ClickBell = false;
    }

    private void ListAryInit(){
        for(int i = 0; i<Stops.size(); i++)
            ListAry.add(new ListData(Stops.get(i), Buses, CarNum));
    }

    private void updateTitle(){
        BusData mine = findBus(CarNum);
        if(mine.getArriving() != -1)setTitle(BusNum + " (" + CarNum + ")   " + Stops.get(mine.getArriving()).getName());
        else setTitle(BusNum + "(" + CarNum + ")  無位置資訊");
    }

    private void showAlert(int idx){
        Log.v("ListAct Update", "showAlert");

        alarmStopName = Stops.get(idx).getName();
        mUIHandler.post(UIDialog);
        Vibrator myVibrator = (Vibrator) getApplication().getSystemService(Service.VIBRATOR_SERVICE);
        myVibrator.vibrate(3000);

        MediaPlayer mp = MediaPlayer.create(getApplicationContext(), R.raw.clock_ring);
        mp.start();

    }

    private BusData findBus(String BusId){
        for(int i = 0; i<Buses.size(); i++){
            if(BusId.equals(Buses.get(i).getCarId()))return Buses.get(i);
        }

        return new BusData();
    }

    private String findNextStop(String seqNo, String CarOnStop) throws JSONException {
        if(CarOnStop.equals("1"))return seqNo;

        if(seqNo.equals(Integer.toString(path.length()-1)))return "-1";

        int i = Integer.parseInt(seqNo);
        if(!path.getJSONObject(i).getString("goBack").equals(path.getJSONObject(i+1).getString("goBack"))) return "-1";

        return Integer.toString(i+1);

    }

    @Override
    protected void onPause() {
        // TODO Auto-generated method stub
        super.onPause();
        if (mHandler != null) {
            mHandler.removeCallbacks(update);
        }
    }

    @Override
    protected  void onRestart(){
        super.onRestart();
        if (mHandler != null) {
            mHandler.post(update);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();

        if (mHandler != null) mHandler.removeCallbacks(update);
        if (mThread != null) mThread.quit();

    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // TODO Auto-generated method stub

        if (keyCode == KeyEvent.KEYCODE_BACK) { // 攔截返回鍵
            if(currentTimeMillis() - KeyBack >3000){
                Toast.makeText(this, "再按一次返回以離開", Toast.LENGTH_SHORT).show();
                KeyBack = currentTimeMillis();
            }else finish();
        }
        return true;
    }
}


