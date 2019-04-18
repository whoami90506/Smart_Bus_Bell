package com.example.user.busdriver;

import android.graphics.drawable.Drawable;

import java.util.ArrayList;

/**
 * Created by user on 2017/7/21.
 */

public class ListData {
    private boolean goback;
    private int seqNo;
    private String bus;
    private String StopName;
    private boolean bell[] = new boolean[4];
    private boolean here;

    public ListData(StopData s, ArrayList<BusData> BusAry, String myBus){
        goback = s.getGoBack();
        StopName = s.getName();
        seqNo = s.getSeqNo();
        update(s, BusAry, myBus);

    }

    public boolean isHere(){
        return here;
    }

    public boolean isGoback(){
        return goback;
    }

    public String getBus(){
        return bus;
    }

    public String getStopName(){
        return StopName;
    }

    public boolean isRing(){
        return bell[0] || bell[1] || bell[2] || bell[3];
    }

    public boolean isRing1(){return bell[0];}
    public boolean isRing2(){return bell[1];}
    public boolean isRing3(){return bell[2];}
    public boolean isRing4(){return bell[3];}

    public void update(StopData s, ArrayList<BusData> BusAry, String myBus){
        bus = "";
        for(int i = 0; i<BusAry.size(); i++)
            if(seqNo == BusAry.get(i).getArriving()){
                bus = BusAry.get(i).getCarId();
                break;
            }
        here = !myBus.equals("") && bus.equals(myBus);


        bell[0] = s.isRing1();
        bell[1] = s.isRing2();
        bell[2] = s.isRing3();
        bell[3] = s.isRing4();
    }
}
