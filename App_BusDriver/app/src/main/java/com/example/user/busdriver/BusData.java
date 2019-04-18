package com.example.user.busdriver;

import static java.lang.System.currentTimeMillis;

/**
 * Created by user on 2017/7/21.
 */

public class BusData {
    private String carId;
    private int arriving;
    private long updating;

    public BusData(){
        carId = "None";
        update("-1");
    }

    public BusData(String _Id, String _arriving){
        carId = _Id;
        update(_arriving);
    }

    public void update(String _arriving){
        arriving = Integer.parseInt(_arriving);
        updating = currentTimeMillis ();
    }

    public String getCarId(){
        return carId;
    }

    public int getArriving(){
        return arriving;
    }

    public boolean isOverTime(){
        return currentTimeMillis() - updating > 120*1000;
    }
}
