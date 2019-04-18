package com.example.user.busdriver;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * Created by user on 2017/7/21.
 */

public class StopData {
    private String name;
    private String StopId;
    private  String StopLocationId;
    private int seqNo;
    private boolean  bell[] = new boolean[4];
    private boolean goBack;
    private boolean CarOnStop;

    public StopData(JSONObject json) throws JSONException {
        name = json.getString("nameZh");
        StopId = json.getString("Id");
        StopLocationId = json.getString("stopLocationId");
        seqNo = Integer.parseInt(json.getString("seqNo"));
        setBell(json);
        goBack = !json.getString("goBack").equals("0");
        setCarOnStop(json.getString("CarOnStop"));
    }

    public String getId(){return StopLocationId; }

    public String getName(){
        return name;
    }

    public boolean getGoBack(){
        return goBack;
    }

    public int getSeqNo(){
        return  seqNo;
    }

    public boolean isRing1(){
        return bell[0];
    }

    public boolean isRing2(){
        return bell[1];
    }

    public boolean isRing3(){
        return bell[2];
    }

    public boolean isRing4(){
        return bell[3];
    }

    public boolean isRing(){
        return bell[0] || bell[1] || bell[2] || bell[3];
    }

    public void update(JSONObject json) throws JSONException {
        setBell(json);
        setCarOnStop(json.getString("CarOnStop"));
    }

    private void setBell(JSONObject json) throws JSONException {

        bell[0] = !json.getString("bell1").equals("0");
        bell[1] = !json.getString("bell2").equals("0");
        bell[2] = !json.getString("bell3").equals("0");
        bell[3] = !json.getString("bell4").equals("0");
    }

    private void setCarOnStop(String s){
        CarOnStop = !s.equals("0");
    }

    public void resetBell(){
        bell[0] = false;
        bell[1] = false;
        bell[2] = false;
        bell[3] = false;
    }


}
